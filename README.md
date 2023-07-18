## About the prototype
A simple API of asynchronous file processing prototype takes a CSV file of the following format as its input

| Song       |    Date    | Number of Plays |
|------------|:----------:|----------------:|
| Umbrella   | 2020-01-02 |             200 | 
| Umbrella   | 2020-01-01 |             100 |
| In The End | 2020-01-01 |             500 |
| Umbrella   | 2020-01-01 |              50 |
| In The End | 2020-01-01 |            1000 |
| Umbrella   | 2020-01-02 |              50 |
| In The End | 2020-01-02 |             500 |

processes it and generates the output CSV file:

| Song       |    Date    |  Total Number of Plays for Date |
|------------|:----------:|--------------------------------:|
| Umbrella   | 2020-01-02 |                             250 | 
| Umbrella   | 2020-01-01 |                             150 |
| In The End | 2020-01-01 |                            1500 |
| In The End | 2020-01-02 |                             500 |

* Input CSV file: “Song”, “Date”, “Number of Plays”.
There will be many records for each song within each day. Input is not sorted.
* Output CSV file: “Song”, “Date, “Total Number of Plays for Date”

## Requirements

* [Docker](https://www.docker.com/) service installed and started
* [docker-compose](https://github.com/docker/compose) installed
* Internet access for docker images downloading from [Docker Hub](https://hub.docker.com)

Prototype consists of three docker containers:
* Backend - [uvicorn](https://www.uvicorn.org/) web server provides the HTTP API endpoints
* Worker - [Celery](https://docs.celeryq.dev/) worker executes the file processing tasks asynchronously
* [RabbitMQ](http://www.rabbitmq.com/) - queue manager as infrastructure for Celery

## How to run

* At first docker containers should be built by running next terminal command from the prototype directory (where is 
  the compose.yml file located):


    docker-compose build

It will take a couple of minutes to download docker images and build the containers.
* To start containers, execute next terminal command:


    docker-compose up -d
Prototype's HTTP API will be accessible on localhost by port 8000. If that port is used by some other software, 
please update compose.yml file by changing the line:
    
     "8000:8000"
with some other port number which is not in use (second port number in this line should stay 8000):

     "9999:8000"

* To run unit and integration tests, execute next terminal command:


    docker-compose exec -i backend bash -c "cd /app/src && python -m pytest"

* To stop containers, execute next terminal command:


    docker-compose down

## API endpoints
* POST /process_csv 

Start celery task of grouping input CSV file by song name and date.
    body: form-data CSV file
    returns: JSON with task_id of task processing the file

Example:

    curl --location '0.0.0.0:8000/process_csv' --form 'file=@"/home/user/example.csv"'
Output:

    {
        "task_id": "77e3e62c-1cf1-4d3b-8079-428de130e3cc"
    }

* GET /result/<task_id>

Get the celery task result by task id
    task_id: UUID identifier of the celery task
    returns: if task state is SUCCESS then return grouped output CSV file
            else return JSON with state of the task

Example:

    curl --location '0.0.0.0:8000/result/d91c750f-4b4b-4daf-8994-f0fe52e2df60'

Output (task not finished):

    {
        "state": "PENDING",
        "message": "None"
    }

Output (task finished):

    Song,Date,Total Number of Plays for Date
    Umbrella,2020-01-02,250
    Umbrella,2020-01-01,150
    In The End,2020-01-01,1500
    In The End,2020-01-02,500