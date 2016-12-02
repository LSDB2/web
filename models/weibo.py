from . import ModelMixin
from . import db
from . import timestamp
from .user import User, Follow


class Weibo(db.Model, ModelMixin):
    __tablename__ = 'weibos'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String())
    created_time = db.Column(db.Integer, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    username = db.Column(db.String())
    comment = db.relationship('Comment', backref='weibo', lazy='select', foreign_keys='Comment.weibo_id')
    like = db.relationship('Like', backref='weibo', lazy='select', foreign_keys='Like.weibo_id')
    avatar = db.Column(db.String())

    def __init__(self, form):
        self.user_id = form.get('user_id')
        self.content = form.get('content', '')
        self.created_time = timestamp()
        self.avatar = User.query.get(self.user_id).avatar

    @classmethod
    def weibo_likes_name(cls, weibo_id):
        ws = Weibo.query.filter_by(id=weibo_id).all()
        name = []
        for w in ws:
            for l in w.like:
                name.append(l.username)
        return name

    @classmethod
    def follow_weibo(cls, id):
        fs = Follow.query.filter_by(follower_id=id).all()
        all_id = [id]
        for f in fs:
            all_id.append(f.followed_id)
        ws_all = []
        for i in all_id:
            ws = Weibo.query.filter_by(user_id=i).order_by(Weibo.created_time.desc()).all()
            for w in ws:
                ws_all.append(w)
        return ws_all


class Comment(db.Model, ModelMixin):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String())
    created_time = db.Column(db.Integer, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    username = db.Column(db.String())
    weibo_id = db.Column(db.Integer, db.ForeignKey('weibos.id'))
    avatar = db.Column(db.String())

    def __init__(self, form):
        self.content = form.get('content', '')
        self.user_id = form.get('user_id')
        self.created_time = timestamp()
        self.avatar = User.query.get(self.user_id).avatar


class Like(db.Model, ModelMixin):
    __tablename__ = 'likes'
    id = db.Column(db.Integer, primary_key=True)
    created_time = db.Column(db.Integer, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    username = db.Column(db.String())
    weibo_id = db.Column(db.Integer, db.ForeignKey('weibos.id'))

    def __init__(self, form):
        self.created_time = timestamp()