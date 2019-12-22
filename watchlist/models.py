"""模型类"""
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from watchlist import db

# 创建数据库模型
class User(db.Model, UserMixin):   # 表名将会是 user （自动生成，小写处理）
    id = db.Column(db.Integer, primary_key=True)    # 主键
    name = db.Column(db.String(20))                 # 用户昵称
    username = db.Column(db.String(20))             # 用户名
    password_hash = db.Column(db.String(128))       # 密码散列值

    def set_password(self, password):
        """设置密码
        :param password: 待设置密码
        """
        self.password_hash = generate_password_hash(password)

    def validate_password(self, password):
        """验证密码
        :param password: 待验证的密码
        """
        return check_password_hash(self.password_hash, password)

class Movie(db.Model):  # 表名将会是 movie
    id = db.Column(db.Integer, primary_key=True)    # 主键
    title = db.Column(db.String(60))                # 电影标题
    year = db.Column(db.String(4))                  # 电影年份