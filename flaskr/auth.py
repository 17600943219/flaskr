import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.db import get_db

# url_prefix 会添加到所有与该蓝图关联的 URL 前面
bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        if not username:
            error = '用户名不能为空。'
        elif not password:
            error = '密码不能为空。'

        if error is None:
            try:
                db.execute(
                    # 占位符可以代替后面的元组参数中相应的值。使 用占位符的好处是会自动帮你转义输入值，以抵御 SQL 注入攻击 。
                    "INSERT INTO user (username, password) VALUES (?, ?)", (username, generate_password_hash(password))
                )
                db.commit()
            except db.IntegrityError:
                error = f"{username} 已经注册过。"
            else:
                return redirect(url_for("auth.login"))
        # 用于储存在渲染模块时可以调用的信息。
        flash(error)

    return render_template('auth/register.html')


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()

        if user is None:
            error = '用户名错误。'
        elif not check_password_hash(user['password'], password):
            error = '密码错误。'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('index'))

        flash(error)
    return render_template('auth/login.html')


@bp.before_app_request
def load_logged_in_user():
    """
    bp.before_app_request() 注册一个 在视图函数之前运行的函数，不论其 URL 是什么。
    load_logged_in_user 检查用户 id 是否已经储存在 session 中，并从数据库中获取用户数据，
    然后储存在 g.user 中。 g.user 的持续时间比请求要长。 如果没有用户 id ，或者 id 不存在，那么 g.user 将会是 None 。
    """
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()


@bp.route('/logout')
def logout():
    """注销的时候需要把用户 id 从 session 中移除。 然后 load_logged_in_user 就不会在后继请求中载入用户了。"""
    session.clear()
    return redirect(url_for('index'))


def login_required(view):
    """
    装饰器返回一个新的视图，该视图包含了传递给装饰器的原视图。新的函数检查用户 是否已载入。如果已载入，
    那么就继续正常执行原视图，否则就重定向到登录页面。 我们会在博客视图中使用这个装饰器。
    """
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        return view(**kwargs)

    return wrapped_view
