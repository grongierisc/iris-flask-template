
from flask import Flask, jsonify
from models import Comment, Post, init_db

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'iris://SuperUser:SYS@localhost:59942/USER'

db = init_db(app)

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