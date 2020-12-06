from flask import Flask, render_template, flash, redirect, url_for, request, session
import requests
import psycopg2
import json
import email_sender
import pickle
import numpy as np
import os
from PIL import Image
import boto3
from keras.models import model_from_json
from keras.preprocessing.image import ImageDataGenerator
from keras.preprocessing import image
import numpy as np
import keras
from keras.applications.imagenet_utils import preprocess_input
from keras.applications.imagenet_utils import decode_predictions
from keras.models import model_from_json
from keras.preprocessing.image import load_img




"""
connection = psycopg2.connect(
    host="localhost",
    database="postgres",
    user="postgres",
    password="aymen6215")
"""

tablename="ML_medicalapp"
Primary_Col_Name='Username'
columns=['Analytics','LoginNumber','Prediction']
client=boto3.client('dynamodb',region_name='us-west-2',aws_access_key_id='AKIAQMQB4MABLCILE6VT',aws_secret_access_key='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')
db=boto3.resource('dynamodb',region_name='us-west-2',aws_access_key_id='AKIAQMQB4MABLCILE6VT',aws_secret_access_key='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')
table=db.Table(tablename)

connection = psycopg2.connect(
    host="mlmedicalapp.chpzat3clawa.us-west-2.rds.amazonaws.com",
    database="postgres",
    user="postgres",
    password="621517Qwerty"
)



cursor=connection.cursor()

app=Flask(__name__)

app.secret_key="secretsir"


@app.route("/")
def home():

    if "user" in session:
        return redirect(url_for("user"))
    else:
        return render_template("index.html")


@app.route("/login", methods=["POST","GET"])
def login():

    if request.method=="POST":
        user=request.form["fname"]
        email=request.form["fname"]
        password=request.form["pword"]


        cursor.execute("select Username,Email,Passwrd from Account where Username='"+user+"' or Email='"+email+"'")

        if len(cursor.fetchall())!=0:

            cursor.execute("select Username,Email,Passwrd from Account where Username='"+user+"' or Email='"+email+"'")
            account=cursor.fetchall()[0]
            if account[0]==user or account[1]==email:

                if account[2]==password:
                    session["user"]=account[0]
                    table.update_item(
                    Key={
                        Primary_Col_Name:session["user"]

                    },
                    UpdateExpression="set LoginNumber=LoginNumber+:val",
                    ExpressionAttributeValues={
                        ':val': 1,

                    }

                    )
                    return redirect(url_for("user"))
                else:
                    flash('Wrong Password')
                    return redirect(url_for("login"))
            else:
                flash('User does not exist, please ')
                return redirect(url_for("login"))
        else:
            flash('User does not exist, please ')
            return redirect(url_for("login"))


    else:
        if "user" in session:


            return redirect(url_for("user"))
        return render_template("login.html")


@app.route("/register", methods=["POST","GET"])
def register():

    if request.method=="POST":
        user=request.form["fname"]
        email=request.form["email"]
        password=request.form["pword"]



        cursor.execute("select Username,Email from Account where Username='"+user+"' or Email='"+email+"'")

        if len(cursor.fetchall())==0:

            res = requests.get('https://ipinfo.io/')
            data = res.json()

            city = data['city']

            location = data['loc'].split(',')
            latitude = location[0]
            longitude = location[1]


            cursor.execute("Insert into Account values('"+user+"','"+email+"','"+password+"',"+latitude+","+longitude+",'"+city+"');")



            connection.commit()


            response=table.put_item(
            Item={
                Primary_Col_Name:user,
                columns[0]:0,
                columns[1]:0,
                columns[2]:0

            }
            )

            session["user"]=user
            Key={
                Primary_Col_Name:session["user"]

            },
            UpdateExpression="set LoginNumber=LoginNumber+:val",
            ExpressionAttributeValues={
                ':val': 1,

            }

            return redirect(url_for("user"))

        else:
            cursor.execute("select Username,Email from Account where Username='"+user+"' or Email='"+email+"'")
            account=cursor.fetchall()[0]
            username=account[0]
            account_email=account[1]
            if user==username and account_email!=email:

                flash('Username already exists')
                return redirect(url_for("register"))
            elif user!=username and account_email==email:
                flash('Email is in use')
                return redirect(url_for("register"))
            elif user==username and account_email==email:
                flash('Username & Email already in use, please ')
                return redirect(url_for("register"))

    else:
        if "user" in session:

            return redirect(url_for("user"))

        return render_template("register.html")


