from flask import Flask
from flask_login import login_user
from flask import request, session
from pymongo import MongoClient
from flask import Flask, request, jsonify
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_cors import CORS
import random
import json
import pygsheets
import pandas as pd
from email.mime.text import MIMEText
import smtplib

app = Flask(__name__)
CORS(app)

client = MongoClient(
    'mongodb+srv://vercel-admin-user-641df86deec22841cd00f989:U7MK7TOONktRvOOR@cluster0.myy76mk.mongodb.net/myFirstDatabase?retryWrites=true&w=majority')
app.config['MONGO_URI'] = 'mongodb+srv://vercel-admin-user-641df86deec22841cd00f989:U7MK7TOONktRvOOR@cluster0.myy76mk.mongodb.net/myFirstDatabase?retryWrites=true&w=majority'
app.config['SECRET_KEY'] = 'a6d217d048fdcd227661b755'
db = client['Admin_BnB']
db2 = client['BnB_all_customers']
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = "ic2023wallet@gmail.com"
app.config['MAIL_PASSWORD'] = "irbnexpguzgxwdgx"


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/home')
def home():
    return 'home page'


# ------------------------------------------------------------------------------------------------------------


@app.route("/addAdmin", methods=["POST"])
def addAdmin():
    users = db['admin_db']
    user = request.json
    print(user)
    name = user['usrnme']
    phone = user['phone']
    pwd = bcrypt.generate_password_hash(user['pwd']).decode('utf-8')
    email = user['email']
    if users.find_one({"usrnme": name}) or users.find_one({"phone": phone}) or users.find_one({"email": email}):
        return {"isSuccess": "False", "msg": "Username or Phone number or Email already exist"}
    else:
        users.insert_one({
            'usrnme': name,
            'pwd': pwd,
            'email': email,
            "phone": phone,
            "pic_url": "https://media.istockphoto.com/id/962353378/vector/fast-food-line-icon.jpg?s=612x612&w=0&k=20&c=xD9-KlVj_w4hqhlB6VnsnTqcaumATgDnywNdhrhOok4=",
            "total_earning": 0,
            "total_customers": 0,
            "total_products": 0
        })
        return {"isSuccess": "True", "msg": f"{name}'s data inserted", "details": {
            'usrnme': name,
            'pwd': pwd,
            'email': email,
            "phone": phone,
            "pic_url": "https://media.istockphoto.com/id/962353378/vector/fast-food-line-icon.jpg?s=612x612&w=0&k=20&c=xD9-KlVj_w4hqhlB6VnsnTqcaumATgDnywNdhrhOok4="
        }}


@app.route("/signInAdmin", methods=["GET", "POST"])
def signInAdmin():
    users = db["admin_db"]
    clients_db = db["client_db_esp"]
    products_db = db['product_db_esp']
    if request.method == "GET":  # and "usrnme" not in session:
        # user = request.json
        # name = user["usrnme"]
        name = request.args.get("usrnme")
        password = request.args.get("pwd")
        # password = user["pwd"]
        logged_user = users.find_one({"usrnme": name})
        print(logged_user)
        if login_user:
            if logged_user:
                if bcrypt.check_password_hash(logged_user["pwd"], password):
                    session["usrnme"] = name
                    clients = clients_db.find({})
                    clients_no = clients_db.count_documents({})
                    products = products_db.find({})
                    products_no = products_db.count_documents({})
                    return {"isSuccess": "True", "details": {'usrnme': logged_user['usrnme'], 'email': logged_user['email'], "phone": logged_user['phone'], "pic_url": logged_user['pic_url'], "total_earning": logged_user['total_earning'], "total_customers": clients_no, "total_products": products_no}}
                else:
                    return {"isSuccess": "False"}
            return {"isSuccess": "False"}
        return {"isSuccess": "False"}


@app.route("/signInClient", methods=["GET", "POST"])
def signInClient():
    users = db["client_db_esp"]
    if request.method == "GET":  # and "usrnme" not in session:
        # user = request.json
        # name = user["usrnme"]
        name = request.args.get("usrnme")
        password = request.args.get("pwd")
        # password = user["pwd"]
        logged_user = users.find_one({"usrnme": name})
        print(logged_user)
        if login_user:
            if logged_user:
                if bcrypt.check_password_hash(logged_user["pwd"], password):
                    session["usrnme"] = name
                    return {"isSuccess": "True", "details": {'usrnme': logged_user['usrnme'], 'email': logged_user['email'], "phone": logged_user['phone'], "pic_url": logged_user['pic_url'], "balance": logged_user['balance'], "rfid": logged_user['rfid']}}
                else:
                    return {"isSuccess": "False"}
            return {"isSuccess": "False"}
        return {"isSuccess": "False"}
    
    
@app.route("/getAdminDetails", methods=["GET", "POST"])
def getAdminDetails():
    users = db["admin_db"]
    clients_db = db["client_db_esp"]
    products_db = db['product_db_esp']
    if request.method == "GET":  # and "usrnme" not in session:
        name = request.args.get("usrnme")
        logged_user = users.find_one({"usrnme": name})
        print(logged_user)
        if logged_user:
            clients = clients_db.find({})
            clients_no = clients_db.count_documents({})
            products = products_db.find({})
            products_no = products_db.count_documents({})
            return {"isSuccess": "True", "details": {'usrnme': logged_user['usrnme'], 'email': logged_user['email'], "phone": logged_user['phone'], "pic_url": logged_user['pic_url'], "total_earning": logged_user['total_earning'], "total_customers": clients_no, "total_products": products_no}}
        else:
            return {"isSuccess": "False"}
    return {"isSuccess": "False"}
    
