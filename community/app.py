
from flask import Flask, jsonify
from models import Comment, Post, init_db

import iris

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'iris://SuperUser:SYS@localhost:59942/USER'

db = init_db(app)

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

###################
# CRUD operations #
###################

@app.route('/comments', methods=['GET'])
def get_comments():
    comments = Comment.query.all()
    return jsonify(comments)

@app.route('/posts', methods=['GET'])
def get_posts():
    posts = Post.query.all()
    return jsonify(posts)

if __name__ == "__main__":
    app.run(debug=True)