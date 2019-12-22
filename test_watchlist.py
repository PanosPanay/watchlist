import unittest

from app import app, db, Movie, User, forge, initdb


class WatchlistTestCase(unittest.TestCase):
    def setUp(self):
        """测试固件，在每个测试方法执行前被调用"""
        # 更新配置
        app.config.update(
            TESTING=True,                   # 开启测试模式（出错时不会输出多于欣喜）
            SQLALCHEMY_DATABASE_URI='sqlite:///:memory:'    # 使用SQLite内存型数据库，不会干扰开发时使用的数据库文件，且速度更快
        )

        # 创建数据库和表
        db.create_all()

        # 创建测试数据，一个用户，一个电影条目
        user = User(name='Test', username='test')
        user.set_password('123')
        movie = Movie(title='Test Movie Title', year='2019')

        # 使用add_all()方法一次添加多个模型类实例，传入列表
        db.session.add_all([user, movie])
        db.session.commit()

        self.client = app.test_client()     # 创建测试客户端，用来模拟客户端请求
        self.runner = app.test_cli_runner() # 创建测试命令运行器，用来触发自定义命令

    def tearDown(self):
        """测试固件，在每个测试方法执行后被调用"""
        db.session.remove()                 # 清除数据库会话
        db.drop_all()                       # 删除数据库表

    def login(self):
        """辅助方法，用于登录用户"""
        self.client.post('/login', data=dict(   # 以字典形式传入POST请求数据
            username='test',
            password='123'
        ), follow_redirects=True)           # 将 follow_redirects 参数设为 True 可以跟随重定向，最终返回的会是重定向后的响应

    # 以下为测试方法(test_...)。在测试方法中使用断言来判断(assert...)程序功能是否正常
    # 测试程序的各个视图函数

    def test_app_exist(self):
        """测试程序实例是否存在"""
        self.assertIsNotNone(app)

    def test_app_is_testing(self):
        """测试程序是否处于测试模式"""
        self.assertTrue(app.config['TESTING'])

    def test_404_page(self):
        """测试404页面"""
        response = self.client.get('/nothing')      # 对测试客户端self.clent调用get()方法相当于浏览器向服务器发送GET请求
        data = response.get_data(as_text=True)      # get_data()方法把as_test参数设为True可以获取Unicode格式的响应主体
        # 判断响应主体是否包含预期内容来测试程序是否正常工作，即应与实际html内容一致
        self.assertIn('Page Not Found - 404', data) 
        self.assertIn('Go Back to Index', data)     # 判断404页面响应是否包含Go Back
        self.assertEqual(response.status_code, 404) # 判断响应状态码

    def test_index_page(self):
        """测试主页"""
        response = self.client.get('/')
        data = response.get_data(as_text=True)
        self.assertIn('Test\'s Watchlist', data)    # 判断主页响应是否包含Test's Watchlist
        self.assertIn('Test Movie Title', data)
        self.assertEqual(response.status_code, 200)

    def test_create_item(self):
        """测试创建条目"""
        self.login()

        # 测试正常创建条目操作
        response = self.client.post('/', data=dict(
            title='New Movie',
            year='2019'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Item created.', data)
        self.assertIn('New Movie', data)

        # 测试创建条目操作，但电影标题为空
        response = self.client.post('/', data=dict(
            title='',
            year='2019'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Item created.', data)
        self.assertIn('Invalid input.', data)

        # 测试创建条目操作，但电影年份为空
        response = self.client.post('/', data=dict(
            title='New Movie',
            year=''
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Item created.', data)
        self.assertIn('Invalid input.', data)

    def test_update_item(self):
        """测试更新条目"""
        self.login()

        # 测试更新页面
        response = self.client.get('/movie/edit/1')
        data = response.get_data(as_text=True)
        self.assertIn('Edit item', data)
        self.assertIn('Test Movie Title', data)
        self.assertIn('2019', data)

        # 测试更新条目操作
        response = self.client.post('/movie/edit/1', data=dict(
            title='New Movie Edited',
            year='2019'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Item updated.', data)
        self.assertIn('New Movie Edited', data)

        # 测试更新条目操作，但电影标题为空
        response = self.client.post('/movie/edit/1', data=dict(
            title='',
            year='2019'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Item updated.', data)
        self.assertIn('Invalid input.', data)

        # 测试更新条目操作，但电影年份为空
        response = self.client.post('/movie/edit/1', data=dict(
            title='New Movie Edited Again',
            year=''
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Item updated.', data)
        self.assertIn('Invalid input.', data)
    
    def test_delete_item(self):
        """测试删除条目"""
        self.login()

        response = self.client.post('/movie/delete/1', follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Item deleted.', data)
        self.assertNotIn('Test Movie Title', data)

    def test_login_protect(self):
        """测试登录保护"""
        response = self.client.get('/')
        data = response.get_data(as_text=True)
        self.assertNotIn('Logout', data)
        self.assertNotIn('Settings', data)
        self.assertNotIn('<form method="post">', data)
        self.assertNotIn('删除', data)
        self.assertNotIn('编辑', data)

    def test_login(self):
        """测试登录"""
        response = self.client.post('/login', data=dict(
            username='test',
            password='123'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Login success.', data)
        self.assertIn('Logout', data)
        self.assertIn('Settings', data)
        self.assertIn('删除', data)
        self.assertIn('编辑', data)
        self.assertIn('<form method="post">', data)

        # 测试使用错误的密码登录
        response = self.client.post('/login', data=dict(
            username='test',
            password='456'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Login success.', data)
        self.assertIn('Invalid username or password.', data)

        # 测试使用空用户名登录
        response = self.client.post('/login', data=dict(
            username='',
            password='123'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Login success.', data)
        self.assertIn('Invalid input.', data)

        # 测试使用空密码登录
        response = self.client.post('/login', data=dict(
            username='test',
            password=''
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Login success.', data)
        self.assertIn('Invalid input.', data)

    def test_logout(self):
        """测试登出"""
        self.login()

        response = self.client.get('/logout', follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Goodbye.', data)
        self.assertNotIn('Logout', data)
        self.assertNotIn('Settings', data)
        self.assertNotIn('删除', data)
        self.assertNotIn('编辑', data)
        self.assertNotIn('<form method="post">', data)

    def test_settings(self):
        """测试设置"""
        self.login()

        # 测试设置页面
        response = self.client.get('/settings')
        data = response.get_data(as_text=True)
        self.assertIn('Settings', data)
        self.assertIn('Your Name', data)
       
        # 测试更新设置
        response = self.client.post('/settings', data=dict(
            name='宝刚',
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Settings updated.', data)
        self.assertIn('宝刚', data)

        # 测试更新设置，但名称为空
        response = self.client.post('/settings', data=dict(
            name='',
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Settings updated.', data)
        self.assertIn('Invalid input.', data)
    
    # 测试自定义命令

    def test_forge_command(self):
        """测试虚拟数据"""
        result = self.runner.invoke(forge)
        self.assertIn('Done.', result.output)
        self.assertNotEqual(Movie.query.count(), 0)

    def test_initdb_command(self):
        """测试初始化数据库"""
        result = self.runner.invoke(initdb)
        self.assertIn('Initialized database.', result.output)

    def test_admin_command(self):
        """测试生成管理员账户"""
        db.drop_all()
        db.create_all()
        result = self.runner.invoke(args=['admin', '--username', 'baogang', '--password', '123'])
        self.assertIn('Creating user...', result.output)
        self.assertIn('Done.', result.output)
        self.assertEqual(User.query.count(), 1)
        self.assertEqual(User.query.first().username, 'baogang')
        self.assertTrue(User.query.first().validate_password('123'))

    def test_admin_command_update(self):
        """测试更新管理员账户"""
        # 使用args参数给出完整的命令参数列表
        result = self.runner.invoke(args=['admin', '--username', 'updatedName', '--password', '456'])
        self.assertIn('Updating user...', result.output)
        self.assertIn('Done.', result.output)
        self.assertEqual(User.query.count(), 1)
        self.assertEqual(User.query.first().username, 'updatedName')
        self.assertTrue(User.query.first().validate_password('456'))


if __name__ == '__main__':
    unittest.main()