import functools
from flask import Flask, Blueprint, render_template, jsonify, request, session, redirect, url_for, flash, g
from werkzeug.security import generate_password_hash, check_password_hash

from pymongo import MongoClient
from hobbytown.forms import UserLoginForm, UserCreateForm

client = MongoClient("localhost", 27017)
db = client.base
user_db = db.user

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/login', methods=('POST','GET'))
def login():
    form = UserLoginForm()
    if request.method == 'POST':
        error = None
        ### userid 와 usersecret이
        form_user = form.username.data
        form_secret = form.secret.data
        try:
            user_id = user_db.find_one({"id": form_user})['id']
            user_secret = check_password_hash(user_db.find_one({"id": form_user})['secret'], form_secret)
        except:
            user_id = None
            user_secret = None
        print(user_db.find_one({"id": form_user}))
        if not user_secret:
            error = "아이디 혹은 비밀번호가 일치하지 않습니다"
        if error is None:
            session.clear()
            session['user_id'] = user_id
            _next = request.args.get('next', '')
            if _next:
                return redirect(_next)
            else:
                print(error)
                # ==return redirect('../mongo')
                return redirect(url_for('main.mongoTest'))
        flash(error)
    return render_template('auth/login.html', form=form)


@bp.route('/signup', methods=('POST', 'GET'))
def signup():
    form = UserCreateForm()
    form_user = form.username.data
    form_secret = form.secret1.data
    form_email = form.email.data

    if request.method == 'POST' and form.validate_on_submit():
        user_id = user_db.find_one({'id': form_user})
        user_email = user_db.find_one({'email': form_email})
        if (not user_id) & (not user_email):
            user_dict = {
                "id": form_user,
                "secret": generate_password_hash(form_secret),
                "email": form_email,
            }
            user_db.insert_one(user_dict)
            return redirect(url_for('main.mongoTest'))
        elif (user_id is None) & (user_email is None):
            flash('이미 존재하는 아이디입니다')
            flash('이미 존재하는 이메일입니다')
        elif user_id is None:
            flash('이미 존재하는 이메일입니다')
        else:
            flash('이미 존재하는 아이디입니다')

    return render_template('auth/signup.html', form=form)


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        g.user = user_db.find_one({'id': user_id})['id']

    print(g.user)


@bp.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(session['url'])


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(*args, **kwargs):
        if g.user is None:
            _next = request.url if request.method == 'GET' else ''
            return redirect(url_for('auth.login', next=_next))
        return view(*args, **kwargs)
    return wrapped_view


@bp.after_app_request
def dddd(self):
    if request.referrer:
        session['url'] = request.referrer
    return self
