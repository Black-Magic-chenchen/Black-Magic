from functools import wraps
from pathlib import Path

from flask import (
    Blueprint,
    render_template,
    request,
    url_for,
    redirect,
    session,
    make_response,
    current_app,
)
from werkzeug.utils import secure_filename

from App.models.models import *
from ..forms import  RegisterForm, LoginForm, adviceForm, ForumForm, AnswerForm,basedir
from werkzeug.security import generate_password_hash, check_password_hash

from App.captcha import Captcha
from io import BytesIO

blog = Blueprint("user", __name__)
api = Blueprint("api", __name__)

# 验证码
@api.route("/graph_captcha/")
def graph_captcha():
    text, image = Captcha.gene_graph_captcha()
    session["imageCode"] = text
    out = BytesIO()
    image.save(out, "png")
    out.seek(0)
    resp = make_response(out.read())
    resp.content_type = "image/png"
    return resp


# 装饰器：登录验证
def login_required(fn):
    @wraps(fn)
    def inner(*args, **kwargs):
        user_id = request.cookies.get("user_id", None)
        if user_id:
            # 登陆过进入页面
            users = UserModel.query.get(user_id)
            request.user = users
            return fn(*args, **kwargs)
        else:
            # 没有登录过，返回登录界面
            return redirect("/login")

    return inner


@blog.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("home/login.html")
    else:
        form = LoginForm(request.form)
        if form.validate():
            username = form.username.data
            password = form.password.data
            users = UserModel.query.filter_by(username=username).first()
            if not users:
                print("error")
                return redirect("/login")
            if check_password_hash(users.password, password):
                temp = render_template("home/index.html")
                response = make_response(temp)
                response.set_cookie("user_id", str(users.id))
                return response
            else:
                return "密码错误"

        else:
            print("error")
            return redirect("/login")


@blog.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("home/register.html")
    else:
        form = RegisterForm(request.form)
        if form.validate():
            username = form.username.data
            password = form.password.data
            code = form.code.data
            if code == session["imageCode"]:
                users = UserModel(
                    username=username, password=generate_password_hash(password)
                )
                score = Score(user_name=username)
                db.session.add(users)
                db.session.add(score)
                db.session.commit()
                return redirect(url_for("user.login"))
            else:
                return "验证码错误"

        else:

            return redirect(url_for("user.register"))


@blog.route("/")
def index():
    current_app.logger.info("用户访问主页")
    return render_template("home/index.html")


@blog.route("/forum/detail/<id>")
def forum_detail(id):
    content = Forum.query.get(id)

    return render_template("home/forumdetail.html", content=content)


@blog.route("/forum/answer/del/<id>", methods=["GET", "POST"])
@login_required
def forum_answer_del(id):
    content = Answer.query.get(id)
    author_id = content.author_id
    db.session.delete(content)
    db.session.commit()
    current_app.logger.info("用户删除了一条评论")

    return redirect(url_for("user.forum_detail", id=author_id))

@blog.route('/likes',methods=['POST'])
def likes():
    id = request.form.get("likes")
    forum = Forum.query.filter_by(id=id).first()
    forum.likes=forum.likes+1
    db.session.commit()
    current_app.logger.info("用户点赞了一篇帖子")
    return redirect("/forum")




@blog.route("/forum", methods=["GET", "POST"])
@login_required
def talk():
    if request.method == "GET":
        lists = Forum.query.order_by(Forum.create_time.desc()).all()
        return render_template("home/forumindex.html", lists=lists)
    elif request.method == "POST":
        form = ForumForm(request.form)
        if form.validate():
            content = Forum()
            content.content = form.content.data
            file = request.files["file"]
            file2 = request.files.get('file2')
            content.user_id = request.cookies.get("user_id", None)

            db.session.add(content)
            db.session.commit()
            if file:
                home_path = Path(__file__).parent.parent
                images_path = home_path.joinpath("static/forum_photo")

                filename = secure_filename(file.filename)

                images_fullpath = images_path.joinpath(filename)
                content.img = "forum_photo/" + filename
                db.session.commit()
                file.save(images_fullpath)
            if file2:

                file_path = basedir + '/static/video/' + file2.filename
                file2.save(file_path)
                content.url=file2.filename
                db.session.commit()
            current_app.logger.info("用户发表了一篇文章")
            return redirect("/forum")
        else:
            return redirect("/write")


