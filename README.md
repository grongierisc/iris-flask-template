# iris-flask-template

![Flask_logo](https://flask.palletsprojects.com/en/2.0.x/_images/flask-logo.png)

## Description

This is a template for a Flask application that can be deployed in IRIS as an native Web Application.

## Installation

1. Clone the repository
2. Create a virtual environment
3. Install the requirements
4. Run the docker-compose file

```bash
git clone
cd iris-flask-template
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
docker-compose up
```

## Usage

The base URL is `http://localhost:53795/flask/`.

### Endpoints

- `/iris` - Returns a JSON object with the top 10 classes present in the IRISAPP namespace.
- `/interop` - A ping endpoint to test the interoperability framework of IRIS.
- `/posts` - A simple CRUD endpoint for a Post object.
- `/comments` - A simple CRUD endpoint for a Comment object.

## How to develop from this template

See WSGI introduction article: [wsgi-introduction](https://community.intersystems.com/post/wsgi-support-introduction).

TL;DR : You can toggle the `DEBUG` flag in the Security portal to make changes to be reflected in the application as you develop.

## Code presentation

### `app.py`

This is the main file of the application. It contains the Flask application and the endpoints.

```python
from flask import Flask, jsonify, request
from models import Comment, Post, init_db

from grongier.pex import Director

import iris

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'iris+emb://IRISAPP'

db = init_db(app)
```

- `from flask import Flask, jsonify, request`: Import the Flask library.
- `from models import Comment, Post, init_db`: Import the models and the database initialization function.
- `from grongier.pex import Director`: Import the Director class to bind the flask app to the IRIS interoperability framework.
- `import iris`: Import the IRIS library.
- `app = Flask(__name__)`: Create a Flask application.
- `app.config['SQLALCHEMY_DATABASE_URI'] = 'iris+emb://IRISAPP'`: Set the database URI to the IRISAPP namespace.
  - The `iris+emb` URI scheme is used to connect to IRIS as an embedded connection (no need for a separate IRIS instance).
- `db = init_db(app)`: Initialize the database with the Flask application.

### `models.py`

This file contains the SQLAlchemy models for the application.

```python
from dataclasses import dataclass
from typing import List
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

@dataclass
class Comment(db.Model):
    id:int = db.Column(db.Integer, primary_key=True)
    content:str = db.Column(db.Text)
    post_id:int = db.Column(db.Integer, db.ForeignKey('post.id'))

@dataclass
class Post(db.Model):
    __allow_unmapped__ = True
    id:int = db.Column(db.Integer, primary_key=True)
    title:str = db.Column(db.String(100))
    content:str = db.Column(db.Text)
    comments:List[Comment] = db.relationship('Comment', backref='post')
```

Not much to say here, the models are defined as dataclasses and are subclasses of the `db.Model` class.

The use of the `__allow_unmapped__` attribute is necessary to allow the creation of the `Post` object without the `comments` attribute.

`dataclasses` are used to help with the serialization of the objects to JSON.

The `init_db` function initializes the database with the Flask application.

```python
def init_db(app):
    db.init_app(app)

    with app.app_context():
        db.drop_all()
        db.create_all()
        # Create fake data
        post1 = Post(title='Post The First', content='Content for the first post')
        ...
        db.session.add(post1)
        ...
        db.session.commit()
    return db
```

- `db.init_app(app)`: Initialize the database with the Flask application.
- `with app.app_context()`: Create a context for the application.
- `db.drop_all()`: Drop all the tables in the database.
- `db.create_all()`: Create all the tables in the database.
- Create fake data for the application.
- return the database object.


### `/iris` endpoint

```python
######################
# IRIS Query example #
######################

@app.route('/iris', methods=['GET'])
def iris_query():
    query = "SELECT top 10 * FROM %Dictionary.ClassDefinition"
    rs = iris.sql.exec(query)
    # Convert the result to a list of dictionaries
    result = []
    for row in rs:
        result.append(row)
    return jsonify(result)
```

This endpoint executes a query on the IRIS database and returns the top 10 classes present in the IRISAPP namespace.

### `/interop` endpoint

```python
########################
# IRIS interop example #
########################
bs = Director.create_python_business_service('BS')

@app.route('/interop', methods=['GET', 'POST', 'PUT', 'DELETE'])
def interop():
    
    rsp = bs.on_process_input(request)

    return jsonify(rsp)
```

This endpoint is used to test the interoperability framework of IRIS. It creates a Business Service object and binds it to the Flask application.

NB : The `bs` object must be outside of the scope of the request to keep it alive.

- `bs = Director.create_python_business_service('BS')`: Create a Business Service object named 'BS'.
- `rsp = bs.on_process_input(request)`: Call the `on_process_input` method of the Business Service object with the request object as an argument.

### `/posts` endpoint

```python
############################
# CRUD operations posts    #
############################

@app.route('/posts', methods=['GET'])
def get_posts():
    posts = Post.query.all()
    return jsonify(posts)

@app.route('/posts', methods=['POST'])
def create_post():
    data = request.get_json()
    post = Post(title=data['title'], content=data['content'])
    db.session.add(post)
    db.session.commit()
    return jsonify(post)

@app.route('/posts/<int:id>', methods=['GET'])
def get_post(id):
    ...
```

This endpoint is used to perform CRUD operations on the `Post` object.

Thanks to the `dataclasses` module, the `Post` object can be easily serialized to JSON.

Here we use the sqlalchemy `query` method to get all the posts, and the `add` and `commit` methods to create a new post.

### `/comments` endpoint

```python
############################
# CRUD operations comments #
############################

@app.route('/comments', methods=['GET'])
def get_comments():
    comments = Comment.query.all()
    return jsonify(comments)

@app.route('/comments', methods=['POST'])
def create_comment():
    data = request.get_json()
    comment = Comment(content=data['content'], post_id=data['post_id'])
    db.session.add(comment)
    db.session.commit()
    return jsonify(comment)

@app.route('/comments/<int:id>', methods=['GET'])
def get_comment(id):
    ...
```

This endpoint is used to perform CRUD operations on the `Comment` object.

The `Comment` object is linked to the `Post` object by a foreign key.

## Troubleshooting

### How to run the Flask application in a standalone mode

You can always run a standalone Flask application with the following command:

```bash
python3 /irisdev/app/community/app.py
```

NB : You must be inside of the container to run this command.

```bash
docker exec -it iris-flask-template-iris-1 bash
```

### Restart the application in IRIS

Be in `DEBUG` mode make multiple calls to the application, and the changes will be reflected in the application.

### How to access the IRIS Management Portal

You can access the IRIS Management Portal by going to `http://localhost:53795/csp/sys/UtilHome.csp`.

### Run this template locally

For this you need to have IRIS installed on your machine.

Next you need to create a namespace named `IRISAPP`.

Install the requirements.

Install IoP :

```bash
#init iop
iop --init

# load production
iop -m /irisdev/app/community/interop/settings.py

# start production
iop --start Python.Production
```

Configure the application in the Security portal.