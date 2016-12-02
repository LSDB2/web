from routes import *
from models.user import *
main = Blueprint('weibo', __name__)

pyid = id
Model = Weibo


@main.route('/all/<int:page>')
def index_all(page):
    u = current_user()
    ws_all = Weibo.query.filter(Weibo.username != u.username).all()
    # 查询 非当前用户的微博
    # ws = Weibo.query.all()
    ws, page_list = per_page(ws_all)
    if len(ws) > 0:
        w = ws[page - 1]
    else:
        w = []
    return render_template('weibo_all.html', user=u, ws=w, page=page_list,p_page=page)


@main.route('/<username>/<int:page>')
@login_required
def index(username, page):
    uid = current_user().id
    # msg = Message.query.filter_by(receiver_id=uid).all()
    u = User.query.filter_by(username=username).first()
    print('u', u)
    print('uid == u.id:', uid == u.id)
    if uid == u.id:
        ws_all = Weibo.follow_weibo(u.id)
        print('ws_all', ws_all)
        ws, page_list = per_page(ws_all)
        print('ws', ws, page_list)
        if len(ws) > 0:
            w = ws[page-1]
        else:
            w = []
        return render_template('weibo_index.html',weibo_list=w,user=u,page=page_list,
                               p_page=page)
    return abort(404)


@main.route('/all/<username>/<int:page>')
@login_required
def user_all(username, page):
    uid = current_user().id
    # msg = Message.query.filter_by(receiver_id=uid).all()
    u = User.query.filter_by(username=username).first()
    if uid == u.id:
        # username的所有微博
        ws_all = u.weibos[::-1]
        ws, page_list = per_page(ws_all)
        if len(ws) > 0:
            w = ws[page - 1]
        else:
            w = []
        return render_template('user_weibo.html',
                               weibo_list=w,
                               user=u,
                               page=page_list,
                               p_page=page)
    print('非当前用户')
    return abort(404)


@main.route('/edit/<int:id>')
@login_required
def edit(id):
    w = Weibo.query.filter_by(id=id).first()
    uid = current_user().id
    if w.user_id == uid:
        return render_template('weibo_edit.html', weibo=w)
    return abort(404)


@main.route('/add', methods=['POST'])
@login_required
def add():
    u = current_user()
    print('u', u)
    form = request.form
    w = Weibo(form)
    w.username = u.username
    w.avatar = u.avatar
    w.user_id = u.id
    w.save()
    print('w', w)
    return redirect(url_for('.index', username=u.username, page=1))


@main.route('/update/<int:id>', methods=['POST'])
@login_required
def update(id):
    u = current_user()
    form = request.form
    w = Weibo.query.filter_by(id=id).first()
    w.content = form.get('content')
    w.save()
    # Weibo.query.filter_by() 生成的是一个SQL查询语句, 没有 save()方法
    # 必须是返回的查询结果 才有这个方法
    return redirect(url_for('.user_all', username=u.username, page=1))


@main.route('/delete/<id>')
@login_required
def delete(id):
    u = current_user()
    w = Weibo.query.filter_by(id=id).first()
    w.delete()
    return redirect(url_for('.user_all', username=u.username, page=1))


@main.route('/addcomment/<weibo_id>', methods=['POST'])
@login_required
def addcomment(weibo_id):
    u = current_user()
    form = request.form
    sign = form.get('sign','')
    c = Comment(form)
    c.user_id = u.id
    c.username = u.username
    c.weibo_id = weibo_id
    c.save()
    if sign:
        return redirect(url_for('.index', username=c.username, page=1))
    return redirect(url_for('.index_all'))


@main.route('/like/<weibo_id>', methods=['POST'])
@login_required
def like(weibo_id):
    u = current_user()
    like_user = Weibo.weibo_likes_name(weibo_id)
    if u.username in like_user:
        dislike(weibo_id)
    else:
        form = request.form
        l = Like(form)
        # 需要手动将 user_id 传入
        w = Weibo.query.get(weibo_id)
        l.user_id = u.id
        l.username = u.username
        l.weibo_id = weibo_id
        if l.username != w.username:
            l.save()
    return redirect(url_for('.index', username=u.username, page=1))


def dislike(weibo_id):
    u = current_user()
    ls = Like.query.filter_by(weibo_id=weibo_id).all()
    l_id = ''
    for l in ls:
        if l.user_id == u.id:
            l_id = l.id
            break
    n = Like.query.get(l_id)
    n.delete()
    return redirect(url_for('.index', username=u.username, page=1))