#--------------------------------------------------------------------------------------------------------

def listToString(s):
    str1 = ""
    for ele in s:
        str1 += str("\n"+str(ele["productName"]+" x " + str(ele["quantity"]) + " - " + str(str(ele["productPrice"]) + "x" + str(ele["quantity"])+" = " + str(ele["productTotalPrice"]))))
    return str1

@app.route("/readRFID", methods=["GET"])
def readRFID():
    users = db["client_db_esp"]
    admin_db = db["admin_db"]

    amount_db = db['current_payment']
    transaction_details_esp = db['transaction_details_esp']

    amount_db_1 = db['current_payment_1']
    transaction_details_esp_1 = db['transaction_details_esp_1']

    amount_db_2 = db['current_payment_2']
    transaction_details_esp_2 = db['transaction_details_esp_2']

    amount_db_3 = db['current_payment_3']
    transaction_details_esp_3 = db['transaction_details_esp_3']

    amount_db_4 = db['current_payment_4']
    transaction_details_esp_4 = db['transaction_details_esp_4']

    amount_db_5 = db['current_payment_5']
    transaction_details_esp_5 = db['transaction_details_esp_5']

    if request.method == "GET":  # and "usrnme" not in session:
        rfid = request.args.get("rfid")
        adminName = request.args.get("adminName")

        if adminName == "admin1":
            if users.find_one({"rfid": rfid}):
                user_account = users.find_one({"rfid": rfid})
                user_balance = user_account["balance"]
                user_name = user_account["usrnme"]
                sender_email = user_account["email"]

                admin_account = admin_db.find_one({"usrnme": adminName})
                admin_earning = admin_account["total_earning"]
                
                user_balance = int(user_balance)
                amount_to_deduct_obj = amount_db_1.find_one({"current": "1"})
                amount_to_deduct = amount_to_deduct_obj["amount"]
                purchasedItems = amount_to_deduct_obj["productList"]

                if (int(user_balance)-int(amount_to_deduct)) <= user_balance and int(int(user_balance)-int(amount_to_deduct)) > 0  and amount_to_deduct != 0:

                    # if amount_to_deduct == 0:
                    #     return {"isSuccess": "False", "msg": "No amount deducted"}
                    
                    new_bal = int(user_balance)-int(amount_to_deduct)
                    new_data = {"$set": {
                        "balance": new_bal
                    }}
                    data = {
                        "amount": 0
                    }
                    users.update_one({"rfid": rfid}, new_data)
                    new_values = {"$set": data}
                    amount_db_1.update_one({"current": "1"}, new_values)
                    
                    purchasedItems = [{**item, "username": user_name} for item in purchasedItems]
                    print(purchasedItems)

                    data = {
                        "purchase":purchasedItems
                    }
                    
                    mycol = db2[user_name]
                    mycol.insert_one(data)

                    transaction_details_esp.insert_one(data)
                    transaction_details_esp_1.insert_one(data)

                    admin_account = admin_db.find_one({"usrnme": adminName})
                    admin_earning = admin_account["total_earning"]

                    total_earning = admin_earning + amount_to_deduct

                    new_earning = {"$set": {
                        "total_earning": total_earning
                    }}

                    admin_db.update_one({"usrnme": adminName}, new_earning)

                    smtp_server = smtplib.SMTP("smtp.gmail.com", 587)
                    smtp_server.ehlo()
                    smtp_server.starttls()
                    smtp_server.login("ic2023wallet@gmail.com", "irbnexpguzgxwdgx")
                    purchasedItems_string = listToString(purchasedItems)
                    mail_data = "Your Payment is Processed Successfully !\n\nDetails :- \n\n" + "Products Purchased :- " + purchasedItems_string + "\n\nTotal Amount Paid :- " + str(amount_to_deduct) + "\nRemaining Balance :- " + str(new_bal) + "\n\n Thank You !"
                    message = MIMEText(mail_data)
                    message["Subject"] = "Payment Successfull !"
                    message["To"] = sender_email
                    smtp_server.sendmail(sender_email, sender_email,
                                        message.as_string())
                    smtp_server.sendmail("ic2023wallet@gmail.com", "ic2023wallet@gmail.com",
                                        message.as_string())
                    smtp_server.quit()
                    
                    return {"isSuccess": "True", "details": {"balance": new_bal, "rfid": user_account["rfid"], "username": user_account["usrnme"]}}
                else:
                    data = {
                        "isSufficient": 0
                    }
                    new_values = {"$set": data}
                    amount_db_1.update_one({"current": "2"}, new_values)

                    smtp_server = smtplib.SMTP("smtp.gmail.com", 587)
                    smtp_server.ehlo()
                    smtp_server.starttls()
                    smtp_server.login("ic2023wallet@gmail.com", "irbnexpguzgxwdgx")
                    purchasedItems_string = listToString(purchasedItems)
                    mail_data = "Insufficient Balance, Please add Balance to your account."
                    message = MIMEText(mail_data)
                    message["Subject"] = "Insufficient Balance !"
                    message["To"] = sender_email
                    smtp_server.sendmail(sender_email, sender_email,
                                        message.as_string())
                    
                    smtp_server.sendmail(sender_email, sender_email,
                                        message.as_string())
                    smtp_server.quit()

                    smtp_server = smtplib.SMTP("smtp.gmail.com", 587)
                    smtp_server.ehlo()
                    smtp_server.starttls()
                    smtp_server.login("ic2023wallet@gmail.com", "irbnexpguzgxwdgx")
                    purchasedItems_string = listToString(purchasedItems)
                    mail_data = "Insufficient Balance, Please add Balance to your account."
                    message = MIMEText(mail_data)
                    message["Subject"] = "Insufficient Balance !"
                    message["To"] = sender_email
                    smtp_server.sendmail(sender_email, sender_email,
                                        message.as_string())
                    
                    smtp_server.sendmail(sender_email, sender_email,
                                        message.as_string())
                    smtp_server.quit()
                    
                    return {"isSuccess": "False", "msg": "Insufficient Balance"}
            else:
                return {"isSuccess": "False","msg": "RFID not found"}
        
        elif adminName == "admin2":
            if users.find_one({"rfid": rfid}):
                user_account = users.find_one({"rfid": rfid})
                user_balance = user_account["balance"]
                user_name = user_account["usrnme"]
                sender_email = user_account["email"]
                user_balance = int(user_balance)
                amount_to_deduct_obj = amount_db_2.find_one({"current": "1"})
                amount_to_deduct = amount_to_deduct_obj["amount"]
                purchasedItems = amount_to_deduct_obj["productList"]

                if (int(user_balance)-int(amount_to_deduct)) <= user_balance and int(int(user_balance)-int(amount_to_deduct)) > 0  and amount_to_deduct != 0:

                    # if amount_to_deduct == 0:
                    #     return {"isSuccess": "False", "msg": "No amount deducted"}
                    
                    new_bal = int(user_balance)-int(amount_to_deduct)
                    new_data = {"$set": {
                        "balance": new_bal
                    }}
                    data = {
                        "amount": 0
                    }
                    users.update_one({"rfid": rfid}, new_data)
                    new_values = {"$set": data}
                    amount_db_2.update_one({"current": "1"}, new_values)

                    purchasedItems = [{**item, "username": user_name} for item in purchasedItems]
                    print(purchasedItems)

                    data = {
                        "purchase":purchasedItems
                    }

                    mycol = db2[user_name]
                    mycol.insert_one(data)

                    transaction_details_esp.insert_one(data)
                    transaction_details_esp_2.insert_one(data)

                    admin_account = admin_db.find_one({"usrnme": adminName})
                    admin_earning = admin_account["total_earning"]

                    total_earning = admin_earning + amount_to_deduct

                    new_earning = {"$set": {
                        "total_earning": total_earning
                    }}

                    admin_db.update_one({"usrnme": adminName}, new_earning)
                    smtp_server = smtplib.SMTP("smtp.gmail.com", 587)
                    smtp_server.ehlo()
                    smtp_server.starttls()
                    smtp_server.login("ic2023wallet@gmail.com", "irbnexpguzgxwdgx")
                    purchasedItems_string = listToString(purchasedItems)
                    mail_data = "Your Payment is Processed Successfully !\n\nDetails :- \n\n" + "Products Purchased :- " + purchasedItems_string + "\nTotal Amount Paid :- " + str(amount_to_deduct) + "\nRemaining Balance :- " + str(new_bal) + "\n\n Thank You !"
                    message = MIMEText(mail_data)
                    message["Subject"] = "Payment Successfull !"
                    message["To"] = sender_email
                    smtp_server.sendmail(sender_email, sender_email,
                                        message.as_string())
                    
                    smtp_server.sendmail("ic2023wallet@gmail.com", "ic2023wallet@gmail.com",
                                        message.as_string())
                    smtp_server.quit()
                    
                    return {"isSuccess": "True", "details": {"balance": new_bal, "rfid": user_account["rfid"], "username": user_account["usrnme"]}}
                else:

                    data = {
                        "isSufficient": 0
                    }
                    new_values = {"$set": data}
                    amount_db_2.update_one({"current": "2"}, new_values)

                    smtp_server = smtplib.SMTP("smtp.gmail.com", 587)
                    smtp_server.ehlo()
                    smtp_server.starttls()
                    smtp_server.login("ic2023wallet@gmail.com", "irbnexpguzgxwdgx")
                    purchasedItems_string = listToString(purchasedItems)
                    mail_data = "Insufficient Balance, Please add Balance to your account."
                    message = MIMEText(mail_data)
                    message["Subject"] = "Insufficient Balance !"
                    message["To"] = sender_email
                    smtp_server.sendmail(sender_email, sender_email,
                                        message.as_string())
                    
                    smtp_server.sendmail(sender_email, sender_email,
                                        message.as_string())
                    smtp_server.quit()

                    return {"isSuccess": "False", "msg": "Insufficient Balance"}
            else:
                return {"msg": "RFID not found"}
            
        elif adminName == "admin3":
            if users.find_one({"rfid": rfid}):
                user_account = users.find_one({"rfid": rfid})
                user_balance = user_account["balance"]
                user_name = user_account["usrnme"]
                sender_email = user_account["email"]
                user_balance = int(user_balance)
                amount_to_deduct_obj = amount_db_3.find_one({"current": "1"})
                amount_to_deduct = amount_to_deduct_obj["amount"]
                purchasedItems = amount_to_deduct_obj["productList"]

                if (int(user_balance)-int(amount_to_deduct)) <= user_balance and int(int(user_balance)-int(amount_to_deduct)) > 0  and amount_to_deduct != 0:

                    # if amount_to_deduct == 0:
                    #     return {"isSuccess": "False", "msg": "No amount deducted"}
                    
                    new_bal = int(user_balance)-int(amount_to_deduct)
                    new_data = {"$set": {
                        "balance": new_bal
                    }}
                    data = {
                        "amount": 0
                    }
                    users.update_one({"rfid": rfid}, new_data)
                    new_values = {"$set": data}
                    amount_db_3.update_one({"current": "1"}, new_values)

                    purchasedItems = [{**item, "username": user_name} for item in purchasedItems]
                    print(purchasedItems)

                    data = {
                        "purchase":purchasedItems
                    }

                    mycol = db2[user_name]
                    mycol.insert_one(data)

                    transaction_details_esp.insert_one(data)
                    transaction_details_esp_3.insert_one(data)

                    admin_account = admin_db.find_one({"usrnme": adminName})
                    admin_earning = admin_account["total_earning"]

                    total_earning = admin_earning + amount_to_deduct

                    new_earning = {"$set": {
                        "total_earning": total_earning
                    }}

                    admin_db.update_one({"usrnme": adminName}, new_earning)
                    smtp_server = smtplib.SMTP("smtp.gmail.com", 587)
                    smtp_server.ehlo()
                    smtp_server.starttls()
                    smtp_server.login("ic2023wallet@gmail.com", "irbnexpguzgxwdgx")
                    purchasedItems_string = listToString(purchasedItems)
                    mail_data = "Your Payment is Processed Successfully !\n\nDetails :- \n\n" + "Products Purchased :- " + purchasedItems_string + "\nTotal Amount Paid :- " + str(amount_to_deduct) + "\nRemaining Balance :- " + str(new_bal) + "\n\n Thank You !"
                    message = MIMEText(mail_data)
                    message["Subject"] = "Payment Successfull !"
                    message["To"] = sender_email
                    smtp_server.sendmail(sender_email, sender_email,
                                        message.as_string())
                    
                    smtp_server.sendmail("ic2023wallet@gmail.com", "ic2023wallet@gmail.com",
                                        message.as_string())
                    smtp_server.quit()
                    
                    return {"isSuccess": "True", "details": {"balance": new_bal, "rfid": user_account["rfid"], "username": user_account["usrnme"]}}
                else:
                    data = {
                        "isSufficient": 0
                    }
                    new_values = {"$set": data}
                    amount_db_3.update_one({"current": "2"}, new_values)

                    smtp_server = smtplib.SMTP("smtp.gmail.com", 587)
                    smtp_server.ehlo()
                    smtp_server.starttls()
                    smtp_server.login("ic2023wallet@gmail.com", "irbnexpguzgxwdgx")
                    purchasedItems_string = listToString(purchasedItems)
                    mail_data = "Insufficient Balance, Please add Balance to your account."
                    message = MIMEText(mail_data)
                    message["Subject"] = "Insufficient Balance !"
                    message["To"] = sender_email
                    smtp_server.sendmail(sender_email, sender_email,
                                        message.as_string())
                    
                    smtp_server.sendmail(sender_email, sender_email,
                                        message.as_string())
                    smtp_server.quit()

                    return {"isSuccess": "False", "msg": "Insufficient Balance"}
            else:
                return {"msg": "RFID not found"}
        
        elif adminName == "admin4":
            if users.find_one({"rfid": rfid}):
                user_account = users.find_one({"rfid": rfid})
                user_balance = user_account["balance"]
                user_name = user_account["usrnme"]
                sender_email = user_account["email"]
                user_balance = int(user_balance)
                amount_to_deduct_obj = amount_db_4.find_one({"current": "1"})
                amount_to_deduct = amount_to_deduct_obj["amount"]
                purchasedItems = amount_to_deduct_obj["productList"]

                if (int(user_balance)-int(amount_to_deduct)) <= user_balance and int(int(user_balance)-int(amount_to_deduct)) > 0  and amount_to_deduct != 0:

                    # if amount_to_deduct == 0:
                    #     return {"isSuccess": "False", "msg": "No amount deducted"}
                    
                    new_bal = int(user_balance)-int(amount_to_deduct)
                    new_data = {"$set": {
                        "balance": new_bal
                    }}
                    data = {
                        "amount": 0
                    }
                    users.update_one({"rfid": rfid}, new_data)
                    new_values = {"$set": data}
                    amount_db_4.update_one({"current": "1"}, new_values)

                    purchasedItems = [{**item, "username": user_name} for item in purchasedItems]
                    print(purchasedItems)

                    data = {
                        "purchase":purchasedItems
                    }

                    mycol = db2[user_name]
                    mycol.insert_one(data)

                    transaction_details_esp.insert_one(data)
                    transaction_details_esp_4.insert_one(data)

                    admin_account = admin_db.find_one({"usrnme": adminName})
                    admin_earning = admin_account["total_earning"]

                    total_earning = admin_earning + amount_to_deduct

                    new_earning = {"$set": {
                        "total_earning": total_earning
                    }}

                    admin_db.update_one({"usrnme": adminName}, new_earning)
                    smtp_server = smtplib.SMTP("smtp.gmail.com", 587)
                    smtp_server.ehlo()
                    smtp_server.starttls()
                    smtp_server.login("ic2023wallet@gmail.com", "irbnexpguzgxwdgx")
                    purchasedItems_string = listToString(purchasedItems)
                    mail_data = "Your Payment is Processed Successfully !\n\nDetails :- \n\n" + "Products Purchased :- " + purchasedItems_string + "\nTotal Amount Paid :- " + str(amount_to_deduct) + "\nRemaining Balance :- " + str(new_bal) + "\n\n Thank You !"
                    message = MIMEText(mail_data)
                    message["Subject"] = "Payment Successfull !"
                    message["To"] = sender_email
                    smtp_server.sendmail(sender_email, sender_email,
                                        message.as_string())
                    
                    smtp_server.sendmail("ic2023wallet@gmail.com", "ic2023wallet@gmail.com",
                                        message.as_string())
                    smtp_server.quit()
                    
                    return {"isSuccess": "True", "details": {"balance": new_bal, "rfid": user_account["rfid"], "username": user_account["usrnme"]}}
                else:
                    data = {
                        "isSufficient": 0
                    }
                    new_values = {"$set": data}
                    amount_db_4.update_one({"current": "2"}, new_values)

                    smtp_server = smtplib.SMTP("smtp.gmail.com", 587)
                    smtp_server.ehlo()
                    smtp_server.starttls()
                    smtp_server.login("ic2023wallet@gmail.com", "irbnexpguzgxwdgx")
                    purchasedItems_string = listToString(purchasedItems)
                    mail_data = "Insufficient Balance, Please add Balance to your account."
                    message = MIMEText(mail_data)
                    message["Subject"] = "Insufficient Balance !"
                    message["To"] = sender_email
                    smtp_server.sendmail(sender_email, sender_email,
                                        message.as_string())
                    
                    smtp_server.sendmail(sender_email, sender_email,
                                        message.as_string())
                    smtp_server.quit()

                    return {"isSuccess": "False", "msg": "Insufficient Balance"}
            else:
                return {"msg": "RFID not found"}
            
        # elif adminName == "admin5":
        #     if users.find_one({"rfid": rfid}):
        #         user_account = users.find_one({"rfid": rfid})
        #         user_balance = user_account["balance"]
        #         user_name = user_account["usrnme"]
        #         user_balance = int(user_balance)
        #         amount_to_deduct_obj = amount_db_5.find_one({"current": "1"})
        #         amount_to_deduct = amount_to_deduct_obj["amount"]

        #         if (int(user_balance)-int(amount_to_deduct)) <= user_balance and int(int(user_balance)-int(amount_to_deduct)) > 0  and amount_to_deduct != 0:

        #             # if amount_to_deduct == 0:
        #             #     return {"isSuccess": "False", "msg": "No amount deducted"}
                    
        #             new_bal = int(user_balance)-int(amount_to_deduct)
        #             new_data = {"$set": {
        #                 "balance": new_bal
        #             }}
        #             data = {
        #                 "amount": 0
        #             }
        #             users.update_one({"rfid": rfid}, new_data)
        #             new_values = {"$set": data}
        #             amount_db_5.update_one({"current": "1"}, new_values)

        #             data = {
        #                 "purchase":purchasedItems
        #             }

        #             transaction_details_esp.insert_one(data)
        #             transaction_details_esp_5.insert_one(data)

        #             return {"isSuccess": "True", "details": {"balance": new_bal, "rfid": user_account["rfid"], "username": user_account["usrnme"]}}
        #         else:
        #             return {"isSuccess": "False", "msg": "Try Again"}
        #     else:
        #         return {"msg": "RFID not found"}
        
        elif adminName == "admin5":
            if users.find_one({"rfid": rfid}):
                user_account = users.find_one({"rfid": rfid})
                user_balance = user_account["balance"]
                user_name = user_account["usrnme"]
                sender_email = user_account["email"]
                user_balance = int(user_balance)
                amount_to_deduct_obj = amount_db_5.find_one({"current": "1"})
                amount_to_deduct = amount_to_deduct_obj["amount"]
                purchasedItems = amount_to_deduct_obj["productList"]

                if (int(user_balance)-int(amount_to_deduct)) <= user_balance and int(int(user_balance)-int(amount_to_deduct)) > 0  and amount_to_deduct != 0:

                    # if amount_to_deduct == 0:
                    #     return {"isSuccess": "False", "msg": "No amount deducted"}
                    
                    new_bal = int(user_balance)-int(amount_to_deduct)
                    new_data = {"$set": {
                        "balance": new_bal
                    }}
                    data = {
                        "amount": 0
                    }
                    users.update_one({"rfid": rfid}, new_data)
                    new_values = {"$set": data}
                    amount_db_5.update_one({"current": "1"}, new_values)

                    purchasedItems = [{**item, "username": user_name} for item in purchasedItems]
                    print(purchasedItems)

                    data = {
                        "purchase":purchasedItems
                    }

                    mycol = db2[user_name]
                    mycol.insert_one(data)

                    transaction_details_esp.insert_one(data)
                    transaction_details_esp_5.insert_one(data)

                    admin_account = admin_db.find_one({"usrnme": adminName})
                    admin_earning = admin_account["total_earning"]

                    total_earning = admin_earning + amount_to_deduct

                    new_earning = {"$set": {
                        "total_earning": total_earning
                    }}

                    admin_db.update_one({"usrnme": adminName}, new_earning)
                    smtp_server = smtplib.SMTP("smtp.gmail.com", 587)
                    smtp_server.ehlo()
                    smtp_server.starttls()
                    smtp_server.login("ic2023wallet@gmail.com", "irbnexpguzgxwdgx")
                    purchasedItems_string = listToString(purchasedItems)
                    mail_data = "Your Payment is Processed Successfully !\n\nDetails :- \n\n" + "Products Purchased :- " + purchasedItems_string + "\nTotal Amount Paid :- " + str(amount_to_deduct) + "\nRemaining Balance :- " + str(new_bal) + "\n\n Thank You !"
                    message = MIMEText(mail_data)
                    message["Subject"] = "Payment Successfull !"
                    message["To"] = sender_email
                    smtp_server.sendmail(sender_email, sender_email,
                                        message.as_string())
                    
                    smtp_server.sendmail("ic2023wallet@gmail.com", "ic2023wallet@gmail.com",
                                        message.as_string())
                    smtp_server.quit()
                    
                    return {"isSuccess": "True", "details": {"balance": new_bal, "rfid": user_account["rfid"], "username": user_account["usrnme"]}}
                else:
                    data = {
                        "isSufficient": 0
                    }
                    new_values = {"$set": data}
                    amount_db_5.update_one({"current": "2"}, new_values)

                    smtp_server = smtplib.SMTP("smtp.gmail.com", 587)
                    smtp_server.ehlo()
                    smtp_server.starttls()
                    smtp_server.login("ic2023wallet@gmail.com", "irbnexpguzgxwdgx")
                    purchasedItems_string = listToString(purchasedItems)
                    mail_data = "Insufficient Balance, Please add Balance to your account."
                    message = MIMEText(mail_data)
                    message["Subject"] = "Insufficient Balance !"
                    message["To"] = sender_email
                    smtp_server.sendmail(sender_email, sender_email,
                                        message.as_string())
                    
                    smtp_server.sendmail(sender_email, sender_email,
                                        message.as_string())
                    smtp_server.quit()

                    return {"isSuccess": "False", "msg": "Insufficient Balance"}
            else:
                return {"msg": "RFID not found"}
            
        else:
            return {"msg": "Error, Invalid Admin Name"}
        
