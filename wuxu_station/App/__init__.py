import logging

from flask import Flask
from App.views.views import blog,api
from .views.views_admin import admin
from .exts import  init_exts



def createApp():
  app = Flask(__name__)
  # 注册蓝图
  app.register_blueprint(blueprint=blog)#前端静态页面
  app.register_blueprint(blueprint=admin)#后台管理
  app.register_blueprint(blueprint=api)#图片验证码
  # 配置数据库
  db_uri = 'mysql+pymysql://root:20040606sht@localhost:3306/station'
  app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
  app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
  app.config['SECRET_KEY'] ='123456'

  app.logger.setLevel(logging.INFO)

  handler = logging.FileHandler('flask.log')
  handler.setLevel(logging.INFO)

  formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(filename)s - %(funcName)s - %(lineno)s - %(message)s')
  handler.setFormatter(formatter)

  app.logger.addHandler(handler)

  init_exts(app)
  return app