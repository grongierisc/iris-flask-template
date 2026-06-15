
import json
from typing import Any

from flask import Flask, jsonify, make_response, request

from models import Comment, Post, init_db

from iop import Director

import iris

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'iris+emb://IRISAPP'

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

########################
# IRIS interop example #
########################
_bs: Any = None


def get_business_service() -> Any:
    global _bs
    if _bs is None:
        _bs = Director.create_python_business_service('BS')
    return _bs

@app.route('/interop', methods=['GET', 'POST', 'PUT', 'DELETE'])
def interop():
    try:
        rsp = get_business_service().process_input(request)
    except Exception as exc:
        payload = {
            "error": "interop_unavailable",
            "detail": str(exc)
        }
        return make_response(jsonify(payload), 503)

    status = getattr(rsp, 'status', 200)
    headers = getattr(rsp, 'headers', {}) or {}
    body = getattr(rsp, 'body', rsp)

    response = make_response(body, int(status))
    for key, value in headers.items():
        response.headers[key] = value
    return response


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
    comment = Comment.query.get(id)
    return jsonify(comment)

@app.route('/comments/<int:id>', methods=['PUT'])
def update_comment(id):
    comment = Comment.query.get(id)
    if comment is None:
        return make_response(jsonify({"error": "comment_not_found"}), 404)
    data = request.get_json()
    comment.content = data['content']
    db.session.commit()
    return jsonify(comment)

@app.route('/comments/<int:id>', methods=['DELETE'])
def delete_comment(id):
    comment = Comment.query.get(id)
    db.session.delete(comment)
    db.session.commit()
    return jsonify(comment)

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
    post = Post.query.get(id)
    return jsonify(post)

@app.route('/posts/<int:id>', methods=['PUT'])
def update_post(id):
    post = Post.query.get(id)
    if post is None:
        return make_response(jsonify({"error": "post_not_found"}), 404)
    data = request.get_json()
    post.title = data['title']
    post.content = data['content']
    db.session.commit()
    return jsonify(post)

@app.route('/posts/<int:id>', methods=['DELETE'])
def delete_post(id):
    post = Post.query.get(id)
    db.session.delete(post)
    db.session.commit()
    return jsonify(post)

if __name__ == "__main__":
    app.run(debug=True)