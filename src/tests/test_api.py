import contextlib
import tempfile
import uuid
from pathlib import Path
from time import sleep

import pytest
from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)


def is_valid_uuid(val: str) -> bool:
    """
    Returns True if val is valid UUID, else False
    :param val: str
    :return: bool
    """
    try:
        uuid.UUID(str(val))
        return True
    except ValueError:
        return False


@pytest.fixture(name="task_id_manager", scope="class")
def task_id_manager_fixture():
    class TaskIdManager:
        def __init__(self):
            self.task_id: str = None

    return TaskIdManager()


class TestAPI:
    """
    Integrity tests of CSV files processing API
    """

    @pytest.fixture
    def teardown(self, task_id_manager):
        yield
        self.delete_test_csv(task_id_manager)

    def delete_test_csv(self, task_id_manager):
        """
        Deletes all files in tmp directory by mask test_task_id*.csv
        """
        print(f"/delete_test_csv/{task_id_manager.task_id}")
        for file in Path(tempfile.gettempdir()).glob(f"{task_id_manager.task_id}*.csv"):
            print(f"/FILE/{file.name}")
            with contextlib.suppress(FileNotFoundError):
                file.unlink()

    def test_post_file(self, task_id_manager):
        """
        Test that correct CSV file accepted successfully and valid task_id returned
        """
        test_filename = "tests/test_input.csv"

        with open(test_filename, "rb") as f:
            response = client.post(
                "/process_csv", files={"file": ("filename", f, "text/csv")}
            )

        assert response.status_code == 200
        resp_dict = response.json()
        task_id = resp_dict.get("task_id")
        assert task_id is not None
        assert is_valid_uuid(task_id) is True
        task_id_manager.task_id = task_id

    def test_read_result(self, teardown, task_id_manager):
        """
        Test that task results request returns task state
        """
        sleep(1)

        test_filename = "tests/test_output.csv"
        with open(test_filename, "r") as f:
            output = f.read()

        print(f"/result-output - {output}")
        response = client.get(f"/result/{task_id_manager.task_id}")
        assert response.status_code == 200
        assert response.text == output

    def test_post_invalid_file(self, task_id_manager):
        """
        Test that incorrect CSV file accepted successfully and valid task_id returned
        """
        test_filename = "tests/test_input_invalid.csv"

        with open(test_filename, "rb") as f:
            response = client.post(
                "/process_csv", files={"file": ("filename", f, "text/csv")}
            )

        assert response.status_code == 200
        resp_dict = response.json()
        task_id = resp_dict.get("task_id")
        assert task_id is not None
        assert is_valid_uuid(task_id) is True
        task_id_manager.task_id = task_id

    def test_read_invalid_result(self, teardown, task_id_manager):
        """
        Test that incorrect CSV task results request returns task state FAILURE
        """
        sleep(1)
        response = client.get(f"/result/{task_id_manager.task_id}")
        assert response.status_code == 200
        assert response.json() == {"state": "FAILURE", "message": "Unknown csv format!"}

    def test_post_no_file(self):
        """
        Test that post request without file returned status 400 and error message
        """
        response = client.post("/process_csv")

        assert response.status_code == 400
        assert response.json() == {"message": "No upload file sent"}
