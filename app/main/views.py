from flask import render_template, flash, redirect, url_for, request, \
                  current_app, abort, jsonify, make_response
from . import main
from ..models import User, Role, Permission, Post, Comment, Vote_comment, \
                     Vote_post
from .. import db
from ..decorators import admin_required, permission_required
from .forms import EditProfileForm, EditProfileAdminForm, PostForm, CommentForm
from datetime import datetime
from flask_login import login_required, current_user


@main.route('/', methods=['GET', 'POST'])
def index():
    form = PostForm()
    if current_user.can(Permission.WRITE_ARTICLES) and \
            form.validate_on_submit():
        post = Post(body=form.body.data,
                    author=current_user._get_current_object())
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    show_followed = False
    if current_user.is_authenticated:
        show_followed = bool(request.cookies.get('show_followed', ''))
    if show_followed:
        query = current_user.followed_posts
    else:
        query = Post.query.filter_by(deleted=False)
    pagination = query.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['BLOG_POSTS_PER_PAGE'],
        error_out=False)
    posts = pagination.items
    post_votes = Vote_post.query
    return render_template('index.html', form=form, posts=posts,
                            pagination=pagination, show_followed=show_followed,
                            post_votes=post_votes)


@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    pagination = user.posts.filter_by(deleted=False) \
                           .order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['BLOG_POSTS_PER_PAGE'],
        error_out=False)
    posts = pagination.items
    post_votes = Vote_post.query
    return render_template('user.html', user=user, posts=posts,
                           pagination=pagination, post_votes=post_votes)


@main.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user)
        db.session.commit()
        flash('Ваш профиль обновлен.')
        return redirect(url_for('.user', username=current_user.username))
    form.name.data = current_user.name
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', form=form)


@main.route('/edit_profile/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(id):
    user = User.query.get_or_404(id)
    form = EditProfileAdminForm(user=user)
    if form.validate_on_submit():
        user.email = form.email.data
        user.username = form.username.data
        user.confirmed = form.confirmed.data
        user.role = Role.query.get(form.role.data)
        user.name = form.name.data
        user.location = form.location.data
        user.about_me = form.about_me.data
        db.session.add(user)
        db.session.commit()
        flash('Профайл {} был обновлен.'.format(user.username))
        return redirect(url_for('.user', username=user.username))
    form.email.data = user.email
    form.username.data = user.username
    form.confirmed.data = user.confirmed
    form.role.data = user.role_id
    form.name.data = user.name
    form.location.data = user.location
    form.about_me.data = user.about_me
    return render_template('edit_profile.html', form=form, user=user)


@main.route('/post/<int:id>', methods=['GET', 'POST'])
def post(id):
    post = Post.query.filter_by(id=id, deleted=False).first_or_404()
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(body=form.body.data,
                          post=post,
                          author=current_user._get_current_object())
        db.session.add(comment)
        db.session.commit()
        flash('Ваш комментарий опубликован.')
        return redirect(url_for('.post', id=post.id, page=-1))
    page = request.args.get('page', 1, type=int)
    if page == -1:
        page = (post.comments.count() - 1) // \
                current_app.config['BLOG_COMMENTS_PER_PAGE'] + 1
    pagination = post.comments.filter_by(deleted=False) \
                     .order_by(Comment.timestamp.asc()).paginate(
                 page, per_page=current_app.config['BLOG_COMMENTS_PER_PAGE'],
                 error_out=False)
    comments = pagination.items
    comment_votes = Vote_comment.query
    post_votes = Vote_post.query
    return render_template('post.html', posts=[post], form=form,
                           comments=comments, pagination=pagination,
                           comment_votes=comment_votes, post_votes=post_votes)

@login_required
@permission_required(Permission.WRITE_ARTICLES)
@main.route('/post_remove/<int:id>', methods=['PUT', 'DELETE'])
def post_remove(id):
    data = {'status': 0, 'message': 'Error'}
    post = Post.query.filter_by(id=id).first()
    if post:
        if request.method == 'PUT':
            post.deleted = False
            data = {'status': 2, 'message': 'Post restored'}
        elif request.method == 'DELETE':
            post.deleted = True
            data = {'status': 1, 'message': 'Post removed'}
        db.session.add(post)
        db.session.commit()
    else:
        data = {'status': 3, 'message': 'Invalid user'}
    return jsonify(data)


@main.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.WRITE_ARTICLES)
def edit(id):
    post = Post.query.filter_by(id=id, deleted=False).first_or_404()
    if current_user != post.author and \
            not current_user.can(Permission.ADMINISTER):
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.body = form.body.data
        db.session.add(post)
        db.session.commit()
        flash("Пост обновлен.")
        return redirect(url_for('.post', id=post.id))
    form.body.data = post.body
    return render_template('edit_post.html', form=form)


@main.route('/comment_edit/<int:id>', methods=['PUT'])
@login_required
@permission_required(Permission.WRITE_ARTICLES)
def edit_comment(id):
    comment = Comment.query.filter_by(id=id, deleted=False).first_or_404()
    data = {'status': 0, 'message': 'invalid comment'}
    if comment:
        comment.edit_ping(current_user.username)
        comment.body_html = request.form['data']
        db.session.add(comment)
        db.session.commit()
        data = {'status': 1, 'message': 'Comment edited'}
    return jsonify(data)


