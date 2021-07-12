##Excerise Task
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Code style: black](https://img.shields.io/badge/code%20style-Flake8-green)](https://github.com/PyCQA/flake8)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)

[![security: bandit](https://img.shields.io/badge/security-bandit-yellow.svg)](https://github.com/PyCQA/bandit)
[![security: bandit](https://img.shields.io/badge/security-safety-yellow)](https://github.com/pyupio/safety)


[![](App/tests/results/coverage.svg)]()

[comment]: <> (<br>coverage badge will appear after running tests :&#41;<br>)

[comment]: <> (P.S coverage 100%)
### About:
 - Time to do task: 10 days
 - Description in Technical_Challenge.pdf<br>
I've cut multiple corners to meet basic requirements in given time with good performance.<br>
   

## Table of content

- Technology stack
- Quality Assurance
- Architecture
- Prerequisites
- Running service
- Test
- Before commit
- What I would do if had more time

## Technology Stack

- Python 3.9
- FastAPI 0.63
- Redis 6
- Postgres
- Docker
- Docker-compose
- Locust performance tests (To be done)
- coverage.py + pytest (To be done)

## Quality Assurance

##### Swagger documentation:

- Create buy order: http://127.0.0.1:8001/docs
- Api cache proxy: http://127.0.0.1:8002/docs
- Db proxy: http://127.0.0.1:8010/docs
- Fetch buy orders: http://127.0.0.1:8020/docs
- Health check: http://127.0.0.1:8050/docs

##### Clean Code:

- Black, Flake8
- isort: import sorting
- Pre-commit: hooks for big files etc.

##### Security :

- bandit: any left credential or AWS key
- safety: any known package vulnerability

##### Tests (To be done):

- coverage.py
- pytest

##### Health checks

- independent service that collects alive calls from services
- one place logs from all services
- missing hardware health checks

## Architecture

1. Each service is called Service_* <br>

- Inside are 2 folders: code_folder and tests
- code_folder contains service code
- tests would contain unittests if done
- Main folder contains requirements.txt

2. Deployment folder is for all deployment related data <br>

- Unified parametrized dockerfile for all services<br>
- docker-compose file containing all config in env vars
- pg_admin readme on how to connect to web ui of postgres sql tools
- Unified entrypoint.sh for all containers allowing us to operate on abstraction

3. Common_utilities contains modules that could be prepared as pip packages and later imported by pip3 <br>
4. Database folder will be populated while running with database files to mimic state saving of normal database <br>
5. Main directory contains all static code analysis files<br>

All services was created with low coupling and high cohesion in mind<br>
That resulted in 6 python3 services and 3 utility ones<br>
Architecture available in archichecture_schema.drawio file<br>
Draw.io is free to use software for block schematics<br>

## Services based on docker-compose

##### 1. Postgres

database container used by db proxy<br>

###### Access to Postgres:

* `localhost:5432`
* **Username:** postgres (as a default)
* **Password:** changeme (as a default)
  <br><br>

##### 2. Pg_admin container: administration and development platform for PostgreSQL<br>

###### Access to PgAdmin:

* **URL:** `http://localhost:5050`
* **Username:** user@domain.com (as a default)
* **Password:** changeme (as a default)
* more info at /Deployment/PGADMIN_POSTGRES.md
  <br><br>

##### 3. api_redis

Redis server for api_cache_proxy service

###### Access to Redis:

* **URL:** `localhost:6379`
* **Username:** no username
* **Password:** no password
* **Cache_db_name:** 0
  <br><br>

##### 4. api_cache_proxy

Python3 proxy service to deal with Redis cache

###### Access to Service:

* **URL:** `http://localhost:8002`
* **Example usage:** `GET http://127.0.0.1:8002/record`
* **Example response:** `200 OK, {json_data}`
  <br><br>

##### 5. api_updater

Python3 loop service to update cache with new record BTC price

###### Access to Service:

* **URL:** `http://localhost:8003`
* **Loop interval:** 15s
* **Example usage:** cannot be used
* **Example response:** no response

##### 6. create_buy_order

Python3 create_buy_order service.

###### Access to Service:

* **URL:** `http://localhost:8001`
* **Example usage:** `POST http://127.0.0.1:8001/place_order/?currency=eur&amount=69`
* **Example response:** `201_CREATED, "Order was placed for EUR:69.00"`
  <br><br>

##### 7. health_check

Python3 health_check service. Endpoint getting all report log requests.

###### Access to Service:

* **URL:** `http://localhost:8050`
* **Example usage:** `POST http://127.0.0.1:8050/report body={level: str, service: str, status: int, data:str}`
* **Example response:** `200_OK`
  <br><br>

##### 8. db_proxy

Python3 database proxy service. Service manages request to get/add data requests to db.

###### Access to Service:

* **URL:** `http://localhost:8010`
* **Example usage:** `GET http://127.0.0.1:8010/get/?start=0&page_size=5`
* **Example response:** `200_OK, json={json_data}`
  <br><br>

##### 9. fetch_buy_orders

Python3 fetch buy orders service. Service manages request to get buy orders, adds pagination.

###### Access to Service:

* **URL:** `http://localhost:8020`
* **Example usage:** `GET http://127.0.0.1:8020/get_orders/?start=0&page_size=3`
* **Example response:** `200_OK, json={json_data}`
  <br><br>

## Prerequisites

Docker installed and running docker deamon

## Running the service

##### Docker start & build

being in main folder

```
$ docker-compose up --build && docker-compose rm -fsv
```

##### Docker down

```
$ docker-compose down
```

##### Accessing API

Create buy order is available at:`http://localhost:8001`<br>
Fetch buy orders is available at:`http://localhost:8020`<br>

Only create buy order and fetch orders are meant for end user.<br>
Example usage:

- Create multiple records
- Fetch data

#### Create_buy_order:

```
POST http://127.0.0.1:8001/place_order/?currency=eur&amount=69 
curl --location --request POST 'http://127.0.0.1:8001/place_order/?currency=eur&amount=69'
```

#### Create_buy_order:

```
POST http://127.0.0.1:8001/place_order/ 
JSON:{
    "currency": "USD",
    "amount": 600
    }
curl --location --request POST 'http://127.0.0.1:8001/place_order/' \
--header 'Content-Type: application/json' \
--data-raw '{
    "currency": "USD",
    "amount": 600
}''
```

#### Fetch_buy_orders:

```
POST GET http://127.0.0.1:8020/get_orders/?start=0&page_size=3 
curl http://127.0.0.1:8020/get_orders/?start=0&page_size=3 
```

#### Fetch_buy_orders:

```
GET http://127.0.0.1:8020/get_orders/?start=0&page_size=100 
curl http://127.0.0.1:8020/get_orders/?start=0&page_size=100 
```

## Test (To be done)

##### run coverage.py 100% coverage

Begin in main folder

```
$ docker-compose up --build tests && docker-compose rm -fsv
```

Open results html file in browser:<br>
Coverage results: ./[Service_*]/tests/results/htmlcov/index.html<br>
Pytest results: ./[Service_*]/tests/results/pytest_results.html<br>

#### Run locust performance tests

You can specity number of worker nodes replacing below 5

```
$ docker-compose up --scale worker=5 locust
```

#### Connect to Locust web UI

Type below adress in browser.<br>
Select number of users and spawn rate.<br>
Remember that after 60 requests normal api user is blocked.<br>

```
 http://127.0.0.1:8089
```

## Before commit

Steps to do before commit or your commit will not be accepted.<br>
In future I would do full CI/CD process verifying code quality.<br>

```
pre-commit run --all-files
```

Before you send the code to the server, please runt this tests

```
$ python -m black --check -l 120 --exclude=venv .
$ python -m flake8 .
$ python -m isort --check-only --diff .
$ bandit -r .
$ safety check --full-report
```

Part of errors you can fix running:

```
$ python -m black -l 120 --exclude=venv .
$ python -m isort .
```

## What I would do if had more time

- health-check for infrastructure
- https://sentry.io/welcome/ for API health-check
- Dockerfile vulnerabilities
- Caching for fetching orders
- More API services for BTC price
- If more services would use db connector then I would create unified abstraction
- A lot more ...