#--------------------------------------------------------------------------------------------------------

@app.route("/getOrderListAdmin", methods=["GET"])
def getOrderListAdmin():
    users = db["client_db_esp"]
    amount_db = db['current_payment']
    transaction_details_esp = db['transaction_details_esp']

    amount_db_1 = db['current_payment_1']
    transaction_details_esp_1 = db['transaction_details_esp_1']

    amount_db_2 = db['current_payment_2']
    transaction_details_esp_2 = db['transaction_details_esp_2']

    amount_db_3 = db['current_payment_3']
    transaction_details_esp_3 = db['transaction_details_esp_3']

    amount_db_4 = db['current_payment_4']
    transaction_details_esp_4 = db['transaction_details_esp_4']

    amount_db_5 = db['current_payment_5']
    transaction_details_esp_5 = db['transaction_details_esp_5']

    if request.method == "GET":  # and "usrnme" not in session:
        adminName = request.args.get("adminName")

        if adminName == "admin1":
            allData = transaction_details_esp_1.find({})
            data = []
            for i in allData:
                if i["purchase"] != None:
                    data.append(i["purchase"])
            return data
        
        elif adminName == "admin2":
            allData = transaction_details_esp_2.find({})
            data = []
            for i in allData:
                if i["purchase"] != None:
                    data.append(i["purchase"])
            return data
            
        elif adminName == "admin3":
            allData = transaction_details_esp_3.find({})
            data = []
            for i in allData:
                if i["purchase"] != None:
                    data.append(i["purchase"])
            return data
        
        elif adminName == "admin4":
            allData = transaction_details_esp_4.find({})
            data = []
            for i in allData:
                if i["purchase"] != None:
                    data.append(i["purchase"])
            return data
            
        # elif adminName == "admin5":
        #     if users.find_one({"rfid": rfid}):
        #         user_account = users.find_one({"rfid": rfid})
        #         user_balance = user_account["balance"]
        #         user_balance = int(user_balance)
        #         amount_to_deduct_obj = amount_db_5.find_one({"current": "1"})
        #         amount_to_deduct = amount_to_deduct_obj["amount"]

        #         if (int(user_balance)-int(amount_to_deduct)) <= user_balance and int(int(user_balance)-int(amount_to_deduct)) > 0  and amount_to_deduct != 0:

        #             # if amount_to_deduct == 0:
        #             #     return {"isSuccess": "False", "msg": "No amount deducted"}
                    
        #             new_bal = int(user_balance)-int(amount_to_deduct)
        #             new_data = {"$set": {
        #                 "balance": new_bal
        #             }}
        #             data = {
        #                 "amount": 0
        #             }
        #             users.update_one({"rfid": rfid}, new_data)
        #             new_values = {"$set": data}
        #             amount_db_5.update_one({"current": "1"}, new_values)

        #             data = {
        #                 "purchase":purchasedItems
        #             }

        #             transaction_details_esp.insert_one(data)
        #             transaction_details_esp_5.insert_one(data)

        #             return {"isSuccess": "True", "details": {"balance": new_bal, "rfid": user_account["rfid"], "username": user_account["usrnme"]}}
        #         else:
        #             return {"isSuccess": "False", "msg": "Try Again"}
        #     else:
        #         return {"msg": "RFID not found"}
        
        elif adminName == "admin5":
            allData = transaction_details_esp_5.find({})
            data = []
            for i in allData:
                if i["purchase"] != None:
                    data.append(i["purchase"])
            return data
        
        elif adminName == "admin":
            allData = transaction_details_esp.find({})
            data = []
            for i in allData:
                if i["purchase"] != None:
                    data.append(i["purchase"])
            return data
        
        else:
            return []
        
