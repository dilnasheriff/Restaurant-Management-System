from flask import Flask,render_template,request,redirect,url_for
from os.path import join, dirname, realpath
import os
app = Flask(__name__)
app.debug = True
import mysql.connector

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

@app.route("/image_upload", methods = ['POST'])
def image_upload():
    if request.method == 'POST':
        f = request.files['file']
        UPLOADS_PATH = join(dirname(realpath(__file__)), '../food_images/')
        if os.path.exists(UPLOADS_PATH+request.form['id']+'.jpg'):
            os.remove(UPLOADS_PATH+request.form['id']+'.jpg')
        f.save(UPLOADS_PATH+request.form['id']+'.jpg')
        return "Success"

@app.route("/food")
def food():
    mycursor.execute("select food_id,item_name from food_items")
    data = mycursor.fetchall()
    return render_template("food.html", item_list=data)

@app.route("/add_food", methods=['POST'])
def food_add():
    req_data=request.form
    sql = "INSERT INTO food_items (item_name,price,category) VALUES (%s,%s,%s)"
    val = (req_data["name"], req_data["price"], req_data["category"])
    mycursor.execute(sql, val)
    mydb.commit()
    return "Added Successfully"

@app.route("/update_food", methods=['POST'])
def food_update():
    req_data=request.form
    sql = "UPDATE food_items set item_name=%s,price=%s,category=%s WHERE food_id=%s"
    val = (req_data["name"], req_data["price"], req_data["category"], req_data["id"])
    mycursor.execute(sql, val)
    mydb.commit()
    return "Updated Successfully"

@app.route("/find_food", methods=['POST'])
def food_find():
    req_data = request.form
    mycursor.execute("select item_name,price,category from food_items where food_id=" + req_data["id"]);
    data = mycursor.fetchall()[0]
    return dict([('food_info', data)])

@app.route("/remove_food", methods=['POST'])
def food_remove():
    req_data = request.form
    sql = "DELETE from food_items WHERE food_id="+req_data["id"]
    mycursor.execute(sql)
    mydb.commit()
    UPLOADS_PATH = join(dirname(realpath(__file__)), '../food_images/')
    if os.path.exists(UPLOADS_PATH + request.form['id'] + '.jpg'):
        os.remove(UPLOADS_PATH + request.form['id'] + '.jpg')
    return "Deleted Successfully"

@app.route("/chef")
def chef():
    mycursor.execute("select * from food_items")
    data = mycursor.fetchall()
    mycursor.execute("select distinct employee.id,employee.name from employee,chef where employee.id=chef.ch_e_id")
    chefs=mycursor.fetchall()
    return render_template("chef.html",item_list=data,chefs=chefs)

@app.route("/add_chef", methods=['POST'])
def chef_value():
    req_data = request.form
    sql = "INSERT INTO employee (name,date_of_joining,salary,pincode,location) VALUES (%s,%s,%s,%s,%s)"
    val = (req_data["name"], req_data["date_of_joining"], req_data["salary"], req_data["pincode"], req_data["location"])
    mycursor.execute(sql, val)
    sql = "INSERT INTO chef (food_id,ch_e_id) VALUES (%s,%s)"
    ch = mycursor.lastrowid
    for food_id in req_data.getlist('food_id'):
        val = (food_id, ch)
        mycursor.execute(sql, val)
    mydb.commit()
    return "Add Successful"

@app.route("/find_chef", methods=['POST'])
def chef_find():
    req_data = request.form
    mycursor.execute("select * from employee where id="+req_data["id"])
    chef_info=mycursor.fetchall()[0]
    mycursor.execute("select chef.food_id,food_items.item_name from chef,food_items where food_items.food_id=chef.food_id and ch_e_id="+req_data["id"])
    food_items=mycursor.fetchall()
    return dict([('chef_info',chef_info),('food_items',food_items)])

@app.route("/update_chef", methods=['POST'])
def chef_update():
    req_data = request.form
    sql = "UPDATE employee set name=%s ,date_of_joining=%s,salary=%s,pincode=%s,location=%s WHERE id=%s"
    val = (req_data["name"], req_data["doj"], req_data["salary"], req_data["pincode"], req_data["location"], req_data["id"])
    mycursor.execute(sql, val)
    mycursor.execute("DELETE from chef WHERE ch_e_id="+req_data["id"])
    sql = "INSERT INTO chef (food_id,ch_e_id) VALUES (%s,%s)"
    for food_id in req_data.getlist('food_id'):
        val = (food_id, req_data["id"])
        mycursor.execute(sql, val)
    mydb.commit()
    return "Updated successfully"

@app.route("/remove_chef", methods=['POST'])
def chef_remove():
    req_data = request.form
    mycursor.execute("DELETE from chef WHERE ch_e_id="+req_data["id"])
    mycursor.execute("DELETE from employee WHERE id=" + req_data["id"])
    mydb.commit()
    return "Deleted Successfully"

@app.route("/cashier")
def cashier():
    mycursor.execute("select employee.id,employee.name from employee,cashier where employee.id=cashier.c_e_id")
    cashiers = mycursor.fetchall()
    return render_template("cashier.html", cashiers=cashiers)

