from flask import Flask, render_template, request,redirect
from flask import session
import os
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

with open('config.json', 'r') as c:
    params = json.load(c)["params"]
local_server = True
app = Flask(__name__)
app.secret_key = 'super-web-gana'
app.config['UPLOAD_FOLDER'] = params['upload_location']

if (local_server):
    app.config['SQLALCHEMY_DATABASE_URI'] = params["local_url"]
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = params["prod_url"]

db = SQLAlchemy(app)

#sno,name,email,phone_num,mes,date
class Contact(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    phone_num = db.Column(db.String(12), nullable=False)
    email = db.Column(db.String(20), nullable=False)
    mes = db.Column(db.String(120), nullable=False)
    date = db.Column(db.String(12))

class Post(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    tagline = db.Column(db.String(80), nullable=False)
    slug = db.Column(db.String(120), nullable=False)
    content = db.Column(db.String(300), nullable=False)
    date = db.Column(db.String(12))
    img_file = db.Column(db.String(20),nullable = True)


@app.route("/")
def home():
    posts = Post.query.filter_by().all()
    return render_template("index.html",params = params,post = posts)


@app.route("/post/<string:post_slug>",methods =['GET'])
def post_route(post_slug):
    post = Post.query.filter_by(slug = post_slug).first()
    return render_template("post.html",params=params,post = post)

@app.route("/about")
def about():
    return render_template("about.html",params = params)

@app.route("/uploader",methods = ['GET', 'POST'])
def uploader():
    if "user" in session and session['user'] == params['admin_user']:
        if request.method=='POST':
            f = request.files['file1']
            f.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(f.filename)))
            return "Uploaded successfully!"

@app.route("/logout")
def logout():
    session.pop('user')
    return redirect("/dashboard")

@app.route("/dashboard", methods = ['GET', 'POST'])
def dashboard():
    if ("user" in session and session['user']==params['admin_user']):
        post = Post.query.all()
        return render_template("dashboard.html", params=params, post = post)

    if request.method=="POST":
        username = request.form.get("uname")
        userpass = request.form.get("pass")
        if username==params['admin_user'] and userpass==params['admin_password']:
            # set the session variable
            session['user']=username
            post = Post.query.all()
            return render_template("dashboard.html", params=params,post = post)
        else:
            return render_template("login.html", params=params)
    else:
        return render_template("login.html", params=params)

@app.route("/edit/<string:sno>", methods = ['GET', 'POST'])
def edit(sno):
    if "user" in session and session['user'] == params['admin_user']:
        if request.method == "POST":
            box_title = request.form.get('title')
            box_tagline = request.form.get('tagline')
            box_slug = request.form.get('slug')
            box_content = request.form.get('content')
            box_img_file = request.form.get('img_file')
            box_date = datetime.now()

            if sno == '0' :
                post = Post(title=box_title,tagline=box_tagline, slug=box_slug, content=box_content,  img_file=box_img_file, date=box_date)
                db.session.add(post)
                db.session.commit()
            else:
                post = Post.query.filter_by(sno=sno).first()
                post.title = box_title
                post.tagline = box_tagline
                post.slug = box_tagline
                post.content = box_content
                post.img_file = box_img_file
                post.date = box_date
                db.session.commit()
                return redirect('/edit/' + sno)
        post = Post.query.filter_by(sno=sno).first()
        return render_template('edit.html',params=params,post=post,sno = sno)

@app.route("/delete/<string:sno>", methods = ['GET', 'POST'])
def delete(sno):
    if "user" in session and session['user'] == params['admin_user']:
        post = Post.query.filter_by(sno=sno).first()
        db.session.delete(post)
        db.session.commit()
        return redirect('/dashboard')


@app.route("/contact",methods = ['GET', 'POST'])
def contact():
    if(request.method=='POST'):
        '''Add entry to the database'''
        fName = request.form.get('name')
        mail = request.form.get('email')
        phoneNO = request.form.get('phone')
        messages = request.form.get('message')
        entry = Contact(name = fName,phone_num = phoneNO,email = mail,mes =messages,date = datetime.now())
        db.session.add(entry)
        db.session.commit()
    return render_template("contact.html",params = params)
app.run(debug=True)