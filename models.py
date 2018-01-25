from __main__ import app
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy(app)


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(500))
    owner_id = db.Column(db.Integer,db.ForeignKey('user.id'))
    pub_date = db.Column(db.DateTime)
    # http://flask-sqlalchemy.pocoo.org/2.1/quickstart/#simple-relationships

    def __init__(self, title, body, owner_id, pub_date):
        self.title = title
        self.body = body
        self.owner_id = owner_id
        if pub_date is None:
            pub_date = datetime.utcnow()
        self.pub_date = pub_date

# TODO below class Comment not incorporated into project hold this example for possible meta use
class Comment(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(500))
    commentowner_id = db.Column(db.Integer,db.ForeignKey('user.id'))

    def __init__(self, text, owner_id):
        self.text = text
        self.commentowner_id1 = commentowner_id
# TODO above class Comment is not incorporated into project to incorporate import via main.py if used      

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(50))
    username = db.Column(db.String(25), unique=True)
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, email, password, username):
        self.email = email
        self.password = password
        self.username = username