import sqlite3
import click
from flask import current_app, g
from flask.cli import with_appcontext


def get_db():
    # g是一个特殊的对象，独立于每一个请求，可以用于存储多个函数都会用到数据
    # 把连接存储于其中，可以多次使用，而不用每次调用get_db都创建一个新的
    if 'db' not in g:
        g.db = sqlite3.connect(
            # current_app另一个特殊对象，指向处理请求的Flask应用
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row  # 告诉连接返回类似字典的行，可以通过列名来操作数据

    return g.db


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()


def init_db():
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf-8'))


# 定义一个名为init-db命令行,它调用 init_db 函数，并为用户显示一个成功的消息
@click.command('init_db')
@with_appcontext
def init_db_command():
    init_db()
    click.echo('Initialized the database.')


def init_app(app):
    # 告诉 Flask 在返回响应后进行清理的时候调用此函数。
    app.teardown_appcontext(close_db)
    # 添加一个新的 可以与 flask 一起工作的命令。
    app.cli.add_command(init_db_command)
