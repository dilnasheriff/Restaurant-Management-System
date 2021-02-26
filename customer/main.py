from flask import Flask,render_template,request,redirect,url_for,make_response,send_file
from os.path import join, dirname, realpath
import os
app = Flask(__name__)
app.debug = True
import mysql.connector
import json
mydb = mysql.connector.connect(
  host="localhost",
  user="newuser",
  passwd="vandna_db",
  database="restaurant"
)
mycursor = mydb.cursor()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/orderplaced")
def orderplaced():
    return render_template("order_placed.html")

@app.route("/logout")
def logout():
    resp = make_response(redirect(url_for('index')))
    resp.delete_cookie('name')
    resp.delete_cookie('email')
    return resp

@app.route("/login", methods=['POST'])
def login():
    req_data = request.form
    mycursor.execute("select name,email_id from customer where phone_no=" + req_data["mobile_no"]);
    data = mycursor.fetchall()
    if len(data)==0:
        return render_template("other_user.html", mobile = req_data['mobile_no'])
    else:
        resp = make_response(redirect(url_for('order')))
        resp.set_cookie('name', data[0][0])
        resp.set_cookie('email', data[0][1])
        return resp

@app.route("/add_user", methods=['POST'])
def add_user():
    req_data = request.form
    sql = "INSERT INTO customer (email_id,phone_no,name) VALUES (%s,%s,%s)"
    val = (req_data["email"], req_data["phone"], req_data["name"])
    mycursor.execute(sql, val)
    mydb.commit()
    resp = make_response(redirect(url_for('order')))
    resp.set_cookie('name', req_data["name"])
    resp.set_cookie('email', req_data["email"])
    return resp

@app.route("/order")
def order():
    if 'name' not in request.cookies:
        return redirect(url_for('index'))
    name = request.cookies.get("name")
    mycursor.execute("SELECT food_id,item_name,price FROM food_items where category='South Indian'")
    si=mycursor.fetchall()
    mycursor.execute("SELECT food_id,item_name,price FROM food_items where category='North Indian'")
    ni=mycursor.fetchall()
    mycursor.execute("SELECT food_id,item_name,price FROM food_items where category='Continental'")
    c=mycursor.fetchall()
    mycursor.execute("SELECT food_id,item_name,price FROM food_items where category='Dessert'")
    d = mycursor.fetchall()
    mycursor.execute("SELECT food_id,item_name,price FROM food_items")
    items = [(x[0],[x[1],x[2]]) for x in mycursor.fetchall() ]

    return render_template("order.html",
                           name=name,
                           south_indian = si,
                           north_indian=ni,
                           continental=c,
                           items = dict(items),
                           dessert=d)

@app.route('/food_images/<path:filename>')
def get_image(filename):
    return send_file('../food_images/'+filename, mimetype='image/gif')

@app.route("/place_order", methods=['POST'])
def place_order():
    items = json.loads(request.form['items'])
    print("INSERT INTO order (email_id) VALUES ('"+request.cookies.get("email")+"')")
    mycursor.execute("INSERT INTO restaurant.order (email_id) VALUES ('"+request.cookies.get("email")+"')")
    order_no = mycursor.lastrowid
    val = (request.cookies.get("email"),
                     order_no,
                     '1')
    mycursor.execute("INSERT INTO food_delivered (email_id,order_no,w_e_id) VALUES (%s,%s,%s)",val)
    for each in items:
        sql = "INSERT INTO food_ordered (food_id,order_no,quantity) VALUES (%s,%s,%s)"
        val = (each, order_no,items[each])
        mycursor.execute(sql, val)
    mydb.commit()
    resp = make_response(redirect(url_for('orderplaced')))
    resp.delete_cookie('name')
    resp.delete_cookie('email')
    return resp



if __name__ == "__main__":
    app.run(port='80',host='127.0.0.1')