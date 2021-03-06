import os
import secrets
import json
from PIL import Image
from breddit.models import User, Post, Comment
from breddit import app, db, bcrypt
from flask import render_template, url_for, flash, redirect, request, abort
from breddit.forms import RegistrationForm, LoginForm, UpdateAccountForm, PostForm
from flask_login import login_user, current_user, logout_user, login_required


@app.route("/")
@app.route("/index")
def index():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=6)
    return render_template('index.html', posts=posts)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data,password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f'Account created for {form.username.data}!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('index'))


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)

    i.save(picture_path)

    return picture_fn

@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated.', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
            form.username.data = current_user.username
            form.email.data = current_user.email
    image_file = url_for(
        'static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account', image_file=image_file, form=form)


def save_post_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(
        app.root_path, 'static/post_pics', picture_fn)

    output_size = (500, 500)
    i = Image.open(form_picture)
    i.thumbnail(output_size)

    i.save(picture_path)

    return picture_fn


@app.route("/post/new", methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        bred_img = save_post_picture(form.post_img.data)
        post = Post(title=form.title.data, link=form.link.data,
                    content=form.content.data, author=current_user, post_img=bred_img)
        db.session.add(post)
        db.session.commit()
        flash('Your post has been created!', 'success')
        return redirect(url_for('index'))
    return render_template('create_post.html', title='New Post',
                           form=form, legend='New Post')


@app.route("/post/<int:post_id>")
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', user=current_user, title=post.title, bred_img=post.post_img, post=post)


@app.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        if form.post_img.data:
            bred_img = save_post_picture(form.post_img.data)
            post.post_img = bred_img
        post.title = form.title.data
        post.content = form.content.data
        post.link = form.link.data
        db.session.commit()
        flash('Your post has been updated!', 'success')
        return redirect(url_for('post', post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        post.link = form.link.data
    post_img = url_for(
        'static', filename='post_pics/' + post.post_img)
    return render_template('create_post.html', title='Update Post',
                           form=form, legend='Update Post', post_img=post_img)


@app.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('index'))

@app.route("/user/<string:username>")
def user_posts(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user).order_by(Post.date_posted.desc()).paginate(page=page, per_page=6)
    return render_template('user_posts.html', posts=posts, user=user)


@app.route("/upvote", methods=['POST'])
@login_required
def upvote_post():
    if request.method == "POST":
        data_received = json.loads(request.data)
        post = Post.query.filter_by(id=data_received['id']).first()

        if post:
            setattr(post, "score", post.score + 1)
            db.session.commit()

            return json.dumps({'status': 'success'})
        return json.dumps({'status': 'no post found'})
    return redirect(url_for('index'))


@app.route("/downvote", methods=['POST'])
@login_required
def downvote_post():
    if request.method == "POST":
        data_received = json.loads(request.data)
        post = Post.query.filter_by(id=data_received['id']).first()

        if post:
            setattr(post, "score", post.score - 1)
            db.session.commit()

        return json.dumps({'status': 'success'})
    return redirect('index.html')


@app.route("/create-comment/<post_id>", methods=['GET', 'POST'])
@login_required
def create_comment(post_id):
    post = Post.query.get_or_404(post_id)
    body = request.form.get('body')

    if not body:
        flash('Comment cannot be empty.', category='error')
    else:
        post = Post.query.filter_by(id=post_id)
        if post:
            comment = Comment(
                body=body, author=current_user.id, post_id=post_id)
            db.session.add(comment)
            db.session.commit()
        else:
            flash('Post does not exist.', category='error')

    return redirect(url_for('post', post_id=post_id))


@app.route("/delete-comment/<comment_id>", methods=['GET', 'POST'])
@login_required
def delete_comment(comment_id):
    comment = Comment.query.filter_by(id=comment_id).first()

    if not comment:
        flash('Comment does not exist.', category='error')
    elif current_user.id != comment.author and current_user.id != comment.post.author:
        flash('You do not have permission to delete this comment.', category='error')
    else:
        db.session.delete(comment)
        db.session.commit()

    return redirect(url_for('post', post_id=comment.post_id))
