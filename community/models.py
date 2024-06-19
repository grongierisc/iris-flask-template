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


def init_db(app):
    db.init_app(app)

    with app.app_context():
        db.drop_all()
        db.create_all()
        # Create fake data
        post1 = Post(title='Post The First', content='Content for the first post')
        post2 = Post(title='Post The Second', content='Content for the Second post')
        post3 = Post(title='Post The Third', content='Content for the third post')

        comment1 = Comment(content='Comment for the first post', post=post1)
        comment2 = Comment(content='Comment for the second post', post=post2)
        comment3 = Comment(content='Another comment for the second post', post=post2)
        comment4 = Comment(content='Another comment for the first post', post=post1)


        db.session.add_all([post1, post2, post3])
        db.session.add_all([comment1, comment2, comment3, comment4])

        db.session.commit()

    return db