@app.route("/getOrderListClient", methods=["GET"])
def getOrderListClient():
    users = db["client_db_esp"]

    if request.method == "GET":  # and "usrnme" not in session:
        username = request.args.get("username")

        logged_user = users.find_one({"usrnme": username})

        client_order_db = db2[username]

        allData = client_order_db.find({})

        purchase = []

        if allData:
            for i in allData:
                if i["purchase"] != None:
                    purchase.append(i["purchase"])

            data = {
                "balance": logged_user['balance'],
                "purchase": purchase
            }

            return data
        
@app.route("/getOrderListClient_to_sheet", methods=["GET"])
def getOrderListClient_to_sheet():
    transaction_details_esp = db['transaction_details_esp']

    if request.method == "GET":  # and "usrnme" not in session:
        allData = transaction_details_esp.find({})
        data = []
        for i in allData:
            if i["purchase"] != None:
                data = data + i["purchase"]

        gc = pygsheets.authorize(service_file='creds.json')
        sh = gc.open('Stall-management-data')
        wks = sh[0]
        existing_data = wks.get_all_records()
        df_combined = pd.DataFrame(data)
        wks.set_dataframe(df_combined, start='A1')
        return data
            
#--------------------------------------------------------------------------------------------------------

@app.route("/addClient", methods=["POST"])
def addClient():
    users = db['client_db_esp']
    user = request.json
    print(user)
    name = user['usrnme']
    phone = user['phone']
    pwd = bcrypt.generate_password_hash(user['pwd']).decode('utf-8')
    email = user['email']
    rfid = user['rfid']
    if users.find_one({"usrnme": name}) or users.find_one({"phone": phone}) or users.find_one({"email": email}):
        return {"isSuccess": "False", "msg": "Username or Phone number or Email already exist"}
    else:
        users.insert_one({
            'usrnme': name,
            'pwd': pwd,
            'email': email,
            "phone": phone,
            "pic_url": "https://media.istockphoto.com/id/962353378/vector/fast-food-line-icon.jpg?s=612x612&w=0&k=20&c=xD9-KlVj_w4hqhlB6VnsnTqcaumATgDnywNdhrhOok4=",
            "balance": 0,
            "rfid": rfid
        })
        return {"isSuccess": "True", "msg": f"{name}'s data inserted", "details": {
            'usrnme': name,
            'pwd': pwd,
            'email': email,
            "phone": phone,
            "pic_url": "https://media.istockphoto.com/id/962353378/vector/fast-food-line-icon.jpg?s=612x612&w=0&k=20&c=xD9-KlVj_w4hqhlB6VnsnTqcaumATgDnywNdhrhOok4=",
            "balance": 0,
            "rfid": rfid
        }}


