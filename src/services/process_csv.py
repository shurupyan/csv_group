import os
import tempfile

from dask import dataframe as dd

CSV_COLUMNS = ["Song", "Date", "Number of Plays"]
FILENAME_MASK = os.path.join(tempfile.gettempdir(), "{}-output.csv")


def read_csv(input_filename: str, task_id: str) -> str:
    """
    Reads input CSV file with columns "Song", "Date", "Number of Plays"
    groups it by "Song" and "Date" columns, summarizing number of plays
    into column "Total Number of Plays for Date". Saves result CSV file
    in temporary directory and returns its full name.
    :param input_filename: full filename to process
    :param task_id: ID of the celery task, UUID
    :return: full output filename
    """
    input_df = dd.read_csv(input_filename, blocksize=25e6)

    if list(input_df.columns) != CSV_COLUMNS:
        raise Exception("Unknown csv format!")

    output_df = input_df.groupby(["Song", "Date"]).aggregate({"Number of Plays": "sum"})
    output_df = output_df.rename(
        columns={"Number of Plays": "Total Number of Plays for Date"}
    )
    output_df.compute()

    path = FILENAME_MASK.format(task_id)
    output_filename = output_df.to_csv(path, single_file=True)[0]
    os.remove(input_filename)
    return output_filename
