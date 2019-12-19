from flask import Flask, url_for

app = Flask(__name__)

@app.route('/')
def hello():
    return '<h1>Hello Totoro!</h1><img src="http://helloflask.com/totoro.gif">'

@app.route('/user/<name>')
def user_page(name):
    return 'User: %s' % name

@app.route('/test')
def test_url_for():
    str = 'Test Page...\n'

    # 下面是一些调用示例（请在命令行窗口中查看输出的URL）:  # 实际上命令行不输出？？？<==在关闭服务或重新加载时会显示
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