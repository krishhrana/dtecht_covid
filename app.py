from flask import Flask, flash, redirect, url_for, render_template, request, send_from_directory
from werkzeug.utils import secure_filename
import numpy as np
import re
import sys
import cv2
import os
from tensorflow.keras.models import load_model
import tensorflow as tf


app=Flask(__name__)



# load the model, and pass in the custom metric function
global graph
model = load_model('BestModelUnlocked_0.1_16.h5')

# initialize these variables

import base64
def convertImage(imgData1):
    imgstr = re.search(r'base64,(.*)', str(imgData1)).group(1)
    with open('output.png', 'wb') as output:
        output.write(base64.b64decode(imgstr))


upload_folder='uploads'
allowed_extensions={'txt','pdf','png','jpg','jpeg'}
app.config['upload_folder']=upload_folder

@app.route('/')
def landing_page():
    return render_template("index.html")


@app.route('/aboutus')
def about():
    return render_template("aboutus.html")

@app.route('/login', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            print('No file part')
            return redirect(request.url)
        file = request.files['file']
       

        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            print('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['upload_folder'], filename))
            x=cv2.imread(os.path.join(app.config['upload_folder'], filename))
            x=cv2.resize(x, (224, 224))
            x = tf.keras.applications.densenet.preprocess_input(x)
            x=np.array(x).reshape(1, 224, 224, 3)
            out = np.rint(model.predict(x))
            print(out)
            int_pred=np.argmax(out, axis=-1)
            if int_pred==0:
                k='Positive'
                result='PRESENT'
            elif int_pred==1:
                k='Negative'
                result='ABSENT'
            elif int_pred==2:
                k='Pneumonia'
                result='HIGH BECAUSE YOU HAVE PNEUMONIA'
            user = request.form['fname'] + ' ' + request.form['lname']
        return render_template("page2.html", value=k, result=result, user=user)

    return render_template("login.html")

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['upload_folder'],
                               filename)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = request.form["fname"] + ' ' + request.form['lname']
        print(user)
        return redirect(url_for("user", usr=user))
    else:
        return render_template("login.html")

@app.route("/<usr>")
def user(usr):
    return f"<h1>{usr}</h1>"

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions




if __name__ == "__main__":
    app.run(debug=True)