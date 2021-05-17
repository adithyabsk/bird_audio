"""Process audio into array with high-pass filter"""
from pathlib import Path

import click
import librosa
import pandas as pd
from click import BadParameter
from scipy import signal
from tqdm import tqdm
from tsfresh import extract_features
from tsfresh.feature_extraction import EfficientFCParameters
from tsfresh.utilities.dataframe_functions import impute

FILE_PATH = Path(__file__).parent
PARAMS_PATH = FILE_PATH / "../../params.yaml"


def unpack_audio(recordings_path: Path, id, filter_order, cutoff_freq):
    """Load mp3 or wav into a floating point time series, then run a high-pass filter.

    Args:
        recordings_path: The path to the recordings dir
        id: The id for the audio recording to unpack
        filter_order: The order for the Butter filter
        cutoff_freq: The critical frequency for the Butter filter (below this is filtered out)

    Returns:
        A df of filtered time series data for the given id, with 'id', 'time', and 'val' columns
    """
    try:
        audio_path = FILE_PATH / ("data/raw/recordings/" + str(id) + ".mp3")
        # load mp3 as audio timeseries arr
        timeseries, sr = librosa.load(audio_path)
    except FileNotFoundError:
        audio_path = FILE_PATH / ("data/raw/recordings/" + str(id) + ".wav")
        timeseries, sr = librosa.load(audio_path)

    # high-pass filter on audio timeseries
    timeseries_filt = highpass_filter(timeseries, sr, filter_order, cutoff_freq)

    df = pd.DataFrame(timeseries_filt, columns=["val"])
    df.reset_index(inplace=True)
    df["id"] = id  # fill col with id
    df = df.reindex(columns=["id", "index", "val"])
    df.columns = ["id", "time", "val"]
    return df


def highpass_filter(audio, sr, order, freq):
    """Apply a Butterworth high-pass filter to get rid of low-freq noise.

    Args:
        audio: The time series audio data
        sr: The audio samplerate

    Returns:
        High-pass filtered time series data
    """
    return signal.lfilter(
        *signal.butter(order, freq, btype="highpass", fs=sr), audio
    )  # numerator and denominator


manual_fc_params = {
    "abs_energy": None,
    "fft_aggregated": [{"aggtype": "centroid"}, {"aggtype": "kurtosis"}],
    "root_mean_square": None,
    "spkt_welch_density": [{"coeff": 2}, {"coeff": 5}, {"coeff": 8}],
}

selected_fc_params = {
    "standard_deviation": None,
    "variance": None,
    "root_mean_square": None,
}


# select features to calculate
# features can be found here: https://tsfresh.readthedocs.io/en/latest/api/tsfresh.feature_extraction.html#tsfresh.feature_extraction.feature_calculators.fft_aggregated
def featurize_audio(id, fc_params):
    return extract_features(
        unpack_audio(id),
        column_id="id",
        column_sort="time",
        default_fc_parameters=fc_params,
        disable_progressbar=True,
        # we impute = remove all NaN features automatically
        impute_function=impute,
        # turn off parallelization
        n_jobs=0,
    )


# featurize dataset
# returns df of all combined
def featurize_set(ids, fc_params=None):
    if fc_params is None:
        fc_params = EfficientFCParameters()
    X_df = pd.DataFrame()
    for id in tqdm(ids):
        X_df = pd.concat([X_df, featurize_audio(id, fc_params)])
    return X_df


@click.command()
@click.argument("song_vs_call_file", type=click.Path(exists=True, dir_okay=False))
@click.argument("recordings_file", type=click.Path(exists=True, dir_okay=True))
@click.argument("output_file", type=click.Path(dir_okay=False))
def main(song_vs_call_file, recordings_file, output_file):
    """Generate the filtered audio time series JSON file.

    Uses the song_vs_call file to get relevant recording ids,
    recordings_file to get corresponding audio files,
    and parameters from `params.yaml` for high-pass filter.

    """
    # TODO (@merlerker): The params are unused
    # # Load DVC Params file
    # with open(PARAMS_PATH) as params_file:
    #     params_dict = yaml.safe_load(params_file)
    # filter_order = params_dict["proc"]["audio"]["filter_order"]
    # cutoff_freq = params_dict["proc"]["audio"]["cutoff_freq"]

    # Load svc file, recordings, and output
    song_vs_call_file, recordings_file, output_file = (
        Path(song_vs_call_file),
        Path(recordings_file),
        Path(output_file),
    )
    if not output_file.parent.exists():
        raise BadParameter("output_filepath directory must exist.")

    # Get ids of recordings we are using for song vs call task
    svc_ids = pd.read_json(song_vs_call_file).squeeze()

    # manual_fc_params
    # selected_fc_params
    # EfficientFCParameters()
    # ComprehensiveFCParameters()
    # MinimalFCParameters()
    X_df = featurize_set(svc_ids, manual_fc_params)
    X_df.to_json(output_file, indent=2, orient="columns")


if __name__ == "__main__":
    main()
