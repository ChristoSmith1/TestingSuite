"""
Methods for merging raw data sources
"""

from pathlib import Path
import time
import g_over_t
from g_over_t.test_info import TESTS_ROOT_PATH, TestInfo, march_info, april_info  # noqa: F401
from g_over_t.util import simple_log

simple_log.set_level("DEBUG")

def merge(test_info: TestInfo) -> None:
    """Merge the pointing data with the power data.
    
    Modifies `test_info.data` in place"""
    simple_log.info(f"Doing the merge for {test_info}")

    # LOAD RAW DATA
    pointing_data = test_info.get_pointing_data()
    simple_log.debug(f"Loaded pointing data. {len(pointing_data):,} data points")
    power_data = test_info.get_power_data()
    simple_log.debug(f"Loaded power_data. {len(power_data):,} data points")

    # DO THE INTERPOLATION/MERGE
    simple_log.info(f"Beginning data merge. Might take awhile, might not.")
    merge_start_time = time.monotonic()
    combined_data = g_over_t.combine_power_position(
        power_data=power_data,
        position_data=pointing_data
    )
    merge_finish_time = time.monotonic()
    merge_time = merge_finish_time - merge_start_time
    simple_log.info(f"Finished data merge in {merge_time:.3f} seconds. {len(combined_data):,} data points in combined.")

    # Filter the NANs
    before_nan_filter_len = len(combined_data)
    combined_data = g_over_t.filter_out_nan(combined_data)
    after_nan_filter_len = len(combined_data)
    simple_log.debug(f"Filtered out NANs. Before filtering, len={before_nan_filter_len:,}. After filtering, len={after_nan_filter_len:,}")
    
    # Convert to pd.DataFrame
    data = g_over_t.convert_to_dataframe(combined_data)

    simple_log.debug(f"Successfully converted to pd.DataFrame.")
    simple_log.debug(f"First data point:")
    simple_log.debug(data.iloc[0])
    simple_log.debug(f"Last data point:")
    simple_log.debug(data.iloc[-1])

    # Go ahead and add the elapsed column automatically
    if "elapsed" not in data.columns:
        simple_log.debug(f"Adding 'elapsed' column")
        data = g_over_t.add_elapsed_time_column(data)

    # Assign to test_info object
    simple_log.debug(f"Assigning `pd.DataFrame` to TestInfo instance {test_info}")
    test_info.data = data

    # Write that to the CSV
    test_info.write_data()

    # Save the parameters.json file.
    test_info.write_parameters()


def _select_path(path: str | None) -> Path:
    if path:
        return Path(path).expanduser().resolve()
    
    from g_over_t.util.choice import get_user_choice_single

    choices = list(TESTS_ROOT_PATH.rglob("parameters.json"))
    print(choices)

    choice = get_user_choice_single(
        choices=[x.relative_to(TESTS_ROOT_PATH) for x in choices],
        prompt_message=f"Choose one of the following parameters files to merge.",
    )
    return TESTS_ROOT_PATH / choice

def main():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "path",
        nargs="?",
        default=None,
        help="Path to test. Can be path to the folder or the 'parameters.json' file.",
    )
    parser.add_argument(
        "--log-level", "-L",
        default="DEBUG",
        choices=[
            "DEBUG",
            "INFO",
            "WARNING",
            "ERROR",
            "CRITICAL",
        ],
        help="The script",
    )
    args = parser.parse_args()

    simple_log.set_level(args.log_level)
    simple_log.debug(f"Parsed arguments: {args}")
    path = _select_path(args.path)
    test_info = TestInfo.load(path)
    
    merge(test_info)

    pass

if __name__ == "__main__":
    main()