import os
import sys
from flask import Flask, url_for, render_template
from flask_sqlalchemy import SQLAlchemy     # 导入 Flask-SQLAlchemy 扩展类
import click

# sqlite:///数据库文件的绝对地址，若不是WINDOWS系统，表示为sqlite:////
WIN = sys.platform.startswith("win")
if WIN:     # 如果是Windows系统，使用3个斜线
    prefix = 'sqlite:///'
else:       # 否则使用4个斜线
    prefix = 'sqlite:////'

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = prefix + os.path.join(app.root_path, 'data.db') # 数据库连接地址
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False    # 关闭对模型修改的监控

# 在扩展类实例化前加载配置
db = SQLAlchemy(app)    # 初始化扩展，传入程序实例 app


# 创建数据库模型
class User(db.Model):   # 表名将会是 user （自动生成，小写处理）
    id = db.Column(db.Integer, primary_key=True)    # 主键
    name = db.Column(db.String(20))                 # 用户名字

class Movie(db.Model):  # 表名将会是 movie
    id = db.Column(db.Integer, primary_key=True)    # 主键
    title = db.Column(db.String(60))                # 电影标题
    year = db.Column(db.String(4))                  # 电影年份


# 自定义命令，用来自动执行创建数据库表操作
@app.cli.command()                                  # 注册为命令
@click.option('--drop', is_flag=True, help='Create after drop.')    # 设置选项
def initdb(drop):
    """初始化数据库
    命令行中执行命令 flask initdb 或 flask initdb --drop"""
    if drop:                                        # 判断是否输入了选项
        db.drop_all()
    db.create_all()
    click.echo('Initialized database.')             # 输出提示信息

@app.cli.command()
def forge():
    """生成虚拟数据
    命令行中执行命令  flask forge """
    db.create_all()

    name = '良多'
    movies = [
        {'title': '霸王别姬', 'year': '1993'},
        {'title': '重庆森林', 'year': '1994'},
        {'title': '花样年华', 'year': '2000'},
        {'title': '蓝宇', 'year': '2001'},
        {'title': '孽子', 'year': '2003'},
        {'title': '色，戒', 'year': '2007'},
        {'title': '欲盖弄潮', 'year': '2007'},
        {'title': '步履不停', 'year': '2008'},
        {'title': '机器人总动员', 'year': '2008'},
        {'title': '触不可及', 'year': '2011'},
        {'title': '万箭穿心', 'year': '2012'},
        {'title': '烈日灼心', 'year': '2015'},
        {'title': '驴得水', 'year': '2016'},
        {'title': '完美陌生人', 'year': '2016'},
        {'title': '看不见的客人', 'year': '2016'},
        {'title': '请以你的名字呼唤我', 'year': '2017'},
        {'title': '谁先爱上他的', 'year': '2018'},
        {'title': '白蛇：缘起', 'year': '2019'},
        {'title': '罗小黑战记', 'year': '2019'},
    ]

    user = User(name=name)
    db.session.add(user)
    for m in movies:
        movie = Movie(title=m['title'], year=m['year'])
        db.session.add(movie)

    db.session.commit()
    click.echo('Done.')                         # 输出提示信息

@app.route('/')
def index():
    user = User.query.first()                       # 读取用户记录
    movies = Movie.query.all()                      # 读取所有电影记录
    return render_template('index.html', user=user, movies=movies)

@app.route('/user/<name>')
def user_page(name):
    return 'User: %s' % name

@app.route('/test')
def test_url_for():
    str = 'Test Page...\n'

    # 下面是一些调用示例（请在命令行窗口中查看输出的 URL）:  # 实际上命令行不输出？？？<==在关闭服务或重新加载时会显示
    # print(url_for('hello'))                     # 输出：/
    str += url_for('hello')
    str += '\n'

    # print(url_for('user_page', name='baogang')) # 输出：/user/baogang
    # print(url_for('user_page', name='hanpi'))   # 输出：/user/hanpi
    str += url_for('user_page', name='baogang')
    str += '\n'
    str += url_for('user_page', name='hanpi')
    str += '\n'

    # 传入了多于的关键字参数，会被当作查询字符串附加到URL后面
    # print(url_for('test_url_for', num=2))       # 输出：/test?num=2
    str += url_for('test_url_for', num=2)
    str += '\n'

    # return 'Test Page...'
    return str