@app.route("/d_analytics")
def diabetes_analytics():
    if "user" in session:

        table.update_item(
        Key={
            Primary_Col_Name:session["user"]

        },
        UpdateExpression="set Analytics=Analytics+:val",
        ExpressionAttributeValues={
            ':val': 1,

        }

        )
        return render_template("d-analytics-user.html",user_name=session["user"])
    else:
        return render_template("d-analytics.html")


@app.route("/hf_analytics")
def heartfailure_analytics():
    if "user" in session:

        table.update_item(
        Key={
            Primary_Col_Name:session["user"]

        },
        UpdateExpression="set Analytics=Analytics+:val",
        ExpressionAttributeValues={
            ':val': 1,

        }

        )
        return render_template("hf-analytics-user.html",user_name=session["user"])
    else:
        return render_template("hf-analytics.html")


@app.route("/lf_analytics")
def liverfailure_analytics():
    if "user" in session:

        table.update_item(
        Key={
            Primary_Col_Name:session["user"]

        },
        UpdateExpression="set Analytics=Analytics+:val",
        ExpressionAttributeValues={
            ':val': 1,

        }

        )

        return render_template("alf-analytics-user.html",user_name=session["user"])
    else:
        return render_template("alf-analytics.html")



@app.route("/prediction")
def prediction():
    return "prediction"


@app.route("/user")
def user():
    if "user" in session:
        return render_template("user.html",user_name=session["user"])
    else:
        return redirect(url_for("home"))

@app.route("/forgot_password", methods=["POST","GET"])
def forgot_password():
    if request.method=="POST":
        user=request.form["fname"]
        email=request.form["email"]


        cursor.execute("select Username,Email,Passwrd from Account where Username='"+user+"' and Email='"+email+"'")

        if len(cursor.fetchall())==0:
            flash('Username ({}) and Email ({}) combination does not exist'.format(user,email))
        else:
            cursor.execute("select Passwrd from Account where Username='"+user+"' and Email='"+email+"'")
            password=cursor.fetchall()[0]
            password=password[0]
            sender=email_sender.ForgotPassword()
            sender.sendEmail(email,user,password)

            flash('Password sent at {}'.format(email))


        return redirect(url_for("forgot_password"))

    else:
        return render_template("forgot_password.html")

@app.route("/logout")
def logout():
    session.pop("user",None)
    return redirect(url_for("home"))

@app.route("/contact")
def contact():

    if "user" in session:
        return render_template("contact-user.html",user_name=session["user"])
    else:
        return render_template("contact.html")


@app.route("/about")
def about():

    if "user" in session:
        return render_template("about-user.html",user_name=session["user"])
    else:
        return render_template("about.html")

@app.route("/myaccount")
def myaccount():


    cursor.execute("select Username,Email,Passwrd from Account where Username='"+session["user"]+"'")
    account=cursor.fetchall()[0]

    username=account[0]
    email=account[1]
    password=account[2]

    return render_template("myaccount.html",user_name=username,password=password,email=email)

@app.route("/changeUsername",methods=["POST"])
def changeUsername():

    if request.method=="POST":

        newname=request.form["fname"]

        cursor.execute("select * from Account where Username ='"+newname+"';")

        if len(cursor.fetchall())==0:

            cursor.execute("UPDATE Account SET Username = '"+newname+"' WHERE Username = '"+session["user"]+"';")
            connection.commit()
            session["user"]=newname

            flash("Username Change Successful")

            return redirect(url_for("myaccount"))
        else:

            flash("Sorry this Username is Not Available")

            return redirect(url_for("myaccount"))


@app.route("/changeEmail",methods=["POST"])
def changeEmail():

    if request.method=="POST":


        newemail=request.form["femail"]

        cursor.execute("select Email from Account where Email ='"+newemail+"';")

        if len(cursor.fetchall())==0:

            cursor.execute("UPDATE Account SET Email = '"+newemail+"' WHERE Username = '"+session["user"]+"';")
            connection.commit()


            flash("Email Change Successful")

            return redirect(url_for("myaccount"))
        else:

            flash("Sorry this Email is Not Available")

            return redirect(url_for("myaccount"))

