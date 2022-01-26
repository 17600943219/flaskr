import os
from flask import Flask


def create_app(test_config=None):
    # 创建并且配置app
    # __name__是当前模块的名称
    # instance_relative_config=True告诉应用配置文件在instance下
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',  # 保证数据安全的，开发时用dev，发布时使用随机值重载
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),  # SQLite数据库文件的存放路径
    )

    if test_config is None:
        # 使用config.py重载缺省配置，例如正式部署时设置一个正式的SECRET_KEY
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # a simple page that says hello
    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    from . import db
    db.init_app(app)

    from . import auth
    # 导入认证蓝图，包括注册新用户、登录和注销
    app.register_blueprint(auth.bp)

    from . import blog
    app.register_blueprint(blog.bp)
    app.add_url_rule('/', endpoint='index')

    return app



