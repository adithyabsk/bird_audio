"""Download data from Xeno Canto"""
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from typing import List, Union

import click
import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from tqdm import tqdm
from yarl import URL

DownloadSetList = Union[URL, str, Path]


def download_audio_recording(download_info: List[DownloadSetList]):
    """Use requests to get the audio recording from Xeno Canto

    Saves the downloaded file to the output_path using the name of the file on the server.

    Args:
        download_info: A tuple with the audio_url, file_name, output_path as a single argument

    """
    # We use a tuple as the single argument because it works better with multiprocessing map
    audio_url, file_name, output_path = download_info
    session = requests.Session()
    retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
    session.mount("https://", HTTPAdapter(max_retries=retries))
    resp = session.get(str(audio_url))
    if resp.status_code == 200:
        with open(output_path / file_name, "wb+") as f:
            f.write(resp.content)
    else:
        tqdm.write(f"Failed to get: {audio_url}")


def parallel_download_recordings(download_set: List[DownloadSetList]):
    """Download recordings in a parallel manner

    Args:
        download_set: A list of tuples with the info needed to download each file.

    """
    with ProcessPoolExecutor(max_workers=10) as ppe:
        list(
            tqdm(
                ppe.map(download_audio_recording, download_set), total=len(download_set)
            )
        )


def build_download_set(
    metadata_file, filter_file, output_path
) -> List[DownloadSetList]:
    """Build the download set from filter and metadata files.

    Args:
        metadata_file: Path to the metadata csv file
        filter_file: Path to the filter json file
        output_path: The output path of all files

    Returns:
        A list of lists with the required info to download a file.

    """
    df = pd.read_csv(metadata_file)
    filter_ids = pd.read_json(filter_file).squeeze()
    filtered_df = df.loc[df.id.isin(filter_ids)].copy()
    # Add protocol to the audio url paths
    filtered_df.file = "https:" + filtered_df.file
    filtered_df["output_path"] = pd.Series([output_path] * len(filtered_df))
    download_set = filtered_df[["file", "file-name", "output_path"]].values.tolist()

    return download_set


@click.command()
@click.argument("metadata_file", type=click.Path(exists=True, dir_okay=False))
@click.argument("filter_file", type=click.Path(exists=True, dir_okay=False))
@click.argument("output_path", type=click.Path(dir_okay=True, file_okay=False))
def main(metadata_file, filter_file, output_path):
    """Generate the audio files.

    Uses the parameters from `params.yaml` to download recordings to the output_path

    """
    metadata_file, filter_file, output_path = map(
        Path, [metadata_file, filter_file, output_path]
    )
    # quirk of DVC, it deletes targets so we need to re-create the folder and re-add the .gitkeep
    output_path.mkdir(parents=True, exist_ok=True)
    (output_path / ".gitkeep").touch()
    download_set = build_download_set(metadata_file, filter_file, output_path)
    parallel_download_recordings(download_set)


if __name__ == "__main__":
    main()
