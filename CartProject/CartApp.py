from flask import Flask
from flask import render_template
from flask import request,redirect, url_for,session
from flask_mysqldb import MySQL
from werkzeug.utils import secure_filename
import os 
from flask_session import Session




UPLOAD_FOLDER = os.path.join('static', 'uploads')
app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'cart'

app.secret_key = 'super secret key'
app.config["SESSION_PERMANENT"] = True
app.config["SESSION_TYPE"] = "filesystem"

Session(app)


ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}


app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

mysql = MySQL(app)




@app.route("/")
def cart_app():
    return redirect(url_for('login'))



@app.route('/adminlogin', methods=['POST', 'GET'])
def admin_login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor()
        cursor.execute(''' SELECT * FROM admin_users where username = %s and password = %s ''',(username,password))
        user = cursor.fetchone()
        cursor.close()
        if(user):
            return "Success"
        else:
            error = "Not a valid credential !"
            return render_template('login.html', error=error)
    return render_template('login.html', error=error)

@app.route('/uploaditem', methods=['POST', 'GET'])
def upload_item():
    error = None
    if request.method == 'POST':
        itemname = request.form['itemname']
        itemprice = request.form['itemprice']
        item_image = request.files['item_image']

        filename = secure_filename(item_image.filename)
        item_image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
  
        
        cursor = mysql.connection.cursor()
        cursor.execute(''' insert into items values(%s,%s,%s) ''',(itemname,itemprice,filename))
        mysql.connection.commit()
        cursor.close()
    return render_template('itemupload.html', error=error)

@app.route('/login', methods=['POST', 'GET'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor()
        cursor.execute(''' SELECT * FROM users where username = %s and password = %s ''',(username,password))
        user = cursor.fetchone()
        cursor.close()
        if(user):
            return "Success"
        else:
            error = "Not a valid credential !"
            return render_template('login.html', error=error)
    return render_template('login.html', error=error)

@app.route('/register', methods=['POST', 'GET'])
def register():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor()
        cursor.execute(''' INSERT INTO users VALUES(%s,%s)''',(username,password))
        mysql.connection.commit()
        cursor.close()
    return render_template('register.html', error=error)

@app.route('/menu', methods=['POST', 'GET'])
def menu():
    session["item_name"] = "test_session"
    se = session.get("item_name")
    cursor = mysql.connection.cursor()
    cursor.execute(''' SELECT * FROM items''')
    data = cursor.fetchall()
    cursor.close()
    return render_template('itemsmenu.html',data=data,se=se)

@app.route('/add/<string:id>', methods=['POST', 'GET'])
def add(id):
    if(not session.get("prod_id")):
        session["prod_id"] = []
    sess_id = session.get("prod_id")
    sess_id.append(id)
    session["prod_id"] = sess_id
    return redirect('/menu')

@app.route('/cart', methods=['POST', 'GET'])
def cart():
    sess_id = session.get("prod_id")
    ids = tuple(sess_id)
    cursor = mysql.connection.cursor()
    query = "SELECT * FROM items WHERE id IN ({})".format(','.join(map(str, sess_id)))
    cursor = mysql.connection.cursor()
    cursor.execute(query)
    data = cursor.fetchall()
    total = 0
    for i in data:
        total = total + int(i[2])
    cursor.close()
    return render_template('cart.html',items=data,total=total)

@app.route('/clearcart', methods=['POST', 'GET'])
def clearcart():
    session.clear()
    return redirect('/menu')