@blog.route("/forum/answer", methods=["POST"])
@login_required
def forum_answer():
    form = AnswerForm(request.form)
    if form.validate():
        content = Answer()
        content.content = form.content.data
        content.author_id = form.author_id.data
        file = request.files["file"]
        content.speaker_id = request.cookies.get("user_id", None)
        db.session.add(content)
        db.session.commit()
        if file:
            home_path = Path(__file__).parent.parent
            images_path = home_path.joinpath("static/answer_photo")

            filename = secure_filename(file.filename)

            images_fullpath = images_path.joinpath(filename)
            content.img = "answer_photo/" + filename
            db.session.commit()
            file.save(images_fullpath)
        current_app.logger.info("用户发表了一条评论")
        return redirect(url_for("user.forum_detail", id=form.author_id.data))
    else:
        return redirect(url_for("user.forum_detail", id=form.author_id.data))


@blog.route("/forum/personal", methods=["GET", "POST"])
@login_required
def forum_personal():
    if request.method == "GET":
        contents = (
            Forum.query.filter_by(user_id=request.cookies.get("user_id"))
            .order_by(Forum.create_time.desc())
            .all()
        )
        return render_template("home/forumpersonal.html", contents=contents)


@blog.route("/forum/personal/upgrade/<id>", methods=["GET", "POST"])
@login_required
def forum_manage(id):
    if request.method == "GET":
        content = Forum.query.get(id)
        return render_template("home/forumupgrade.html", content=content)
    elif request.method == "POST":
        form = ForumForm(request.form)
        if form.validate():
            content_upgrade = Forum.query.get(id)
            content_upgrade.content = request.form.get("content")
            file = request.files["file"]
            if file:
                home_path = Path(__file__).parent.parent
                images_path = home_path.joinpath("static/answer_photo")

                filename = secure_filename(file.filename)

                images_fullpath = images_path.joinpath(filename)
                content_upgrade.img = "answer_photo/" + filename
                db.session.commit()
                file.save(images_fullpath)
            if(Collect.query.filter_by(author_id=id).first()):
                       collect_upgrade = Collect.query.filter_by(author_id=id).first()
                       collect_upgrade.content = content_upgrade.content
                       collect_upgrade.img = content_upgrade.img
            db.session.commit()
            current_app.logger.info("用户修改了帖子")
            return redirect("/forum/personal")
        else:
            return redirect(url_for("user.forum_manage", id=id))


@blog.route("/forum/personal/del/<id>", methods=["GET", "POST"])
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
    current_app.logger.info("用户删除了帖子")
    return redirect("/forum/personal")


@blog.route("/location")
@login_required
def location():
    return render_template("home/location.html")


@blog.route("/collect", methods=["GET", "POST"])
@login_required
def collect():
    if request.method == "GET":
        collection = (
            Collect.query.filter_by(user_id=request.cookies.get("user_id"))
            .order_by(Collect.author_create.desc())
            .all()
        )
        return render_template("home/forumcollect.html", lists=collection)
    elif request.method == "POST":
        id = request.form.get("collect")
        judge = Collect.query.filter_by(author_id=id).first()

        if judge is None:
            content = Forum.query.get(id)
            collection = Collect()
            collection.user_id = request.cookies.get("user_id", None)
            collection.content = content.content
            collection.img = content.img
            collection.author_create = content.create_time
            collection.author_id = content.id
            collection.url=content.url
            db.session.add(collection)
            db.session.commit()
            current_app.logger.info("用户收藏了一篇帖子")
            return redirect("/collect")
        else:
            return redirect("/forum")