@app.route("/changePassword",methods=["POST"])
def changePassword():

    if request.method=="POST":

        newpass=request.form["fpassword"]


        cursor.execute("UPDATE Account SET Passwrd = '"+newpass+"' WHERE Username = '"+session["user"]+"';")
        connection.commit()


        flash("Password Change Successful")

        return redirect(url_for("myaccount"))

@app.route("/deleteAccount")
def deletAccount():
    cursor.execute("DELETE FROM Account WHERE Username = '"+session["user"]+"';")
    connection.commit()
    return redirect(url_for("logout"))


@app.route("/diabetes_model",methods=["POST","GET"])
def diabetesModel():
    if request.method=="POST":

        pregnancies=request.form["pregnancies"]
        glucose=request.form["glucose"]
        bp=request.form["bp"]
        skin=request.form["skin"]
        insulin=request.form['insulin']
        bmi=request.form['bmi']
        diabetes=request.form['diabetes']
        age=request.form['age']

        model=pickle.load(open('models/diabetes_model.pkl','rb'))

        prediction=model.predict(np.array([float(pregnancies),float(glucose),float(bp),float(skin),float(insulin),float(bmi),float(diabetes),float(age)]).reshape(1, -1))[0]

        if prediction==1:
            flash("Patient is Diabetic")
        elif prediction==0:
            flash("Patient is Non-Diabetic")

        return redirect(url_for("diabetesModel"))
    else:
        if "user" in session:
            table.update_item(
            Key={
                Primary_Col_Name:session["user"]

            },
            UpdateExpression="set Prediction=Prediction+:val",
            ExpressionAttributeValues={
                ':val': 1,

            }

            )
            return render_template("diabetes_model.html",user_name=session["user"])
        else:
            return render_template("diabetes_model.html",user_name=None)

@app.route("/heartfailure_model",methods=["POST","GET"])
def heartFailureModel():
    if request.method=="POST":

        creatinine_phospoho=request.form["cp"]
        ejection_fraction=request.form["ef"]
        serum_creatinine=request.form["sc"]
        serum_sodium=request.form["ss"]
        sex=request.form['gender']
        smoker=request.form['smoker']

        if sex=="male":
            sex=1
        else:
            sex=0

        if smoker=="yes":
            smoker=1
        else:
            smoker=0

        model=pickle.load(open('models/heartfailure_model.pkl','rb'))

        prediction=model.predict(np.array([float(creatinine_phospoho),float(ejection_fraction),float(serum_creatinine),float(serum_sodium),sex,smoker]).reshape(1, -1))[0]

        if prediction==1:
            flash("Patient has High Chance of Heart Failure")
        elif prediction==0:
            flash("Patient has Low Chance of Heart Failure")

        return redirect(url_for("heartFailureModel"))
    else:



        if "user" in session:
            table.update_item(
            Key={
                Primary_Col_Name:session["user"]

            },
            UpdateExpression="set Prediction=Prediction+:val",
            ExpressionAttributeValues={
                ':val': 1,

            }

            )
            return render_template("heartfailure_model.html",user_name=session["user"])
        else:
            return render_template("heartfailure_model.html",user_name=None)

