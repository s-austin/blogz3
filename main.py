from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:ok@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = '929cd6a8c076fba19ba288f1a2f6ed87'
#test change from laptop
#from models import db, User, Blog
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

@app.route("/")
def index():
    return render_template("index.html")

@app.before_request
def require_login():
    allowed_routes = ['index', 'blog','signup','login']
    if request.endpoint not in allowed_routes and 'email' not in session:
       loggedin_flag = False
       return redirect('/login')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        loggedin_flag = False
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and user.password == password:
            # user has logged in
            session['email'] = email
            loggedin_flag = True
            flash("Logged in")
            return redirect('/')
        else:
            loggedin_flag = False
            flash('User password incorrect, or user does not exist', 'error')

    return render_template('login.html')

@app.route('/logout')
def logout():
    if  'email' in session:
        del session['email']
        flash('You are logged out')
        return render_template('login.html')

@app.route("/blog", methods=['GET'])
def display_blogs():
    blogs = Blog.query.all()
    return render_template("blog.html", blogs=blogs)
    #return Blog.query.all()

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        email_error = ''
        password_error = ''
        verify_error = ''
        username_error = ''
       
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        verify = request.form['verify']
        
        if username == "":
            username_error = "username cannot be blank"
        elif (len(password)) < 8:
            username_error = "username has to be at least 8 characters long"

        if password == "":
            password_error = "Password cannot be blank"
        elif (len(password)) < 3:
            password_error = "Password has to be at least 3 characters long"
        elif password != verify:
            verify_error = "Passwords do not match"

        existing_user = User.query.filter_by(email=email).first()
        if not existing_user and not password_error and not verify_error:
            new_user = User(email, password, username)
            db.session.add(new_user)
            db.session.flush()   #from Adnan's example flush session to get id of inserted row
            db.session.commit()
            session['email'] = email
            loggedin_flag = True
            #session['user_id'] = new_user.id
            return redirect('/newpost')
        else:
            # TODO consider using flash("User already exists")
            return render_template('signup.html', email_error=email_error, password_error=password_error, verify_error=verify_error)

    return render_template('signup.html')            


@app.route('/newpost', methods=['POST', 'GET'])
def new_post():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        #owner = User.query.filter_by(username=session['username']).first()
        owner = User.query.filter_by(email=session['email']).first()
        pub_date = datetime.utcnow()

        if title == "" or body == "":
            if title == "":
                title_error = "Please enter a title"
            if body == "":
                body_error = "Please enter a post body"
            return render_template('/newpost.html', title=title, body=body, title_error=title_error, body_error=body_error, owner_id=owner_id)
        else:
            post = Blog(title, body, owner.id, pub_date)
            db.session.add(post)
            db.session.commit()
            blog = Blog.query.order_by('-id').first()
            #the hyphen beofre the id is a wildcard for the page page
            query_param_url = "/blog?id=" + str(blog.id)
            #body_id = str(post.id)
            #return redirect("/blog?id=" + body_id)
            return redirect(query_param_url)

    return render_template('/newpost.html')

@app.route('/newpost', methods=['POST', 'GET'])        

@app.route('/singleUser', methods=['POST', 'GET'])
def singleUser():

    owner = User.query.filter_by(email=session['email']).first()

    if request.method == 'POST':
        blog_name = request.form['blog']   
        new_blog = Task(blog_name, owner)
        db.session.add(new_blog)
        db.session.commit()

    blogs = Blog.query.filter_by(owner=owner).all()
    return render_template('singleUser.html', title="Your Blog!", 
        blogs=blogs)



# TODO add delete only if logged in
@app.route('/delete-blog', methods=['POST'])
def delete_blog():

    blog_id = int(request.form['blog-id'])
    blog = Blog.query.get(blog_id)
    db.session.delete(blog)
    db.session.commit()

    return redirect('/')


if __name__ == '__main__':
    app.run()