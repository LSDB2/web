from routes import *


main = Blueprint('weibo', __name__)

pyid = id
Model = Weibo


@main.route('/all')
def index_all():
    u = current_user()
    ws = Weibo.query.filter(Weibo.username != u.username).all()
    # 查询 非当前用户的微博
    # ws = Weibo.query.all()
    print('其他人微博', ws)
    for w in ws:
        weibo_num = len(w.comment)
        print('评论', w.comment)
    return render_template('weibo_all.html', comments_num=weibo_num, username=u.username, ws=ws)


@main.route('/<username>')
@login_required
def index(username):
    u = User.query.filter_by(username=username).first()
    ws = Weibo.query.filter_by(user_id=u.id).all()
    return render_template('weibo_index.html', weibo_list=ws, user=u.username)


@main.route('/edit/<int:id>')
@login_required
def edit(id):
    w = Weibo.query.filter_by(id=id).first()
    return render_template('weibo_edit.html', weibo=w)


@main.route('/add', methods=['POST'])
@login_required
def add():
    u = current_user()
    form = request.form
    w = Weibo(form)
    # 需要手动将 user_id 传入
    w.user_id = u.id
    w.username = u.username
    w.save()
    # ws = Weibo.query.all()
    # print('已存', ws)
    return redirect(url_for('.index', username=u.username))


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
    return redirect(url_for('.index', username=u.username))


@main.route('/delete/<id>')
@login_required
def delete(id):
    u = current_user()
    w = Weibo.query.filter_by(id=id).first()
    w.delete()
    return redirect(url_for('.index', username=u.username))


@main.route('/addcomment/<weibo_id>', methods=['POST'])
@login_required
def addcomment(weibo_id):
    u = current_user()
    form = request.form
    c = Comment(form)
    # 需要手动将 user_id 传入
    c.user_id = u.id
    c.username = u.username
    c.weibo_id = weibo_id
    c.save()
    print('已存', Comment.query.all())
    return redirect(url_for('.index_all'))