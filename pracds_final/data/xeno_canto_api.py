"""Download data from Xeno Canto"""
import itertools
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from tqdm import tqdm
from yarl import URL

BASE_URL = URL("https://www.xeno-canto.org/api/2")
RAW_DATA_PATH = Path(__file__).parent / "../../data/raw"
META_DATA_FILENAME = "metadata.csv"


def get_page_recording(song_url):
    session = requests.Session()
    retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
    session.mount("https://", HTTPAdapter(max_retries=retries))
    resp = session.get(str(song_url))
    if resp.status_code == 200:
        return resp.json().get("recordings", [])
    else:
        page = song_url.query.get("page")
        tqdm.write(f"Failed to get page: {page}")


def search_recordings(**query_params):
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


def download_sono(sono_list, path):
    pass


def download_audio(audio_list, path):
    pass


def save_recordings_metadata(songs_json, path, file_name):
    df = pd.DataFrame.from_records(songs_json)
    df.to_csv(path / file_name, index=False)


if __name__ == "__main__":
    qp = {
        "query": "+".join(
            [
                'cnt:"United States"',
            ]
        ),
    }
    rs = search_recordings(**qp)
    save_recordings_metadata(rs, RAW_DATA_PATH, META_DATA_FILENAME)
