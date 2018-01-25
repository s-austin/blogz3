from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:ok@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = '929cd6a8c076fba19ba288f1a2f6ed87'

from models import db, User, Blog

@app.route("/")
def index():
    return render_template("index.html")

@app.before_request
def require_login():
    allowed_routes = ['index', 'blog','signup','login','static']
    if request.endpoint not in allowed_routes and 'email' not in session:
       loggedin_flag = False
       return redirect('/login')

@app.route('/login', methods=['POST', 'GET'])
def login():
    login_error = ""
    emaillogin_error = ""
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        
        if user and user.password == password:
            # user has logged in
            session['email'] = email
            #flash("Logged in")
            return redirect('/')
        else:
            #flash('User password incorrect, or user does not exist', 'error')
            login_error = "Something is not right.  Check your email and password, and try again."
            return render_template('login.html', login_error=login_error)
    return render_template('login.html')

@app.route('/logout')
def logout():
    if  'email' in session:
        del session['email']
        flash('You are logged out')
        return render_template('login.html')

# See video time frame 10 minute mark https://education.launchcode.org/web-fundamentals/videos/forms-in-flask/
@app.route("/blog", methods=['GET'])
def display_blogs():


    blog_id = request.args.get("id")
    user_ID= request.args.get("userid")
    #change naming convention to better track what is going on....

    if blog_id:
        the_blog = Blog.query.get(blog_id)
        return render_template("theBlog.html", the_blog=the_blog)

    if user_ID:
        user_posts = Blog.query.filter_by(owner_id=user_ID).all()
        return render_template("singleUser.html", user_posts=user_posts)

    #posts = Blog.query.order_by(desc(Blog.pub_date))
    #return render_template("blog.html", posts=posts)

    blogs = Blog.query.order_by(Blog.pub_date.desc())
    #https://stackoverflow.com/questions/4186062/sqlalchemy-order-by-descending
    #blogs = Blog.query.all()
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
            #session['user_id'] = new_user.id
            return redirect('/newpost')
        else:
            # TODO consider using flash("User already exists")
            return render_template('signup.html', email_error=email_error, password_error=password_error, verify_error=verify_error, username_error=username_error)

    return render_template('signup.html')            

# test is flask still working?
@app.route('/newpost', methods=['POST', 'GET'])
def new_post():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        #owner = User.query.filter_by(username=session['username']).first()
        owner = User.query.filter_by(email=session['email']).first()
        pub_date = datetime.utcnow()

        title_error = ""
        body_error = ""

        if title == "" or body == "":
            if title == "":
                title_error = "Please enter a title"
            if body == "":
                body_error = "Please enter a post body"
            return render_template('/newpost.html', title=title, body=body, title_error=title_error, body_error=body_error)
        else:
            post = Blog(title, body, owner.id, pub_date)
            db.session.add(post)
            db.session.flush()   #from Adnan's example flush session to get id of inserted row
            db.session.commit()
            blog = Blog.query.order_by('-id').first()
            #the hyphen beofre the id is a wildcard for the page page
            query_param_url = "/blog?id=" + str(blog.id)
            #body_id = str(post.id)
            #return redirect("/blog?id=" + body_id)
            return redirect(query_param_url)

    return render_template('/newpost.html')
      
@app.route('/singleUser', methods=['POST', 'GET'])
def singleUser():

    owner = User.query.filter_by(email=session['email']).first()

    if request.method == 'POST':
        blog_name = request.form['blog']   
        new_blog = Blog(blog_name, owner)
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