from models.user import Follow, Message
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
    print('request', request)
    # ms = Model.query.all()
    s = session.get('user_id', None)
    if s is not None:
        u = User.query.filter_by(id=session['user_id']).first()
        return redirect(url_for('weibo.index', username=u.username, page=1))
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
        return redirect(url_for('weibo.index', username=user.username,page=1))
    else:
        return redirect(url_for('.index'))


@main.route('/register', methods=['POST'])
def register():
    form = request.form
    u = User(form)
    if u.valid():
        u.save()
        session['uid'] = u.id
        return redirect(url_for('.index'))
    else:
        return redirect(url_for('.index'))


@main.route('/profile/<username>', methods=['GET'])
@login_required
def profile(username):
    current_u = current_user()
    uid = current_u.id
    un = current_u.username
    u = query_by(User, username=username)
    if current_u != u:
        weibo, comment, followed, follow = all_info(username)
        msg = '关注'
        for r in followed:
            if r.follower_id == uid:
                msg = '已关注'
        return render_template('profile.html', user=u, weibo=weibo, comment=comment, msg=msg,
                               followed=followed, follow=follow,un=current_u)
    else:
        weibo, comment, followed, follow = all_info(un)
        return render_template('person_profile.html', user=u, weibo=weibo, comment=comment,
                               followed=followed, follow=follow, un=un)


@main.route('/follow/<id>', methods=['POST'])
@login_required
def follow(id):
    # id 是 被关注人 的id，当前看到页面的那个人的id
    p_username = User.query.filter_by(id=id).first().username
    u = current_user()
    f = Follow()
    f.followed_id = id
    f.follower_id = u.id
    f.followed = User.query.filter_by(id=id).first()
    f.follower = u
    f.save()
    followeds = Follow.query.filter_by(followed_id=id).all()
    for followed in followeds:
        print('fffff', followed)
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


@main.route('/msg/<id>', methods=['POST'])
@login_required
def msg(id):
    content = request.form.get('content')
    p = request.form.get('id')
    msg = Message(content)
    p_username = User.query.filter_by(id=id).first().username
    u = current_user()
    msg.receiver_id = id
    msg.sender_id = u.id
    msg.receiver = User.query.filter_by(id=id).first()
    msg.sender = u
    msg.save()
    if p == '1':
        return redirect(url_for('.profile', username=p_username))
    else:
        return redirect(url_for('.msg_index', username=u.username))


@main.route('/msg/<username>')
@login_required
def msg_index(username):
    print('看谁的私信',username, '当前用户', current_user().username,  username == current_user().username )
    u = current_user()
    if username == u.username:
        # for user, msg in relation_msg(username).items():
        #     print('uuu',user, 'msg',msg['rec'].content, 'msg2', msg['send'].content)
        # # print('ggg', relation_msg(username))
        msg_from = Message.query.filter_by(receiver_id=u.id).all()
        msg_to = Message.query.filter_by(sender_id=u.id).all()
        return render_template('msg.html', rec=msg_from, send=msg_to, user=u)
    else:
        return redirect(url_for('.index'))


def relation_msg(username):
    user = User.query.filter_by(username=username).first()
    msg_to = user.fro
    msg_from = user.rec
    re_msg = {}
    for r in relation_list(username):
        rec = []
        for m_t in msg_to:
            if m_t.receiver.username == r:
                # re_msg[r]['rec'] = []
                rec.append(m_t)
        for m_f in msg_from:
            sen = []
            if m_f.sender.username == r:
                # re_msg[r]['send'] = []
                sen.append(m_f)
        re_msg[r] = {'rec':rec, 'send':sen}
    return re_msg


def relation_list(username):
    msg_to, msg_from = user_msg(username)
    r_list = []
    for m_t in msg_to:
        r_list.append(m_t.receiver.username)
    for m_f in msg_from:
        r_list.append(m_f.sender.username)
        r_list = list(set(r_list))
    return r_list


def user_msg(username):
    user = User.query.filter_by(username=username).first()
    msg_to = user.fro
    msg_from = user.rec
    return msg_to, msg_from


@main.route('/logout', methods=['GET'])
@login_required
def logout():
    session.pop('user_id', None)
    return redirect(url_for('.index'))


def all_info(username):
    user = User.query.filter_by(username=username).first()
    return user.weibos, user.comments, user.followed, user.follower


@main.route('/user/update/<int:id>', methods=['POST'])
@login_required
def update(id):
    u = current_user()
    user = User.query.get(id)
    form = request.form
    pwd = form.get('password')
    if len(pwd) > 2 and pwd != user.password:
        user.avatar = form.get('avatar', user.avatar)
        user.password = pwd
        user.save()
        print('user.save', user)
        return redirect(url_for('.logout'))
    else:
        return redirect(url_for('.profile', username=u.username))

