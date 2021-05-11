"""Build song vs call list"""
import json
from pathlib import Path

import click
import pandas as pd
from click import BadParameter


def build_song_vs_call_df(metadata_file: Path, filter_ids_file: Path) -> pd.DataFrame:
    """Load both metadata and filter ids and build a dataframe for the song vs call question.

    Args:
        metadata_file: The path to the metadata csv file
        filter_ids_file: The path to the filter ids json file

    Returns:
        A filtered dataframe with only rows that have either song or call (not both) in the type \
            column
    """
    df = pd.read_csv(metadata_file)
    filtered_ids = pd.read_json(filter_ids_file).squeeze()
    filtered_df = df[df.id.isin(filtered_ids)]

    # build a list of filtered ids that have only either call or song (not both)
    split_col = filtered_df.type.str.replace(" ", "").str.split(",")
    call_rows = split_col.apply(lambda l: "call" in l and "song" not in l)
    song_rows = split_col.apply(lambda l: "call" not in l and "song" in l)
    song_vs_call_df = filtered_df[call_rows | song_rows]

    return song_vs_call_df


@click.command()
@click.argument("metadata_file", type=click.Path(exists=True, dir_okay=False))
@click.argument("filter_ids_file", type=click.Path(exists=True, dir_okay=False))
@click.argument("output_file", type=click.Path(dir_okay=False))
def main(metadata_file, filter_ids_file, output_file):
    """Generate the filtered ids JSON file.

    Uses the parameters from `params.yaml` and the metadata.csv file to build a JSON list of ids

    """
    metadata_file, filter_ids_file, output_file = (
        Path(metadata_file),
        Path(filter_ids_file),
        Path(output_file),
    )
    if not output_file.parent.exists():
        raise BadParameter("output_filepath directory must exist.")

    song_vs_call_df = build_song_vs_call_df(metadata_file, filter_ids_file)

    with open(output_file, "w+") as json_file:
        json.dump(song_vs_call_df.id.tolist(), json_file, indent=2)


if __name__ == "__main__":
    main()
