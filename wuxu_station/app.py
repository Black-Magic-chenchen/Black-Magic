from App import createApp
from flask import Flask, session, g, request
from App.models.models import UserModel

app = createApp()


@app.before_request
def my_before_request():
    user_id = request.cookies.get("user_id")
    if user_id:
        user = UserModel.query.get(user_id)
        setattr(g, "user", user)
    else:
        setattr(g, "user", None)


@app.context_processor
def my_context_processor():
    return {"user": g.user}


if __name__ == "__main__":
    app.run(debug=True)
