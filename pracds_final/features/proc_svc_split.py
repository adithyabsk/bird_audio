"""Build song vs call train/test split"""
import json
from pathlib import Path

import click
import pandas as pd
import yaml
from click import BadParameter
from sklearn.model_selection import train_test_split

FILE_PATH = Path(__file__).parent
PARAMS_PATH = FILE_PATH / "../../params.yaml"


@click.command()
@click.argument("song_vs_call_file", type=click.Path(exists=True, dir_okay=False))
@click.argument("output_file", type=click.Path(dir_okay=False))
def main(song_vs_call_file, output_file):
    """Generate the filtered ids JSON file.

    Uses the parameters from `params.yaml` and the metadata.csv file to build a JSON list of ids

    """
    song_vs_call_file, output_file = Path(song_vs_call_file), Path(output_file)
    if not output_file.parent.exists():
        raise BadParameter("output_filepath directory must exist.")

    # Load DVC Params file
    with open(PARAMS_PATH) as params_file:
        params_dict = yaml.safe_load(params_file)

    random_seed = params_dict["random_seed"]

    song_vs_call_ids = pd.read_json(song_vs_call_file).squeeze()
    song_vs_call_ids_train, song_vs_call_ids_test = train_test_split(
        song_vs_call_ids, random_state=random_seed
    )

    with open(output_file, "w+") as json_file:
        json.dump(
            {
                "train_ids": song_vs_call_ids_train.tolist(),
                "test_ids": song_vs_call_ids_test.tolist(),
            },
            json_file,
            indent=2,
        )


if __name__ == "__main__":
    main()
