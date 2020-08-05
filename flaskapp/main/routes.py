from flask import render_template, request, Blueprint
from flaskapp.models import Post
from flask_login import current_user
from flask_socketio import SocketIO, send, emit, join_room, leave_room
from flaskapp import socketio
from flask_mobility.decorators import mobile_template

main = Blueprint('main', __name__)

@main.route("/")
@main.route('/home')
def view():
    return render_template("fgl_home.html")

@main.route('/posts')
def home():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=10)
    return render_template("posts.html", posts=posts)

@main.route("/test")
def test():
    return render_template("FGL_Layout.html")

@socketio.on('message')
def handleMessage(msg):
    print('Message: ' + msg)
    send(msg, broadcast=True)