@blog.route("/collect/del/<id>", methods=["GET", "POST"])
@login_required
def collect_del(id):
    content = Collect.query.get(id)
    db.session.delete(content)
    db.session.commit()
    current_app.logger.info("用户删除了一篇收藏")
    return redirect("/collect")


@blog.route("/write")
@login_required
def write():
    if request.method == "GET":
        contents = Forum.query.filter_by(user_id=request.cookies.get("user_id")).all()
        return render_template("home/forumwrite.html", contents=contents)


@blog.route("/user/", methods=["GET", "POST"])
@login_required
def user():
    if request.method == "GET":
        user = UserModel.query.filter_by(id=request.cookies.get("user_id")).first()
        return render_template("home/user.html", user=user)
    else:
        file = request.files["file"]
        users = UserModel.query.filter_by(id=request.cookies.get("user_id")).first()
        users.nicheng = request.form.get("nicheng")
        users.schools = request.form.get("school")
        users.sex = request.form.get("sex")
        users.brief = request.form.get("brief")
        db.session.commit()
        if file:
            home_path = Path(__file__).parent.parent
            images_path = home_path.joinpath("static/photo")

            filename = secure_filename(file.filename)

            images_fullpath = images_path.joinpath(filename)
            users.img = "photo/" + filename
            db.session.commit()
            file.save(images_fullpath)
        current_app.logger.info("用户修改了个人信息")
        return redirect("/user/")


@blog.route("/advice", methods=["GET", "POST"])
@login_required
def advice():
    if request.method == "GET":
        return render_template("home/advice.html")
    else:
        form = adviceForm(request.form)
        if form.validate():
            content = form.content.data
            telephone = form.telephone.data
            advices = Advice()
            advices.content = content
            advices.telephone = telephone
            advices.user_id = request.cookies.get("user_id")
            db.session.add(advices)
            db.session.commit()
            current_app.logger.info("用户提出了建议")
        else:
            return form.errors
        return redirect("/advice")


@blog.route("/knowledge")
def knowledge():
    return render_template("home/knowledge.html")


@blog.route("/抑郁症", methods=["GET", "POST"])
@login_required
def depression():
    if request.method == "GET":
        return render_template("home/抑郁症测试.html")
    else:
        users = UserModel.query.filter_by(id=request.cookies.get("user_id")).first()
        score = request.form.get("my_var")
        test = Score.query.filter_by(user_name=users.username).first()
        test.depress = score
        db.session.commit()

        return redirect("/")


@blog.route("/情绪", methods=["GET", "POST"])
@login_required
def feeling():
    if request.method == "GET":
        return render_template("home/测一测你的情绪.html")
    else:
        users = UserModel.query.filter_by(id=request.cookies.get("user_id")).first()
        score = request.form.get("my_var")
        test = Score.query.filter_by(user_name=users.username).first()
        test.feeling = score
        db.session.commit()

        return redirect("/")


@blog.route("/焦虑", methods=["GET", "POST"])
@login_required
def anxiety():
    if request.method == "GET":
        return render_template("home/焦虑量表.html")
    else:
        users = UserModel.query.filter_by(id=request.cookies.get("user_id")).first()
        score = request.form.get("my_var")
        test = Score.query.filter_by(user_name=users.username).first()
        test.anxiety = score
        db.session.commit()

        return redirect("/")


@blog.route("/苛刻标准", methods=["GET", "POST"])
@login_required
def character():
    if request.method == "GET":
        return render_template("home/苛刻标准性格测试.html")
    else:
        users = UserModel.query.filter_by(id=request.cookies.get("user_id")).first()
        score = request.form.get("my_var")
        test = Score.query.filter_by(user_name=users.username).first()
        test.character = score
        db.session.commit()

        return redirect("/")


@blog.route("/scores")
@login_required
def tubiao():
    users = UserModel.query.filter_by(id=request.cookies.get("user_id")).first()
    test = Score.query.filter_by(user_name=users.username).first()
    return render_template("home/scores.html", test=test)


@blog.route("/video_view")
def video_view():
    url = request.args.get("url")
    return render_template("home/video_view.html", url=url)
