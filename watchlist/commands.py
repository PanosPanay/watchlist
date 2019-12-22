"""命令函数"""
import click

from watchlist import app, db
from watchlist.models import User, Movie

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

@app.cli.command()
@click.option('--username', prompt=True, help='The username used to login.')
@click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True, help='The password used to login.') # hide_input=True会让密码输入隐藏，confirmation_prompt=True要求二次确认输入
def admin(username, password):
    """生成管理员账户
    命令行中执行命令,eg.  flask admin --username baogang --password 123
    """
    db.create_all()

    user = User.query.first()
    if user is not None:
        click.echo('Updating user...')
        user.username = username
        user.set_password(password)
    else:
        click.echo('Creating user...')
        user = User(username=username, name='Admin')
        user.set_password(password)
        db.session.add(user)

    db.session.commit()
    click.echo('Done.')