@app.route("/add_cashier", methods=['POST'])
def cashier_add():
    req_data = request.form
    sql = "INSERT INTO employee (name,date_of_joining,salary,pincode,location) VALUES (%s,%s,%s,%s,%s)"
    val = (req_data["name"], req_data["date_of_joining"], req_data["salary"], req_data["pincode"], req_data["location"])
    mycursor.execute(sql, val)
    sql = "INSERT INTO cashier (counter_id,c_e_id) VALUES (%s,%s)"
    val = (req_data["counter_id"], mycursor.lastrowid)
    mycursor.execute(sql, val)
    mydb.commit()
    return "Added Successfully"

@app.route("/find_cashier", methods=['POST'])
def cashier_find():
    req_data = request.form
    mycursor.execute(
        "select employee.*,cashier.counter_id from employee,cashier where cashier.c_e_id=employee.id AND employee.id=" +
        req_data["id"])
    cashier_info = mycursor.fetchall()[0]
    return dict([('cashier_info', cashier_info)])

@app.route("/update_cashier", methods=['POST'])
def cashier_update():
    req_data = request.form
    sql = "UPDATE employee set name=%s ,date_of_joining=%s,salary=%s,pincode=%s,location=%s WHERE id=%s"
    val = (
        req_data["name"], req_data["doj"], req_data["salary"], req_data["pincode"], req_data["location"],
        req_data["id"])
    mycursor.execute(sql, val)
    mycursor.execute("DELETE from cashier WHERE c_e_id=" + req_data["id"])
    sql = "INSERT INTO cashier (c_e_id,counter_id) VALUES (%s,%s)"
    val = (req_data["id"], req_data["counter_id"])
    mycursor.execute(sql, val)
    mydb.commit()
    return "Updated successfully"

@app.route("/remove_cashier", methods=['POST'])
def cashier_remove():
    req_data = request.form
    mycursor.execute("DELETE from employee WHERE id=" + req_data["id"])
    mycursor.execute("DELETE from cashier WHERE c_e_id=" + req_data["id"])
    mydb.commit()
    return "Deleted Successfully"

@app.route("/waiter")
def waiter():
    mycursor.execute("select employee.id,employee.name from employee,waiter where employee.id=waiter.id")
    waiters = mycursor.fetchall()
    return render_template("waiter.html", waiters=waiters)

@app.route("/add_waiter", methods=['POST'])
def waiter_add():
    req_data = request.form
    print(req_data)
    sql = "INSERT INTO employee (name,date_of_joining,salary,pincode,location) VALUES (%s,%s,%s,%s,%s)"
    val = (req_data["name"], req_data["date_of_joining"], req_data["salary"], req_data["pincode"], req_data["location"])
    mycursor.execute(sql, val)
    wid = mycursor.lastrowid
    sql = "INSERT INTO waiter (id,hall_type) VALUES (%s,%s)"
    val = (wid, req_data["hall_type"])
    mycursor.execute(sql, val)
    for each in list(req_data["tables"].split(',')):
        mycursor.execute("INSERT INTO tables_alloted (t_alloc,w_e_id) VALUES(%s,%s)", (each,wid))
    mydb.commit()
    return "Added Successfully"

@app.route("/update_waiter", methods=['POST'])
def waiter_update():
    req_data = request.form
    sql = "UPDATE employee set name=%s ,date_of_joining=%s,salary=%s,pincode=%s,location=%s WHERE id=%s"
    val = (
    req_data["name"], req_data["doj"], req_data["salary"], req_data["pincode"], req_data["location"], req_data["id"])
    mycursor.execute(sql, val)
    mycursor.execute("DELETE from waiter WHERE id=" + req_data["id"])
    mycursor.execute("DELETE from tables_alloted WHERE w_e_id=" + req_data["id"])
    sql = "INSERT INTO waiter (id,hall_type) VALUES (%s,%s)"
    val = (req_data["id"], req_data["hall_type"])
    mycursor.execute(sql, val)
    for each in list(req_data["tables"].split(',')):
        mycursor.execute("INSERT INTO tables_alloted (t_alloc,w_e_id) VALUES(%s,%s)", (each, req_data["id"]))
    mydb.commit()
    return "Updated successfully"

@app.route("/find_waiter", methods=['POST'])
def waiter_find():
    req_data = request.form
    mycursor.execute("select employee.*,waiter.hall_type from employee,waiter where waiter.id=employee.id AND employee.id=" + req_data["id"])
    waiter_info = mycursor.fetchall()[0]
    mycursor.execute(
        "select t_alloc from tables_alloted where w_e_id=" +
        req_data["id"])
    tables = mycursor.fetchall()
    return dict([('waiter_info', waiter_info), ('tables', ','.join([str(x[0]) for x in tables]))])

@app.route("/remove_waiter", methods=['POST'])
def waiter_remove():
    req_data = request.form
    mycursor.execute("DELETE from employee WHERE id=" + req_data["id"])
    mycursor.execute("DELETE from waiter WHERE id=" + req_data["id"])
    mycursor.execute("DELETE from tables_alloted WHERE w_e_id=" + req_data["id"])
    mydb.commit()
    return "Deleted Successfully"


@app.route("/customer", methods=['POST'])
def func5():
    req_data=request.form
    mycursor.execute('select * from customer where phone = "%s"', req_data[phone])
    result=mycursor.fetchall()
    if result:
        return redirect(url_for('customerWelcome'))
    else:
        return redirect(url_for('newCustomer'))


if __name__ == "__main__":
    app.run(port='80',host='127.0.0.2')