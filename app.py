#!/usr/bin/env python

from flask import Flask, render_template, session, request, url_for, jsonify
from flask_socketio import SocketIO, emit
# from gevent import monkey; monkey.patch_socket()
# import gevent
import os
from pymongo import MongoClient
from functools import wraps

# Set this variable to "threading", "eventlet" or "gevent" to test the
# different async modes, or leave it set to None for the application to choose
# the best option based on installed packages.
async_mode = "threading"

app = Flask(__name__, static_folder="build", static_url_path="", template_folder="")
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=async_mode)
json_path = "./src/data/iec104_server.json"
json_dst = "./src/data/etc/safe/iec104.json"

#datebase clinet
client = MongoClient('localhost', 27017)
user_db = client.safe_protocol.user

users = [
    { 
        "_id" : 1, 
        "username" : "gushenxing", 
        "password" : "gushenxingrocks!", 
        "level" : 1 
    },
    { 
        "_id" : 2, 
        "username" : "panxiao", 
        "password" : "panxiao", 
        "level" : 0 
    },
    { 
        "_id" : 3, 
        "username" : "gaohuifang", 
        "password" : "gaohuifang", 
        "level" : 0 
    },
    { 
        "_id" : 4, 
        "username" : "cenliguang", 
        "password" : "cenliguang", 
        "level" : 0 
    },
    { 
        "_id" : 5, 
        "username" : "guyi", 
        "password" : "guyi", 
        "level" : 1 
    }
]

def deal_with_alert_data(d):
    d1 = d.split("|")
    d2 = [s.split("-") for s in d1]
    return dict(d2)


def main_server(port=5000):
    socketio.run(app, host="0.0.0.0", port=port)

def monitor_server(port=8000):
    import socket
    from select import select
    inputs = []
    s = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
    s.bind(("0.0.0.0", port))
    s.listen(10)
    s.setblocking(False)
    inputs.append(s)
    address = dict()
    while 1:
        rs, ws, es = select(inputs, [], [], 1)
        for r in rs:
            if r is s:
                conn, addr = s.accept()
                print("Client {0} connected !".format(addr))
                address[conn] = addr
                inputs.append(conn)
            else:
                data = r.recv(1024)
                if not data:
                    print("Client {0} disconnected !".format(address[r]))
                    address.pop(r)
                    inputs.remove(r)
                else:
                    d = deal_with_alert_data(data.strip())
                    socketio.emit("alert", d)


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session['username'] is None:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


@app.route('/api/v1.0/users', methods=['GET'])
def get_users():
    return jsonify({'users': users})

@app.route('/api/v1.0/user', methods=['POST', 'GET'])
def get_user():
    username = request.args['username']
    user = user_db.find_one({'username': username})
    user = {
        'username': user['username'],
        'password': user['password'],
        'level': user['level']
    }
    print(user)
    return jsonify({'users': user})


@app.route("/")
def index():
    print('Terminal: index')
    return render_template('./src/index.html', async_mode=socketio.async_mode)

# @app.route("/s", methods=['POST'])
# def monitor():
#     data = json.loads(request.form.get('data'))
#     # d = deal_with_alert_data(data.strip())
#     socketio.emit("alert", data)



@app.route("/check", methods=['POST', 'GET'])
def check():
    print('Terminal: login')
    return render_template('./src/index.html')
    # if request.method == 'POST':
    #     username = request.args['username']
    #     password = request.args['password']
    #    
    #     user = user_db.find_one({'username': username})
    #     if request.args['password'] == password :
    #         session['username'] = username
    #         session['password'] = password

    #     else:
    #         session['username'] = None
    #         session['password'] = None
    #         error = 'Invalid username/password'
    #         # return render_template('login.html', error=error)


def deal_with_file(dst=json_dst):
    cmd = "cp " + json_path + " " + dst
    # print(cmd)
    os.system(cmd)


@socketio.on("setting")
def receive_json(data):
    try:
        with open(json_path, "w") as f:
            f.write(data["json"])
        deal_with_file()
        print("Receive json file")
        socketio.emit("setting", "Success!")
    except:
        socketio.emit("setting", "Failed!")
        print("Writing file error!")
    # print(data)


@socketio.on('connect')
def test_connect():
    print("Terminal: Client connected!")
    try:
        with open(json_path, "r") as f:
            d = f.read()
            socketio.emit("init", {"json": d})
    except:
        socketio.emit("init", {"json": "{}"})
        print("Loading file error!")


@socketio.on('disconnect')
def test_disconnect():
    print('Terminal: Client disconnected', request.sid)


if __name__ == '__main__':
    import threading
    # t1 = gevent.spawn(main_server)
    # t2 = gevent.spawn(monitor_server)
    t1 = threading.Thread(target=main_server, args=())
    t2 = threading.Thread(target=monitor_server, args=())
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    
