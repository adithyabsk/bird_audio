"""Build filter list"""
import json
from pathlib import Path
from typing import List

import click
import pandas as pd
import yaml
from click import BadParameter

FILE_PATH = Path(__file__).parent
PARAMS_PATH = FILE_PATH / "../../params.yaml"


def read_and_filter_df(
    metadata_file: Path,
    unique_birds: int,
    total_seconds: int,
    manual_filter_list: List[int],
    quality_levels: List[str],
) -> pd.DataFrame:
    """Read metadata csv into a dataframe and filter it using the kwargs.

    Args:
        metadata_file: The path to the metadata csv file
        unique_birds: The total number of unique birds on which to filter
        total_seconds: The maximum recording length in seconds to allow
        manual_filter_list: A list of ids to manually remove from the dataset
        quality_levels: A list of quality ratings (e.g. "A", "B", etc...)

    Returns:
        A filtered DataFrame with an additional `total_seconds` column

    """
    df = pd.read_csv(metadata_file)
    # Take the length column which is in the form MM:SS and convert it to duration in seconds
    df["total_seconds"] = pd.to_timedelta(
        df.length.str.split(":").apply(lambda row: f"{row[0]}m {row[1]}s")
    ).dt.total_seconds()
    # Get the set of birds to include in the filtered df and make sure that Identity unknowns are
    # removed
    birds = set(df.en.value_counts().iloc[:unique_birds].index.tolist()) - {
        "Identity unknown"
    }
    filtered_df = df[
        # Make sure that the bird name is in the top N birds
        df.en.isin(birds)
        # Make sure the recording length is less than M seconds
        & (df.total_seconds < total_seconds)
        # Manually remove specific ids for reasons specified in params.yaml
        & ~df.id.isin(manual_filter_list)
        # Make sure that file are not null (url for audio)
        & ~df.file.isnull()
        # Make sure that the quality is in specified list
        & df.q.isin(quality_levels)
    ]

    return filtered_df


@click.command()
@click.argument("metadata_file", type=click.Path(exists=True, dir_okay=False))
@click.argument("output_file", type=click.Path(dir_okay=False))
def main(metadata_file, output_file):
    """Generate the filtered ids JSON file.

    Uses the parameters from `params.yaml` and the metadata.csv file to build a JSON list of ids

    """
    metadata_file, output_file = Path(metadata_file), Path(output_file)
    if not output_file.parent.exists():
        raise BadParameter("output_filepath directory must exist.")

    # Load DVC Params file
    with open(PARAMS_PATH) as params_file:
        params_dict = yaml.safe_load(params_file)

    unique_birds = params_dict["build"]["filter"]["unique_birds"]
    total_seconds = params_dict["build"]["filter"]["total_seconds"]
    manual_filter_list = params_dict["build"]["filter"]["manual_removal"]
    quality_levels = params_dict["build"]["filter"]["quality_levels"]

    filtered_df = read_and_filter_df(
        metadata_file, unique_birds, total_seconds, manual_filter_list, quality_levels
    )

    with open(output_file, "w+") as json_file:
        json.dump(filtered_df.id.tolist(), json_file, indent=2)


if __name__ == "__main__":
    main()
