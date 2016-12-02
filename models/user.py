from . import ModelMixin
from . import db
from . import timestamp


class User(db.Model, ModelMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String())
    password = db.Column(db.String())
    avatar = db.Column(db.String())
    weibos = db.relationship('Weibo', backref='user', lazy='select', foreign_keys='Weibo.user_id')
    comments = db.relationship('Comment', backref='user', lazy='select', foreign_keys='Comment.user_id')
    like = db.relationship('Like', backref='user', lazy='select', foreign_keys='Like.user_id')
    followed = db.relationship('Follow', backref='followed', lazy='immediate', foreign_keys='Follow.followed_id')
    follower = db.relationship('Follow', backref='follower',  lazy='immediate', foreign_keys='Follow.follower_id')
    fro = db.relationship('Message', backref='sender', lazy='immediate', foreign_keys='Message.sender_id')
    rec = db.relationship('Message', backref='receiver',  lazy='immediate', foreign_keys='Message.receiver_id')

    def __init__(self, form):
        self.username = form.get('username', '')
        self.password = form.get('password', '')
        self.avatar = '/static/img/doge.gif'

    def valid_login(self, u):
        if u is not None:
            username_equals = u.username == self.username
            password_equals = u.password == self.password
            return username_equals and password_equals
        else:
            return False

    # 验证注册用户的合法性的
    def valid(self):
        valid_username = User.query.filter_by(username=self.username).first() == None
        valid_username_len = len(self.username) >= 2
        valid_password_len = len(self.password) >= 2
        msgs = []
        if not valid_username:
            message = '用户名已经存在'
            msgs.append(message)
        elif not valid_username_len:
            message = '用户名长度必须大于等于 6'
            msgs.append(message)
        elif not valid_password_len:
            message = '密码长度必须大于等于 6'
            msgs.append(message)
        status = valid_username and valid_username_len and valid_password_len
        return status, msgs

    # 所有关注者和自己的微博的列表

    # 所有点赞者的名字
    @classmethod
    def like_names(cls, id):
        ws_all = cls.follow_weibo(id)
        name_list = []
        for ws in ws_all:
            for w in ws.like:
                name_list.append(w.username)
        return name_list


class Follow(db.Model, ModelMixin):
    """
    有一个关注者 id
    有一个被关注者 id
    """
    __tablename__ = 'follows'
    id = db.Column(db.Integer, primary_key=True)
    follower_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    followed_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    time = db.Column(db.Integer, default=0)

    def __init__(self):
        self.time = timestamp()


class Message(db.Model, ModelMixin):
    __tablename__ = 'msgs'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String())
    sender_id = db.Column(db.String(), db.ForeignKey('users.id'))
    receiver_id = db.Column(db.String(), db.ForeignKey('users.id'))
    time = db.Column(db.Integer, default=0)

    def __init__(self, content):
        self.content = content
        self.time = timestamp()
