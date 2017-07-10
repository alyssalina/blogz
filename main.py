from flask import Flask, request, render_template, redirect, session, flash
from flask_sqlalchemy import SQLAlchemy
app = Flask(__name__)
app.config['DEBUG']=True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:Dannya32@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO']= True
db = SQLAlchemy(app)

app.secret_key = 'K^kzqbF&ZKEY:68fQ=iCY#M&'

#create Blogpost Class
class Blogpost (db.Model):
    id = db.Column(db.Integer, primary_key=True)
    blogtitle = db.Column(db.String(120))
    blogpost = db.Column(db.String(20000))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, blogtitle, blogpost, owner):
        self.blogtitle = blogtitle
        self.blogpost = blogpost
        self.owner = owner

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blogpost', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.before_request
def require_login():
    #note to self, this is the function, not the /url
    allowed_routes = ['login','signup','blog']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/login', methods=['POST','GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and user.password == password:
            session['username'] = username
            flash("Welcome back!")
            return redirect('/newpost')
        elif user and user.password != password:
            flash('Password is incorrect.','error')
        else:
            flash('User does not exist','error')

    return render_template('login.html')

@app.route('/signup', methods = ['POST','GET'])
def signup():
    if request.method =='POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        if username == '' or password == '' or verify =='':
            flash("One or more fields are invalid",'error')
        elif password != verify:
            flash("Password and verifcation do not match")
        elif len(username)<3:
            flash ("Invalid username. Username must be at least 3 characters")
        elif len(password)<3:
            flash ("Invalid password. Password must be at least 3 characters but more is better!")
        else:
            existing_user = User.query.filter_by(username=username).first()
            if not existing_user:
                new_user = User(username,password)
                db.session.add(new_user)
                db.session.commit()

                session['username'] = username
                
                flash("Welcome to your blog!")
                return redirect('/newpost')
            else:
                flash ("Username already exists")
    
    return render_template('signup.html')

@app.route('/logout')
def logout():
    del session['username']
    return redirect ('/blog')


@app.route('/')
def index():
    users = User.query.all()
    return render_template('index.html', title="Blog Writers", users=users)

@app.route('/blog', methods=['POST','GET'])
def blog():
    if request.args.get("id"):
        indy_id = request.args.get("id")
        indi_blog = Blogpost.query.filter_by(id = indy_id).all()
        return render_template('individual_blog.html', indi_blog=indi_blog)
    elif request.args.get("user"):
        indi_user = request.args.get("user")
        indi_posts = Blogpost.query.filter_by(owner_id = indi_user).all()
        return render_template('individual_user.html', indi_posts=indi_posts)
    else:
        #need to show only specific owners still
        blogs = Blogpost.query.all()
        return render_template('blog.html', title="Blogz", blogs=blogs)
    
@app.route('/newpost',methods=['POST','GET'])
def newpost():

    owner = User.query.filter_by(username=session['username']).first()

    if request.method=='POST':
        blogtitle = request.form['blogtitle']
        blogpost = request.form['blogpost']

        if blogtitle != "" and blogpost !="":
            new_blog = Blogpost(blogtitle, blogpost, owner)
            db.session.add(new_blog)
            db.session.commit()
            indy_id = new_blog.id
            indi_blog = Blogpost.query.filter_by(owner = indy_id).all()

            return render_template('individual_blog.html', indi_blog=indi_blog)
        else:
            flash('Please provide both a blog title and content for your post!','error')

    return render_template('newpost.html')



if __name__ == '__main__':
    app.run()