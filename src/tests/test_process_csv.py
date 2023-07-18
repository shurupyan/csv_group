import os
import shutil
import tempfile
from pathlib import Path

import pytest
from services.process_csv import read_csv

OUTPUT_FILENAME_MASK = os.path.join(tempfile.gettempdir(), "{}-output.csv")


class TestClassCSVProcess:
    """
    Tests of CSV files processing function
    """

    task_id = "test_task_id"

    def delete_test_csv(self):
        """
        Deletes all files in tmp directory by mask test_task_id*.csv
        """
        for file in Path(tempfile.gettempdir()).glob(f"{self.task_id}*.csv"):
            file.unlink()

    def setup_method(self, method):
        """setup any state tied to the execution of the given method in a
        class.  setup_method is invoked for every test method of a class.
        """
        self.delete_test_csv()

    def teardown_method(self, method):
        """teardown any state that was previously setup with a setup_method
        call.
        """
        self.delete_test_csv()

    def test_success(self):
        """
        Test that correct CSV file processed successfully and output file created
        """
        test_filename = "test_input.csv"
        input_filename = os.path.join(
            tempfile.gettempdir(), f"{self.task_id}-{test_filename}"
        )

        shutil.copy(f"tests/{test_filename}", input_filename)
        res = read_csv(input_filename, self.task_id)

        assert res == OUTPUT_FILENAME_MASK.format(self.task_id)
        assert os.path.isfile(res) is True
        assert os.path.isfile(input_filename) is False

    def test_fail_on_wrong_csv_struct(self):
        """
        Test that processing of CSV file with wrong headers raises Exception
        """
        test_filename = "test_input_wrong_header.csv"
        input_filename = os.path.join(
            tempfile.gettempdir(), f"{self.task_id}-{test_filename}"
        )

        shutil.copy(f"tests/{test_filename}", input_filename)
        with pytest.raises(Exception):
            read_csv(input_filename, self.task_id)

        assert os.path.isfile(OUTPUT_FILENAME_MASK.format(self.task_id)) is False
        assert os.path.isfile(input_filename) is True

    def test_fail_on_invalid_csv(self):
        """
        Test that processing of non-CSV file raises Exception
        """
        test_filename = "test_input_invalid.csv"
        input_filename = os.path.join(
            tempfile.gettempdir(), f"{self.task_id}-{test_filename}"
        )

        shutil.copy(f"tests/{test_filename}", input_filename)
        with pytest.raises(Exception):
            read_csv(input_filename, self.task_id)

        assert os.path.isfile(OUTPUT_FILENAME_MASK.format(self.task_id)) is False
        assert os.path.isfile(input_filename) is True

    def test_fail_on_file_not_exists(self):
        """
        Test that processing of not existing file raises FileNotFoundError
        """
        input_filename = "test_wrong_filename.csv"

        with pytest.raises(FileNotFoundError):
            read_csv(input_filename, self.task_id)
