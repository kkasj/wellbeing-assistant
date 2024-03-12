# API 

## Running the server

1. Navigate to the api folder
```console
cd api
```

2. Install requirements
```console
pip install -r requirements.txt
```

3. Run the following command
```console
uvicorn main:app
``````

or, if you do not have `uvicorn` in your PATH, you can run it as a Python module
```console
python -m uvicorn main:app
```

## Documentation
To see the documentation of the endpoints, run the server and go to: http://127.0.0.1:8000/docs


## Database scheme
![Db](./database.png)