@main.route('/comment_vote/', methods=['POST'])
@login_required
@permission_required(Permission.COMMENT)
def comment_vote():
    data = {'status': 0, 'message': 'Invalid method: {}'.format(request.method)}
    if request.method == 'POST':
        comment_vote = Vote_comment.query.filter_by(
            comment_id=request.form['comment'], voter_id=current_user.id).first()
        if comment_vote:
            comment_vote.vote = request.form['vote']
            db.session.add(comment_vote)
            db.session.commit()
            data = {'status': 1, 'message': 'User id {} re-voted comment id {}'
                .format(current_user.id,
                        request.form['comment'])}
        else:
            comment_vote = Vote_comment(vote=request.form['vote'],
                                        voter=current_user,
                                        comment_id=request.form['comment'])
            db.session.add(comment_vote)
            db.session.commit()
            data = {'status': 1, 'message': 'User id {} voted comment id {}'
                .format(current_user.id,
                        request.form['comment'])}
    return jsonify(data)


@main.route('/post_vote/', methods=['POST'])
@login_required
@permission_required(Permission.WRITE_ARTICLES)
def post_vote():
    data = {'status': 0, 'message': 'Invalid method: {}'.format(request.method)}
    if request.method == 'POST':
        post_vote = Vote_post.query.filter_by(
            post_id=request.form['post'], voter_id=current_user.id).first()
        if post_vote:
            post_vote.vote = request.form['vote']

            data = {'status': 1, 'message': 'User id {} re-voted post id {}'
                .format(current_user.id,
                        request.form['post'])}
        else:
            post_vote = Vote_post(vote=request.form['vote'],
                                        voter=current_user,
                                        post_id=request.form['post'])
            data = {'status': 1, 'message': 'User id {} voted post id {}'
                .format(current_user.id,
                        request.form['post'])}
        db.session.add(post_vote)
        db.session.commit()
    return jsonify(data)


@login_required
@permission_required(Permission.WRITE_ARTICLES)
@main.route('/comment_remove/<int:id>', methods=['PUT', 'DELETE'])
def comment_remove(id):
    data = {'status': 0, 'message': 'Error'}
    comment = Comment.query.filter_by(id=id).first()
    if comment:
        if request.method == 'PUT':
            comment.deleted = False
            data = {'status': 2, 'message': 'Comment restored'}
        elif request.method == 'DELETE':
            comment.deleted = True
            data = {'status': 1, 'message': 'Comment removed'}
        db.session.add(comment)
        db.session.commit()
    else:
        data = {'status': 3, 'message': 'Invalid user'}
    return jsonify(data)


@main.route('/follow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Недействительный пользователь.')
        return redirect(url_for('.index'))
    if current_user.is_following(user):
        flash('Вы уже подписаны на этого пользователя.')
        return redirect(url_for('.user', username=username))
    current_user.follow(user)
    flash('Теперь Вы подписаны на {}.'.format(username))
    return redirect(url_for('.user', username=username))


@main.route('/unfollow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if User is None:
        flash('Недействительный пользователь.')
        return redirect(url_for('.index'))
    if not current_user.is_following(user):
        flash('Вы не подписаны на этого пользователя.')
        return redirect(url_for('.user', username=username))
    current_user.unfollow(user)
    flash("Вы больше не подписаны на {}.".format(username))
    return redirect(url_for('.user', username=username))


@main.route('/followers/<username>')
def followers(username):
    user = User.query.filter_by(username=username).first()
    if User is None:
        flash('Недействительный пользователь.')
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    pagination = user.followers.paginate(
        page, per_page=current_app.config['BLOG_FOLLOWERS_PER_PAGE'],
        error_out=False)
    follows = [{'user': item.follower, 'timestamp': item.timestamp}
               for item in pagination.items]
    return render_template('followers.html', user=user, title="Подписчики",
                           endpoint='.followers', pagination=pagination,
                           follows=follows)


@main.route('/followed-by/<username>')
def followed_by(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Недействительный пользователь.')
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    pagination = user.followed.paginate(
        page, per_page=current_app.config['BLOG_FOLLOWERS_PER_PAGE'],
        error_out=False)
    follows = [{'user': item.followed, 'timestamp': item.timestamp}
               for item in pagination.items]
    return render_template('followers.html', user=user, title="Подписки",
                            endpoint='.followed_by', pagination=pagination,
                            follows=follows)


@main.route('/all')
@login_required
def show_all():
    resp = make_response(redirect(url_for('.index')))
    resp.set_cookie('show_followed', '', max_age=30*24*60*60)
    return resp


@main.route('/followed')
@login_required
def show_followed():
    resp = make_response(redirect(url_for('.index')))
    resp.set_cookie('show_followed', '1', max_age=30*24*60*60)
    return resp


@main.route('/moderate')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate():
    page = request.args.get('page', 1, type=int)
    pagination = Comment.query.filter_by(deleted=False).order_by(Comment.timestamp.desc()).paginate(
        page, per_page=current_app.config['BLOG_COMMENTS_PER_PAGE'],
        error_out=False)
    comments = pagination.items
    comment_votes = Vote_comment.query
    return render_template('moderate.html', comments=comments,
                            pagination=pagination, page=page,
                            comment_votes=comment_votes)


@main.route('/moderate/enable/<int:id>')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate_enable(id):
    comment = Comment.query.get_or_404(id)
    comment.disabled = False
    db.session.add(comment)
    db.session.commit()
    return redirect(url_for('.moderate',
                            page=request.args.get('page', 1, type=int)))


@main.route('/moderate/disabled/<int:id>')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate_disabled(id):
    comment = Comment.query.get_or_404(id)
    comment.disabled = True
    db.session.add(comment)
    db.session.commit()
    return redirect(url_for('.moderate',
                            page=request.args.get('page', 1, type=int)))