@app.route("/deleteClient", methods=["DELETE"])
def deleteClient():
    users = db["client_db_esp"]
    rfid = request.args.get('rfid')
    if users.find_one({"rfid": rfid}) is None:
        return {"msg": f"{rfid} doesnot exists in the database"}

    users.delete_one({"rfid": rfid})
    return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}


@app.route("/addProduct", methods=["POST"])
def addProduct():
    users = db['product_db_esp']
    user = request.json
    print(user)
    productName = user['productName']
    productPrice = user['productPrice']
    pid = random.getrandbits(32)
    users.insert_one({
        'productName': productName,
        'productPrice': productPrice,
        "pic_url": "https://media.istockphoto.com/id/962353378/vector/fast-food-line-icon.jpg?s=612x612&w=0&k=20&c=xD9-KlVj_w4hqhlB6VnsnTqcaumATgDnywNdhrhOok4=",
        "pid": pid
    })
    return {"isSuccess": "True", "msg": f"{productName}'s data inserted", "details": {
        'productName': productName,
        'productPrice': productPrice,
        "pic_url": "https://media.istockphoto.com/id/962353378/vector/fast-food-line-icon.jpg?s=612x612&w=0&k=20&c=xD9-KlVj_w4hqhlB6VnsnTqcaumATgDnywNdhrhOok4=",
        "pid": pid
    }}


