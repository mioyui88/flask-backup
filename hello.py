from flask import Flask
from flask import request
from flaskext.mysql import MySQL
import json

mysql = MySQL()

app = Flask(__name__)
 
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'root'
app.config['MYSQL_DATABASE_DB'] = 'cnvd'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

@app.route("/")
def hello():
    return "Welcome to Python Flask App!"

@app.route("/ip")
def ip():
    ip = request.args.get('IP')
    cursor = mysql.connect().cursor()
    cursor.execute("SELECT * from DEVICE_list_0 where DEV_ip = '"+ip+"' ")
    data = cursor.fetchall()
    if data == ():
     return "no data"
    else:
     r = json.dumps(data)
     return r


@app.route('/user/<name>')
def user(name):
	return '<h1>Hello, % s!</h1>' % name

 
if __name__ == "__main__":
    app.run(debug=True)
