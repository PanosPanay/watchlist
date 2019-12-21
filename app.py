import os
import sys
from flask import Flask, url_for, render_template, request, redirect, flash
from flask_sqlalchemy import SQLAlchemy     # 导入 Flask-SQLAlchemy 扩展类
import click

# sqlite:///数据库文件的绝对地址，若不是WINDOWS系统，表示为sqlite:////
WIN = sys.platform.startswith("win")
if WIN:     # 如果是Windows系统，使用3个斜线
    prefix = 'sqlite:///'
else:       # 否则使用4个斜线
    prefix = 'sqlite:////'

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev'    # flash消息签名所需的密钥，等同于app.secret_key = 'dev'
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
    db.session.add(user)                        # 添加到数据库会话
    for m in movies:
        movie = Movie(title=m['title'], year=m['year'])
        db.session.add(movie)                   # 添加到数据库会话

    db.session.commit()                         # 提交数据库会话
    click.echo('Done.')                         # 输出提示信息


@app.context_processor
def inject_user():  # 函数名可以随意修改
    """模板上下文处理函数"""
    user = User.query.first()
    return dict(user=user)  # 需要返回字典，等同于return {'user': user}
    # 这个函数返回的变量（以字典键值对的形式）将会统一注入到每一个模板的上下文环境中，因此可以直接在模板中使用

@app.errorhandler(404)      # 传入要处理的错误代码
def page_not_found(e):      # 接受异常对象作为参数
    return render_template('404.html'), 404  # 返回模板和状态码

@app.route('/', methods=['GET', 'POST'])        # methods表示同时接受GET和POST请求，否则默认只接受GET请求
def index():
    """主页"""
    if request.method == 'POST':                # 判断是否是POST请求
        # 获取表单数据
        title = request.form.get('title')       # request.form是一个特殊的字典
        year = request.form.get('year')
        # 验证数据
        if not title or not year or len(year) > 4 or len(title) > 60:
            # flash() 函数用来在视图函数里向模板传递提示消息，get_flashed_messages() 函数则用来在模板中获取提示消息
            flash('Invalid input.') # 显示错误提示
            return redirect(url_for('index'))   # 重定向回主页
        # 保存表单数据到数据库
        movie = Movie(title=title, year=year)   # 创建记录
        db.session.add(movie)                   # 添加到数据库会话
        db.session.commit()                     # 提交数据库会话
        flash('Item created.')                  # 显示成功创建的提示
        return redirect(url_for('index'))       # 重定向回主页

    movies = Movie.query.all()                  # 读取所有电影记录
    return render_template('index.html', movies=movies)

@app.route('/movie/edit/<int:movie_id>', methods=['GET', 'POST'])
def edit(movie_id):
    """编辑电影条目页面"""
    movie = Movie.query.get_or_404(movie_id)    # 获取待更新的电影记录

    if request.method == 'POST':                # 处理编辑表单的提交请求
        title = request.form['title']
        year = request.form['year']

        if not title or not year or len(year) > 4 or len(title) > 60:
            flash('Invalid input.')
            return redirect(url_for('edit', movie_id=movie_id))     # 重定向回对应的编辑页面

        movie.title = title                     # 更新标题
        movie.year = year                       # 更新年份
        db.session.commit()                     # 提交数据库会话
        flash('Item updated.')
        return redirect(url_for('index'))       # 重定向回主页

    return render_template('edit.html', movie=movie)    # 传入被编辑的电影记录

@app.route('/movie/delete/<int:movie_id>', methods=['POST'])    # 限定只接受POST请求
def delete(movie_id):
    """只相应删除电影条目按钮的操作，无单独页面"""
    movie = Movie.query.get_or_404(movie_id)    # 获取电影记录
    db.session.delete(movie)                    # 删除对应的记录
    db.session.commit()                         # 提交数据库会话
    flash('Item deleted.')
    return redirect(url_for('index'))           # 重定向回主页


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