@app.route("/getAllProduct", methods=["GET"])
def getAllProduct():
    users = db["product_db_esp"]
    ans = []
    for user in users.find({}):
        ans.append({
            "productName": user['productName'],
            "productPrice": user['productPrice'],
            "pic_url": user['pic_url'],
            "pid": user['pid']
        })
    return ans

@app.route("/set_issufficient", methods=["GET"])
def set_issufficient():
    admin = request.args.get('adminName')
    amount_db_1 = db['current_payment_1']
    amount_db_2 = db['current_payment_2']
    amount_db_3 = db['current_payment_3']
    amount_db_4 = db['current_payment_4']
    amount_db_5 = db['current_payment_5']
    data = {
            "isSufficient": 1
        }
    new_values = {"$set": data}

    if admin == "admin1":
        amount_db_1.update_one({"current": "2"}, new_values)
        return {"isSuccess":True}
    elif admin == "admin2":
        amount_db_2.update_one({"current": "2"}, new_values)
        return {"isSuccess":True}
    elif admin == "admin3":
        amount_db_3.update_one({"current": "2"}, new_values)
        return {"isSuccess":True}
    elif admin == "admin4":
        amount_db_4.update_one({"current": "2"}, new_values)
        return {"isSuccess":True}
    elif admin == "admin5":
        amount_db_5.update_one({"current": "2"}, new_values)
        return {"isSuccess":True}
    else:
        return {"isSuccess":False}
    
