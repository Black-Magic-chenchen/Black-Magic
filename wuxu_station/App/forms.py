import os

import wtforms
from wtforms.validators import Length, InputRequired

basedir = os.path.abspath(os.path.dirname(__file__))
class RegisterForm(wtforms.Form):
    username = wtforms.StringField(
        validators=[Length(min=3, max=20, message="用户名格式错误")]
    )
    password = wtforms.StringField(
        validators=[Length(min=3, max=20, message="密码格式错误")]
    )
    code = wtforms.StringField(
        validators=[Length(min=4, max=4, message="验证码格式错误")]
    )


class LoginForm(wtforms.Form):
    username = wtforms.StringField(
        validators=[Length(min=3, max=20, message="用户名格式错误")]
    )
    password = wtforms.StringField(
        validators=[Length(min=3, max=20, message="密码格式错误")]
    )


class adviceForm(wtforms.Form):
    content = wtforms.StringField(
        validators=[Length(min=3, max=100, message="长度错误")]
    )
    telephone = wtforms.StringField(
        validators=[Length(min=11, max=11, message="手机号码格式错误")]
    )


class ForumForm(wtforms.Form):
    content = wtforms.StringField(
        validators=[Length(min=1, max=2000, message="输入不符合要求！")]
    )


class AnswerForm(wtforms.Form):
    content = wtforms.StringField(
        validators=[Length(min=1, max=2000, message="输入不符合要求！")]
    )
    author_id = wtforms.IntegerField(
        validators=[InputRequired(message="必须传入问题id")]
    )
