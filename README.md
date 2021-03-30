# flask-backend
Flask prototyping backend for the MyOpenPantry project. Powered by [flask-smorest](https://flask-smorest.readthedocs.io/en/latest/).

## Setting up the Environment

### Install Virtualenv
```bash
  sudo pip3 install virtualenv
```

### Create and Activate the Virtual Environment
```bash
  python3 -m venv venv
  . /venv/bin/activate
```

### Install Dependencies
```bash
 pip install -r requirements.txt
```

Note: The project currently uses sqlite as the database. This is subject to change, and will require more installation steps once done.

## Running Tests
```bash
 pytest tests
```

## Starting the Development Server
```bash
 echo $'FLASK_APP=myopenpantry\nFLASK_ENV=development' > .env
 flask run
```

### Credits
lafrench's [flask-smorest sqlalchemy example](https://github.com/lafrech/flask-smorest-sqlalchemy-example)