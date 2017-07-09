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
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blogpost', backref='owner')

    def __init__(self, email, password):
        self.email = email
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['login','register']
    if request.endpoint not in allowed_routes and 'email' not in session:
        return redirect('/login')

@app.route('/')
def index():
    return redirect('/blog')

@app.route('/blog', methods=['POST','GET'])
def blog():
    if request.args.get("id"):
        indy_id = request.args.get("id")
        indi_blog = Blogpost.query.filter_by(id = indy_id).all()
        return render_template('individual_blog.html', indi_blog=indi_blog)
    else:
        blogs = Blogpost.query.filter_by(owner=onwer).all()
        return render_template('blog.html', title="Blogz", blogs=blogs)
    
@app.route('/newpost',methods=['POST','GET'])
def newpost():

    if request.method=='POST':
        blogtitle = request.form['blogtitle']
        blogpost = request.form['blogpost']

        if blogtitle != "" and blogpost !="":
            new_blog = Blogpost(blogtitle, blogpost, owner)
            db.session.add(new_blog)
            db.session.commit()
            indy_id = new_blog.id
            indi_blog = Blogpost.query.filter_by(id = indy_id,owner=owner).all()

            return render_template('individual_blog.html', indi_blog=indi_blog)
        else:
            flash('Please provide both a blog title and content for your post!','error')

    return render_template('newpost.html')

if __name__ == '__main__':
    app.run()