@app.route("/get_issufficient", methods=["GET"])
def get_issufficient():
    admin = request.args.get('adminName')
    amount_db_1 = db['current_payment_1']
    amount_db_2 = db['current_payment_2']
    amount_db_3 = db['current_payment_3']
    amount_db_4 = db['current_payment_4']
    amount_db_5 = db['current_payment_5']
    data = {
            "isSufficient": 0
        }
    new_values = {"$set": data}

    if admin == "admin1":
        dt = amount_db_1.find_one({"current": "2"})
        isSufficient = dt["isSufficient"]
        return {"isSuccess":True, "isSufficient":isSufficient}
    elif admin == "admin2":
        dt = amount_db_2.find_one({"current": "2"})
        isSufficient = dt["isSufficient"]
        return {"isSuccess":True, "isSufficient":isSufficient}
    elif admin == "admin3":
        dt = amount_db_3.find_one({"current": "2"})
        isSufficient = dt["isSufficient"]
        return {"isSuccess":True, "isSufficient":isSufficient}
    elif admin == "admin4":
        dt = amount_db_4.find_one({"current": "2"})
        isSufficient = dt["isSufficient"]
        return {"isSuccess":True, "isSufficient":isSufficient}
    elif admin == "admin5":
        dt = amount_db_5.find_one({"current": "2"})
        isSufficient = dt["isSufficient"]
        return {"isSuccess":True, "isSufficient":isSufficient}
    else:
        return {"isSuccess":False}


