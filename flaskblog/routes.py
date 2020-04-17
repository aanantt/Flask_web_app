import os
import secrets

from PIL import Image
from flask import render_template, flash, url_for, redirect, request, abort
from flask_login import login_user, current_user, logout_user, login_required
from flask_socketio import emit

from flaskblog import app, bcrypt, db, sockett
from flaskblog.Forms import LoginForm, RegistrationForm, SearchForm, UpdateAccountForm, PostForm, CommentForm
from flaskblog.models import User, Post, PostComment


@app.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    query = request.form.get('search')
    search = "%{}%".format(query)
    users = User.query.filter(User.username.like(search))
    posts=Post.query.filter(Post.title.like(search))
    return render_template('search.html', users=users,posts=posts)


@app.route('/')
@app.route('/home')
def home():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    posts = Post.query.all()
    return render_template('home.html', posts=posts)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember_me.data)
            request_data = request.args.get('next')
            return redirect(request_data) if request_data else redirect(url_for('home'))
    return render_template('login.html', form=form)


@app.route('/registration', methods=['GET', 'POST'])
def registration():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('signup.html', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))


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


@app.route("/accounts", methods=['GET', 'POST'])
@login_required
def accounts():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('accounts'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account',
                           image_file=image_file, form=form)


@app.route('/post/new', methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('create_post.html', form=form)


@app.route('/post/<int:post_id>', methods=['POST', 'GET'])
@login_required
def post(post_id):
    form = CommentForm()
    post = Post.query.get_or_404(post_id)
    po = Post.query.filter_by(id=post_id).first()
    post_com = po.post_comment.all()
    p = po.likes.count()
    return render_template('post.html', post=post, p=p, form=form, post_com=post_com)


@app.route('/post/<int:post_id>/update', methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        return redirect(url_for('post', post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    return render_template('create_post.html', form=form)


@app.route('/post/<int:post_id>/delete', methods=["GET", 'POST'])
@login_required
def delete(post_id):
    post = Post.query.get(post_id)
    if post.author != current_user:
        abort(403)
        return
    db.session.delete(post)
    db.session.commit()
    flash('your Post has been deleted', 'success')
    return redirect(url_for('home'))


@app.route('/user/<int:post_id>')
@login_required
def user(post_id):
    user = User.query.filter_by(id=post_id).first()
    return render_template('user.html', user=user)


@app.route('/comment/delete/<int:comm_id>/<int:user>', methods=['GET', 'POST'])
def delete_comment(comm_id, user):
    p_com=PostComment.query.filter_by(id=comm_id, user_id=user).first()
    db.session.delete(p_com)
    db.session.commit()
    return redirect(request.referrer)


@app.route('/like/<int:post_id>/<action>')
@login_required
def like_action(post_id, action):
    post = Post.query.filter_by(id=post_id).first_or_404()
    if action == 'like':
        current_user.like_post(post)
        db.session.commit()
    if action == 'unlike':
        current_user.unlike_post(post)
        db.session.commit()
    return redirect(request.referrer)


@app.route('/comment/<int:post_id>', methods=['GET', 'POST'])
@login_required
def commentaction(post_id):
    if request.method == "POST":
        com_data = request.form.get('comment')
        print(com_data)
        addcom = PostComment(comment=com_data, user_id=current_user.id, post_id=post_id)
        db.session.add(addcom)
        db.session.commit()
        return redirect(request.referrer)


@sockett.on('vote')
def handle_vote(ballot, action):
    post = Post.query.filter_by(id=ballot).first_or_404()
    if action == 'like':
        current_user.like_post(post)
        db.session.commit()
    if action == 'unlike':
        current_user.unlike_post(post)
        db.session.commit()
    p = Post.query.filter_by(id=ballot).first()
    result1 = p.likes.count()
    emit("vote_results", {'results1': result1}, broadcast=True)

@login_required
@app.route('/me')
def me():
    return render_template('user.html',user=current_user)
