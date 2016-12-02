from flask import Blueprint
from flask import jsonify
from flask import redirect
from flask import render_template
from flask import request
from flask import send_from_directory
from flask import session
from flask import url_for
from flask import abort
from functools import wraps
from models.user import User
from models.weibo import Weibo, Comment, Like


def admin_required(f):
    @wraps(f)
    def function(*args, **kwargs):
        # your code
        print('admin required')
        if request.args.get('uid') != '1':
            print('not admin')
            abort(404)
        return f(*args, **kwargs)
    return function


def current_user():
    print('SESSION', session)
    uid = session.get('user_id', None)
    print('UID', uid)
    if uid is not None:
        u = User.query.get(uid)
        return u


def login_required(f):
    @wraps(f)
    def function(*args, **kwargs):
        u = current_user()
        if u is None:
            print('U IS NONE')
            return redirect(url_for('user.index'))
        print('U IS NOT NONE', args, kwargs)
        return f(*args, **kwargs)
    return function


def per_page(w_list):
    n = len(w_list)
    ws = [w_list[i:i + 10] for i in range(0, n, 10)]
    p, m = divmod(n, 10)
    if m > 0:
        p += 1
    page_list = [i for i in range(1, p + 1)]
    return ws, page_list
