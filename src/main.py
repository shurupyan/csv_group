import os
import shutil
import tempfile
import uuid

from celery.result import AsyncResult
from fastapi import FastAPI, UploadFile
from starlette.responses import FileResponse, JSONResponse

from tasks import group_file, celery_app

app = FastAPI()

FILENAME_MASK = os.path.join(tempfile.gettempdir(), "{}-input.csv")


@app.post("/process_csv")
async def process_csv(file: UploadFile | None = None):
    """
    Start celery task of grouping input CSV file by song name and date.
    :param file: CSV file
    :return: JSON with task_id of task processing the file
    """
    if not file:
        return JSONResponse({"message": "No upload file sent"}, status_code=400)
    else:
        task_id = str(uuid.uuid4())
        path = FILENAME_MASK.format(task_id)
        with open(path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        result = group_file.apply_async((path, task_id), task_id=task_id)
        return {"task_id": result.id}


@app.get("/result/{task_id}")
async def say_hello(task_id: str):
    """
    Get the celery task result by task id
    :param task_id: identifier of the celery task
    :return: if task state is SUCCESS then return grouped output CSV file
            else return JSON with state of the task
    """
    res = AsyncResult(task_id, app=celery_app)
    if res.state == "SUCCESS":
        return FileResponse(res.result)
    return {
        "state": res.state,
        "message": str(res.result),
    }
