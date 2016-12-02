from models.user import User
from models.user import Follow
from routes import *
from flask import request
from models import timestamp

main = Blueprint('user', __name__)
Model = User


# 查询函数
def query_by(model, s='first', **kwargs):
    if s == 'first':
        user = model.query.filter_by(**kwargs).first()
    else:
        user = model.query.filter_by(**kwargs).all()
    return user


@main.route('/')
def index():
    print('主页')
    # ms = Model.query.all()
    return render_template('user_login.html')


@main.route('/login', methods=['POST'])
def login():
    form = request.form
    # print('form', form)
    u = User(form)
    # user = index(User, username=u.username)
    user = User.query.filter_by(username=u.username).first()
    if u.valid_login(user):
        session.permanent = True
        session['user_id'] = user.id
        # print('当', u)
        return redirect(url_for('weibo.index', username=user.username))
    else:
        return redirect(url_for('.index'))


@main.route('/register', methods=['POST'])
def register():
    form = request.form
    u = User(form)
    if u.valid():
        u.save()
        session['uid'] = u.id
        print('成功')
        return redirect(url_for('.index'))

    else:
        print('失败')
        return redirect(url_for('.index'))


@main.route('/profile/<username>', methods=['GET'])
@login_required
def profile(username):
    uid = current_user().id
    u = query_by(User, username=username)
    # u = User.query.filter_by(username=username).first()
    weibo = query_by(Weibo, 'all', username=u.username)
    # weibo = Weibo.query.filter_by(username=u.username).all()
    comment = query_by(Comment, 'all', username=u.username)
    # comment = Comment.query.filter_by(username=u.username).all()
    followed = query_by(Follow, 'all', followed_id=u.id)
    # followed = Follow.query.filter_by(followed_id=u.id).all()
    print('FOLLOW ALL', Follow.query.all())
    # follow = Follow.query.filter_by(follower_id=u.id).all()

    for name in followed:
        print('uuuu', name)
    msg = '关注'
    for r in followed:
        if r.follower_id == uid:
            print('关注者ID', r.follower_id)
            print('当前登录ID', uid)
            msg = '已关注'
    return render_template('profile.html', user=u, weibo=weibo, comment=comment, msg=msg,
                           followed=followed, follow=followed)


@main.route('/follow/<id>', methods=['POST'])
@login_required
def follow(id):
    # id 是 被关注人 的id，当前看到页面的那个人的id
    p_username = User.query.filter_by(id=id).first().username
    u = current_user()
    f = Follow()
    f.followed_id = id
    f.follower_id = u.id
    f.followed_name = p_username
    f.follower_name = u.username
    print('被关注人', f.followed_name)
    print('关注人', f.follower_name)
    f.save()
    followeds = Follow.query.filter_by(followed_id=id).all()
    for followed in followeds:
        print('fffff', followed, followed.followed_name)
    print('all', Follow.query.all())
    return redirect(url_for('.profile', username=p_username))


@main.route('/unfollow/<id>', methods=['POST'])
@login_required
def unfollow(id):
    p_username = User.query.filter_by(id=id).first().username
    all = Follow.query.filter_by(followed_id=id).all()
    f_id = ''
    u = current_user()
    for bg in all:
        if bg.follower_id == u.id:
            f_id = bg.id
            break
    f = Follow.query.filter_by(id=f_id).first()
    f.delete()
    return redirect(url_for('.profile', username=p_username))