@app.route("/alf_model",methods=["POST","GET"])
def ALFModel():
    if request.method=="POST":


        input=[]

        input.append(float(request.form["age"]))
        input.append(float(request.form["waist"]))
        input.append(float(request.form["mbp"]))
        input.append(float(request.form["minbp"]))
        input.append(float(request.form["goodchol"]))
        input.append(float(request.form["badchol"]))
        input.append(float(request.form["totalchol"]))


        if request.form['gender']=="male":
            input.append(0)
            input.append(1)
        else:
            input.append(1)
            input.append(0)

        if request.form['region']=="east":
            input.append(1)
            input.append(0)
            input.append(0)
            input.append(0)
        elif request.form['region']=="north":
            input.append(0)
            input.append(1)
            input.append(0)
            input.append(0)
        elif request.form['region']=="south":
            input.append(0)
            input.append(0)
            input.append(1)
            input.append(0)
        elif request.form['region']=="west":
            input.append(0)
            input.append(0)
            input.append(0)
            input.append(1)


        if request.form['obesity']=="No":
            input.append(1)
            input.append(0)
        else:
            input.append(0)
            input.append(1)

        if request.form['Dyslipidemia']=="No":
            input.append(1)
            input.append(0)
        else:
            input.append(0)
            input.append(1)

        if request.form['pvd']=="No":
            input.append(1)
            input.append(0)
        else:
            input.append(0)
            input.append(1)

        if request.form['income']=="low":
            input.append(1)
            input.append(0)
        else:
            input.append(0)
            input.append(1)

        if request.form['poorvision']=="No":
            input.append(1)
            input.append(0)
        else:
            input.append(0)
            input.append(1)

        if request.form['ac']=="No":
            input.append(1)
            input.append(0)
        else:
            input.append(0)
            input.append(1)

        if request.form['ht']=="No":
            input.append(1)
            input.append(0)
        else:
            input.append(0)
            input.append(1)

        if request.form['fht']=="No":
            input.append(1)
            input.append(0)
        else:
            input.append(0)
            input.append(1)

        if request.form['diabetes']=="No":
            input.append(1)
            input.append(0)
        else:
            input.append(0)
            input.append(1)

        if request.form['fd']=="No":
            input.append(1)
            input.append(0)
        else:
            input.append(0)
            input.append(1)


        if request.form['hepa']=="No":
            input.append(1)
            input.append(0)
        else:
            input.append(0)
            input.append(1)

        if request.form['famhepa']=="No":
            input.append(1)
            input.append(0)
        else:
            input.append(0)
            input.append(1)

        if request.form['chron']=="No":
            input.append(1)
            input.append(0)
        else:
            input.append(0)
            input.append(1)


        model=pickle.load(open('models/alf_model.pkl','rb'))

        prediction=model.predict(np.array(input).reshape(1, -1))[0]

        if prediction==1:
            flash("Patient has High Chance of Acute Liver Failure")
        elif prediction==0:
            flash("Patient has Low Chance of Acute Liver Failure")

        return redirect(url_for("ALFModel"))
    else:

        if "user" in session:
            table.update_item(
            Key={
                Primary_Col_Name:session["user"]

            },
            UpdateExpression="set Prediction=Prediction+:val",
            ExpressionAttributeValues={
                ':val': 1,

            }

            )
            return render_template("alf_model.html",user_name=session["user"])
        else:
            return render_template("alf_model.html",user_name=None)


@app.route("/pneumonia", methods=["POST","GET"])
def pneumonia():
    if "user" in session:
        if request.method=="POST":

            if request.files:

                path=request.files['image']


                img_array=np.array(Image.open(path).resize((300,300)).convert('RGB'))

                json_file = open('models/model.json', 'r')
                loaded_model_json = json_file.read()
                json_file.close()
                loaded_model = model_from_json(loaded_model_json)
                # load weights into new model
                loaded_model.load_weights("models/model.h5")


                img_batch = np.expand_dims(img_array, axis=0)
                img_preprocessed = preprocess_input(img_batch)

                if loaded_model.predict(img_preprocessed)[0]>0.5:
                    flash("The Patient Has Pneumonia")
                else:
                    flash("The Patient Does Not Have Pneumonia")


                return render_template("pneumonia.html",user_name=session["user"])

        else:
            return render_template("pneumonia.html",user_name=session["user"])

    else:
        return redirect(url_for("home"))

@app.route("/braintumor", methods=["POST","GET"])
def braintumor():

    if "user" in session:
        if request.method=="POST":

            if request.files:

                path=request.files['image']


                img_array=np.array(Image.open(path).resize((300,300)).convert('RGB'))

                json_file = open('models/braintumor_model.json', 'r')
                loaded_model_json = json_file.read()
                json_file.close()
                loaded_model = model_from_json(loaded_model_json)
                # load weights into new model
                loaded_model.load_weights("models/braintumor_model.h5")


                img_batch = np.expand_dims(img_array, axis=0)
                img_preprocessed = preprocess_input(img_batch)

                if loaded_model.predict(img_preprocessed)[0]>0.5:
                    flash("The Patient Has Brain Tumor")
                else:
                    flash("The Patient Does Dot Have Brain Tumor")


                return render_template("braintumor.html",user_name=session["user"])
        else:

            return render_template("braintumor.html",user_name=session["user"])
    else:
        return redirect(url_for("home"))

if __name__=="__main__":

    app.run(debug=True)
