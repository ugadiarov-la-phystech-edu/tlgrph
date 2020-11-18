from secrets import token_urlsafe

from flask import Flask, render_template, redirect, url_for, session, request
from flask_wtf import FlaskForm

from flask_bootstrap import Bootstrap

from wtforms import StringField, SubmitField
from wtforms.widgets import TextArea
from wtforms.validators import Required

from redis import Redis


def acquire_post_ids():
    max_post_id = int(app.config['CONNECTION'].incr(app.config['REDIS_ID_SEQUENCE'], app.config['ID_ACQUIRE_COUNT']))
    current_post_id = max_post_id - app.config['ID_ACQUIRE_COUNT'] + 1
    app.config['MAX_POST_ID'] = max_post_id
    app.config['CURRENT_POST_ID'] = current_post_id


app = Flask(__name__)
Bootstrap(app)
app.config.from_envvar('FLASK_CONFIG')
app.config['CONNECTION'] = Redis(host=app.config['REDIS_HOST'], port=app.config['REDIS_PORT'], db=0)
acquire_post_ids()


def get_post_key(post_id):
    return f'post:{post_id}'


class PostForm:
    title = StringField('Title', widget=TextArea(), validators=[Required()])
    author = StringField('Your name', widget=TextArea(), validators=[Required()])
    story = StringField('Your story...', widget=TextArea(), validators=[Required()])


class PostFormPublish(FlaskForm, PostForm):
    submit = SubmitField('Publish')


class PostFormEdit(FlaskForm, PostForm):
    submit = SubmitField('Edit')


def create():
    current_post_id = app.config['CURRENT_POST_ID']
    max_post_id = app.config['MAX_POST_ID']
    connection = app.config['CONNECTION']
    expriration_time = app.config['REDIS_EXPIRATION_TIME_SECONDS']
    
    form = PostFormPublish()
    if form.validate_on_submit():
        if 'token' not in session:
            session['token'] = token_urlsafe()
        
        token = session['token']        
        post_key = get_post_key(current_post_id)
        pipeline = connection.pipeline()
        pipeline.hset(post_key, mapping={'title': form.title.data, 'author': form.author.data, 'story': form.story.data, 'token': token})
        pipeline.expire(post_key, expriration_time)
        pipeline.execute()
        
        if current_post_id == max_post_id:
            acquire_post_ids()
        else:
            app.config['CURRENT_POST_ID'] += 1
        
        return redirect(url_for('create_update', post_id=str(current_post_id)))
    return render_template('main.html', form=form, readonly=False)


def update(post_id):
    connection = app.config['CONNECTION']
    
    post_key = get_post_key(post_id)
    post = connection.hgetall(post_key)
    if not post:
        return render_template('404.html'), 404
    
    form = PostFormEdit()
    post = {key.decode() : value.decode() for key, value in post.items()}
    editable = 'token' in session and session['token'] == post['token']
    if form.validate_on_submit() and editable:
        connection.hset(post_key, mapping={'title': form.title.data, 'author': form.author.data, 'story': form.story.data})
    else:
        form.title.data = post['title']
        form.author.data = post['author']
        form.story.data = post['story']
    
    return render_template('main.html', form=form, readonly=not editable)


@app.route('/', methods=['GET', 'POST'])
@app.route('/<post_id>', methods=['GET', 'POST'])
def create_update(post_id=None):
    if post_id is None:
        return create()
    else:
        return update(post_id)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

