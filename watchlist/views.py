"""视图函数"""
from flask import url_for, render_template, request, redirect, flash
from flask_login import login_user, login_required, logout_user, current_user        # 导入用户认证扩展类

from watchlist import app, db
from watchlist.models import User, Movie

@app.route('/', methods=['GET', 'POST'])        # methods表示同时接受GET和POST请求，否则默认只接受GET请求
def index():
    """主页"""
    # 新增电影条目
    if request.method == 'POST':                # 判断是否是POST请求
        if not current_user.is_authenticated:   # 如果当前用户未认证/登录
            return redirect(url_for('index'))   # 重定向回主页(未登录不能使用增加条目功能)
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

    # 显示电影列表
    movies = Movie.query.all()                  # 读取所有电影记录
    return render_template('index.html', movies=movies)

@app.route('/movie/edit/<int:movie_id>', methods=['GET', 'POST'])
@login_required     # 用于视图保护,将未登录用户拒之门外
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
@login_required     # 用于视图保护,将未登录用户拒之门外
def delete(movie_id):
    """只相应删除电影条目按钮的操作，无单独页面"""
    movie = Movie.query.get_or_404(movie_id)    # 获取电影记录
    db.session.delete(movie)                    # 删除对应的记录
    db.session.commit()                         # 提交数据库会话
    flash('Item deleted.')
    return redirect(url_for('index'))           # 重定向回主页

@app.route('/login', methods=['GET', 'POST'])
def login():
    """登录"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if not username or not password:
            flash('Invalid input.')
            return redirect(url_for('login'))

        user = User.query.first()
        # 验证用户名和密码是否一致
        if username == user.username and user.validate_password(password):
            login_user(user)                    # 登录用户
            flash('Login success.')
            return redirect(url_for('index'))   # 重新定向到主页

        flash('Invalid username or password.')  # 如果验证失败，显示错误信息
        return redirect(url_for('login'))       # 重定向回登录页面

    return render_template('login.html')

@app.route('/logout')
@login_required     # 用于视图保护,将未登录用户拒之门外
def logout():
    """注销/登出"""
    logout_user()   # 登出用户
    flash('Goodbye.')
    return redirect(url_for('index'))           # 重定向回主页

@app.route('/settings', methods=['GET', 'POST'])
@login_required     # 用于视图保护,将未登录用户拒之门外
def settings():
    """设置界面，设置用户名字（昵称）"""
    if request.method == 'POST':
        name = request.form['name']

        if not name or len(name) >20:
            flash('Invalid input.')
            return redirect(url_for('settings'))

        current_user.name = name
        # current_user 会返回当前登录用户的数据库记录对象
        # 等同于下面的用法
        # user = User.query.first()
        # user.name = name
        db.session.commit()
        flash('Settings updated.')
        return redirect(url_for('index'))

    return render_template('settings.html')