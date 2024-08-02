from flask import Blueprint, render_template, request, redirect
from functools import wraps
from pathlib import Path
from werkzeug.utils import secure_filename
from App.forms import basedir
from App.models.models_admin import *
from App.models.models import *
from werkzeug.security import generate_password_hash

admin = Blueprint('admin', __name__)


# 装饰器：登录验证
def login_required(fn):
    @wraps(fn)
    def inner(*args, **kwargs):
        user_id = request.cookies.get('admin_user_id', None)
        if user_id:
            # 登陆过进入后台管理系统
            user = AdminUserModel.query.get(user_id)
            request.user = user
            return fn(*args, **kwargs)
        else:
            # 没有登录过，返回登录界面
            return redirect('/admin/login/')

    return inner


# 后台管理登录
@admin.route('/admin/login/', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'GET':
        return render_template(('admin/login.html'))
    elif request.method == 'POST':
        username = request.form.get('username')
        userpwd = request.form.get('userpwd')

        user = AdminUserModel.query.filter_by(name=username, passwd=userpwd).first()
        if user:
            response = redirect('/admin/index/')
            response.set_cookie('admin_user_id', str(user.id))
            return response

        else:
            return 'Login Failed'


# 后台管理首页
@admin.route('/admin/index/')
@login_required
def admin_index():
    admin_user_id = request.cookies.get('admin_user_id')
    user = AdminUserModel.query.filter_by(id=admin_user_id).first()
    users = UserModel.query.count()
    articles=Forum.query.count()
    return render_template('admin/index.html', username=user.name, users=users,articles=articles)

@admin.route('/admin/user/')
@login_required
def admin_user():
    users = UserModel.query.all()
    return render_template('admin/user.html',users=users)




@admin.route('/admin/add/', methods=['GET', 'POST'])
@login_required
def admin_add():
    if request.method == 'POST':
        username = request.form.get('name')
        password = request.form.get('password')
        user_add = UserModel()
        user_add.username = username
        user_add.password = generate_password_hash(password)

        try:
            db.session.add(user_add)
            db.session.commit()
        except Exception as e:
            print(e)
            db.session.rollback()
        return redirect('/admin/index/')
    else:
        return '请求方式错误'

@admin.route('/admin/update/<id>', methods=['GET', 'POST'])
@login_required
def admin_update(id):
    if request.method == 'GET':
        user_update = UserModel.query.get(id)
        return render_template('admin/user_update.html', user_update=user_update, username=request.user.name)
    elif request.method == "POST":
        username = request.form.get('name')
        password = request.form.get('password')
        user_update = UserModel.query.get(id)

        user_update.username = username
        user_update.password = generate_password_hash(password)
        try:
            db.session.commit()
        except Exception as e:
            print(e)
        return redirect('/admin/index/')
    else:
        return '请求方式错误'

@admin.route('/admin/article/')
@login_required
def admin_article():
    forums=Forum.query.all()
    return render_template('admin/article.html',forums=forums)

@admin.route('/admin/change-article/<id>',methods=['GET','POST'])
@login_required
def admin_article_change(id):
    if request.method=='GET':
       content = Forum.query.get(id)

       return render_template('admin/article_update.html',content=content)
    elif request.method == "POST":

            content_upgrade = Forum.query.get(id)
            content_upgrade.content = request.form.get("content")
            file = request.files["file"]
            file2 = request.files.get('file2')



            db.session.commit()
            if file:
                home_path = Path(__file__).parent.parent
                images_path = home_path.joinpath("static/forum_photo")

                filename = secure_filename(file.filename)

                images_fullpath = images_path.joinpath(filename)
                content_upgrade.img = "forum_photo/" + filename
                db.session.commit()
                file.save(images_fullpath)
            if file2:

                file_path = basedir + '/static/video/' + file2.filename
                file2.save(file_path)
                content_upgrade.url=file2.filename
                db.session.commit()

            return redirect("/admin/article")


@admin.route("/admin/article/del/<id>", methods=["GET", "POST"])
@login_required
def forum_del(id):
    content = Forum.query.get(id)
    collects = Collect.query.filter_by(author_id=id).all()
    answers = Answer.query.filter_by(author_id=id).all()
    for collect in collects:
        db.session.delete(collect)
    for answers in answers:
        db.session.delete(answers)
    db.session.delete(content)

    db.session.commit()
    return redirect("/admin/article")

