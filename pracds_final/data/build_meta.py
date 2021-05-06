"""Download data from Xeno Canto"""
import itertools
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from typing import Any, Dict, List

import click
import pandas as pd
import requests
import yaml
from click import BadParameter
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from tqdm import tqdm
from yarl import URL

JSON = Dict[str, Any]

BASE_URL = URL("https://www.xeno-canto.org/api/2")
FILE_PATH = Path(__file__).parent
PARAMS_PATH = FILE_PATH / "../../params.yaml"


def get_page_recording(song_url: URL) -> JSON:
    """Use requests to get an individual page of recordings from Xeno Canto.

    Args:
        song_url: The Xeno Canto page endpoint

    Returns:
        The JSON response of the request

    """
    session = requests.Session()
    retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
    session.mount("https://", HTTPAdapter(max_retries=retries))
    resp = session.get(str(song_url))
    if resp.status_code == 200:
        return resp.json().get("recordings", [])
    else:
        page = song_url.query.get("page")
        tqdm.write(f"Failed to get page: {page}")


def search_recordings(**query_params) -> List[JSON]:
    """Search for recordings using the Xeno Canto search API

    The keys in the return dictionaries are speified in the API docs

    https://www.xeno-canto.org/explore/api


    Args:
        **query_params: A dictionary with query and/or page as keys with values as specified in the
            API docs.

    Returns:
        A list of recording information (list of dictionaries)

    """
    url = (BASE_URL / "recordings").with_query(query_params)
    resp = requests.get(str(url))
    if resp.status_code == 200:
        resp_json = resp.json()
        num_pages = resp_json["numPages"]
        recordings = resp_json["recordings"]
        if num_pages > 1:
            page_urls = [url.update_query(page=p) for p in range(2, num_pages + 1)]
            with ProcessPoolExecutor(max_workers=10) as ppe:
                recordings.extend(
                    itertools.chain(
                        *tqdm(
                            ppe.map(get_page_recording, page_urls), total=num_pages - 1
                        )
                    )
                )
    else:
        raise Exception(f"Request failed with status code: {resp.status_code}")

    return recordings


def save_recordings_metadata(song_list: List[JSON], output_path: Path):
    """Convert a list of json records to a dataframe.

    Saves the dataframe as a csv to the the output_path

    Args:
        song_list: A list of json dictionaries
    """
    df = pd.DataFrame.from_records(song_list)
    df.to_csv(output_path, index=False)

    return df


@click.command()
@click.argument("output_file", type=click.Path(dir_okay=False))
def main(output_file):
    """Generate the audio meta data.

    Uses the parameters from `params.yaml` to build a csv of recordings

    """
    output_file = Path(output_file)
    if not output_file.parent.exists():
        raise BadParameter("output_filepath directory must exist.")

    # Load DVC Params file
    with open(PARAMS_PATH) as params_file:
        params_dict = yaml.safe_load(params_file)

    # Extract the Xeno Canto list of queries to filter initial data and build a kwarg dict
    query_list = params_dict["build"]["meta"]["queries"]
    qp = {"query": "+".join(query_list)}
    # Search for the recordings using the queries and save the data
    rs = search_recordings(**qp)
    save_recordings_metadata(rs, output_file)


if __name__ == "__main__":
    main()