@app.route("/getAllClient", methods=["GET"])
def getAllClient():
    users = db["client_db_esp"]
    ans = []
    for user in users.find({}):
        ans.append({
            "usrnme": user["usrnme"],
            "email": user["email"],
            "phone": user["phone"],
            "pic_url": user["pic_url"],
            "balance": user["balance"],
            "rfid": user["rfid"]
        })
    return ans


@app.route("/deleteProduct", methods=["DELETE"])
def deleteProduct():
    users = db["product_db_esp"]
    pid = request.args.get('pid')
    pid = int(pid)
    if users.find_one({"pid": pid}) is None:
        return {"msg": f"{pid} doesnot exists in the database"}

    users.delete_one({"pid": pid})
    return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}

#--------------------------------------------------------------------------------------------------------

@app.route("/handlePayment", methods=["POST"])
def handlePayment():
    users1 = db['current_payment_1']
    users2 = db['current_payment_2']
    users3 = db['current_payment_3']
    users4 = db['current_payment_4']
    users5 = db['current_payment_5']
    user = request.json
    print(user)
    total_amount = user['total_amount']
    total_amount = int(total_amount)
    adminName = user['adminName']
    productList = user['productList']

    if adminName == "admin1":
        if users1.find_one({"current": "1"}):
            data = {
                "amount": total_amount,
                "productList": productList
            }
            new_values = {"$set": data}
            users1.update_one({"current": "1"}, new_values)
            return {"msg": "Amount Updated", "total_amount": total_amount}
        else:
            return {"msg": "Amount not found"}
        
    elif adminName == "admin2":
        if users2.find_one({"current": "1"}):
            data = {
                "amount": total_amount,
                "productList": productList
            }
            new_values = {"$set": data}
            users2.update_one({"current": "1"}, new_values)
            return {"msg": "Amount Updated", "total_amount": total_amount}
        else:
            return {"msg": "Amount not found"}
        
    elif adminName == "admin3":
        if users3.find_one({"current": "1"}):
            data = {
                "amount": total_amount,
                "productList": productList
            }
            new_values = {"$set": data}
            users3.update_one({"current": "1"}, new_values)
            return {"msg": "Amount Updated", "total_amount": total_amount}
        else:
            return {"msg": "Amount not found"}
        
    elif adminName == "admin4":
        if users4.find_one({"current": "1"}):
            data = {
                "amount": total_amount,
                "productList": productList
            }
            new_values = {"$set": data}
            users4.update_one({"current": "1"}, new_values)
            return {"msg": "Amount Updated", "total_amount": total_amount}
        else:
            return {"msg": "Amount not found"}
        
    elif adminName == "admin5":
        if users5.find_one({"current": "1"}):
            data = {
                "amount": total_amount,
                "productList": productList
            }
            new_values = {"$set": data}
            users5.update_one({"current": "1"}, new_values)
            return {"msg": "Amount Updated", "total_amount": total_amount}
        else:
            return {"msg": "Amount not found"}
        
    else:
        return {"msg": "No RFID Device associated with admin you have loggedin, Please contact developer to solve this issue"}

#--------------------------------------------------------------------------------------------------------


@app.route("/addbalance_esp", methods=["GET"])
def addbalance_esp():
    users = db["client_db_esp"]
    if request.method == "GET":  # and "usrnme" not in session:
        # user = request.json
        # name = user["usrnme"]
        rfid = request.args.get("rfid")
        addMoney = request.args.get("addMoney")
        # password = user["pwd"]
        logged_user = users.find_one({"rfid": rfid})
        print(logged_user)
        if logged_user:
            prev_bal = logged_user["balance"]
            if (int(prev_bal)+int(addMoney)) <= 100000:
                new_bal = int(prev_bal)+int(addMoney)
                new_data = {"$set": {
                    "balance": new_bal
                }}
                users.update_one({"rfid": rfid}, new_data)
                return {"isSuccess": "True", "details": {"balance": new_bal, "rfid": logged_user["rfid"]}}
            else:
                return {"isSuccess": "False", "msg": "Cannot add more than Rs 1,00,000"}
        else:
            return {"isSuccess": "False", "msg": "Invalid Data"}
        
@app.route("/readStatus", methods=["GET"])
def readStatus():
    users = db["lora_status"]
    if request.method == "GET":  # and "usrnme" not in session:
        logged_user = users.find_one({"id": "1"})
        if logged_user["status"] == "1":
            return {"isSuccess": "True", "status": "1"}
        else:
            return {"isSuccess": "True", "status": "0"}
    else:
        return {"isSuccess": "False", "error":"error"}

# -------------------------------------------------------------------------------------------------------


@app.route("/logout")
def logout():
    name = request.args.get("usrnme")
    session.pop("usrnme", None)
    return f"{name.upper()} logged out successfully"


if __name__ == '__main__':
    app.run()










