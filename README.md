
# SteelEye Assessment




## Introduction
This repository contains the solution for
SteelEye full-stack developer - Orders filters and listing problem.


## File contents
* `main.py` : It has all the required endpoints of the application.
* `trades_data.json`: Contains the fake data list.
* `pydantic_models.py`: Contains the Pydantic model.

## Libraries Used
- fastapi: API framework
- uvicorn: ASGI web server
- pydantic: Data validation
- trade-data: Mock json data of the List[Trade]

## Approach
I have picked up the `asynchronous` approach to build this API as it can process the multiple request in parallel which may process the request in another thread if needed and then notify the main thread which results in no queue wait when there are multiple requests on the same endpoint.

For server I am using `uvicorn` which is recommended for the `FastAPI` framework.
