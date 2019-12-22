"""包构造文件，创建程序实例"""
import os
import sys
from flask import Flask
from flask_sqlalchemy import SQLAlchemy     # 导入 Flask-SQLAlchemy 扩展类
from flask_login import LoginManager        # 导入用户认证扩展类

# sqlite:///数据库文件的绝对地址，若不是WINDOWS系统，表示为sqlite:////
WIN = sys.platform.startswith("win")
if WIN:     # 如果是Windows系统，使用3个斜线
    prefix = 'sqlite:///'
else:       # 否则使用4个斜线
    prefix = 'sqlite:////'

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev'    # flash消息签名所需的密钥，等同于app.secret_key = 'dev'
# 注意更新这里的路径，把 app.root_path 添加到 os.path.dirname() 中，以便把文件定位到项目根目录
app.config['SQLALCHEMY_DATABASE_URI'] = prefix + os.path.join(os.path.dirname(app.root_path), 'data.db') # 数据库连接地址
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False    # 关闭对模型修改的监控

# 在扩展类实例化前加载配置
db = SQLAlchemy(app)    # 初始化扩展，传入程序实例 app
login_manager = LoginManager(app)   # 初始化Flask-Login

@login_manager.user_loader
def load_user(user_id):
    from watchlist.models import User
    user = User.query.get(int(user_id))         # 用ID作为User魔性的主键查询对应的用户
    return user     # 返回用户对象

login_manager.login_view = 'login'  # 当未登录用户执行被限制的操作，重新定向到登录页面，并显示一个错误提示
# 如果需要的话，可以通过设置 login_manager.login_message 来自定义错误提示消息

@app.context_processor
def inject_user():  # 函数名可以随意修改
    """模板上下文处理函数"""
    from watchlist.models import User
    user = User.query.first()
    return dict(user=user)  # 需要返回字典，等同于return {'user': user}
    # 这个函数返回的变量（以字典键值对的形式）将会统一注入到每一个模板的上下文环境中，因此可以直接在模板中使用

from watchlist import views, errors, commands
