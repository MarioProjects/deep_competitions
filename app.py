from __future__ import division, print_function
# coding=utf-8
import os
import numpy as np
import pandas as pd

# Flask utils
from flask import Flask, redirect, url_for, request, render_template
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from gevent.pywsgi import WSGIServer
# Para poder utilizar las sessiones debemos importar...
from flask import session, escape

import json

# Ignore warnings
import sys
import warnings

if not sys.warnoptions:
    warnings.simplefilter("ignore")

""" --- IMPORT LIBRARIES --- """

import numpy as np
import pickle
import pathlib
import time
from datetime import datetime

import torch
from torch import nn, optim
from torch.autograd.variable import Variable
import torch.nn.functional as F

# Para utilizar nuestras bases de datos basadas en SQl instalamos flask_sqlalchemy
from flask_sqlalchemy import SQLAlchemy

# We establish a seed for the replication of the experiments correctly
seed = 0
torch.manual_seed(seed=seed)
torch.cuda.manual_seed(seed=seed)

# Con os.path.abspath(os.getcwd()) tomamos la ruta absoluta de nuestro entorno de trabajo actual (pwd)
# PODEMOS ACCEDER A NUESTRA BASE DE DATOS A TRAVES DE CONSOLA -> sqlite3 users.db
# Alli si posteriormente escribimos .schema nos muestra el esquema de la DB y podemos hacer operaciones
dbdir = "sqlite:///" + os.path.abspath(os.getcwd()) + "/users.db"
print(dbdir)
# Define a flask app
app = Flask(__name__)

# DEBEMOS CREAR UNA LLAVE SECRETA PARA QUE OTRA GENTE NO PUEDA CAMBIAR EL VALOR DE LAS VARIABLES DE SESSION
app.secret_key = "1234"

# Necesitamos configurar la aplicacion y decirle donde estara nuestra db
app.config["SQLALCHEMY_DATABASE_URI"] = dbdir
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False # Para que no salgan notificaciones molestas
# Referimos nuestra base de datos pasandole nuestra aplicacion
db = SQLAlchemy(app)

current_page = "index"
ALLOWED_EXTENSIONS = set(['npy'])

# Vamos a crear a traves de una clase de Python nuestra tabla/esquema en la base de datos
class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True) # Creamos un identificador unico clave primaria
    # Creamos una columna para el nombre de usuario que sea unica (no usernames iguales y que no este vacio/null)
    username = db.Column(db.String(50), unique=True, nullable=False)
    # Algo parecido para el password
    password = db.Column(db.String(80), nullable=False)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_username():
    try: current_username = session["username"]
    except: current_username = ""
    return current_username


def trigger_action(action):
    # Main page
    global current_page

    if current_page == "mnist": return mnist(action=action)
    if current_page == "cifar10": return cifar10(action=action)

    data_mnist = load_results("mnist_results.txt")
    mnist_info = display_results(data_mnist, 3)
    data_cifar10 = load_results("cifar10_results.txt")
    cifar10_info = display_results(data_cifar10, 3)

    # Si no accedemos al endpoint a traves de GET o POST es porque se ha accedido de forma
    # 'normal' a traves del navegador y hacemos visible la vista signup.html con el formulario
    return render_template("index.html", mnist_info=mnist_info, cifar10_info=cifar10_info, show_modal={"modal_type":action}, username={"username":get_username()})

# Las rutas definidas mediante flask tienen como predeterminado recibir una peticion de tipo GET
# Pero la accion de signup se realiza mediante POST y debemos preprarar nuestra ruta
# Podemos definir diferentes puntos de entrada con el mismo nombre que hagan cosas diferentes
# dependiendo si se llama por GET o POST pero en este caso vamso a aceptar las dos peticiones
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method=="POST": # Si venimos de hacer submit en un formulario
        # Podemos acceder a los valores de lo que nos llega del formulario a traves
        # de request con request.form[input_form_name]
        hashed_pw = generate_password_hash(request.form["password"], method="sha256") # Ciframos el password
        # Creamos un registro para añadirlo a la base de datos
        new_user = Users(username=request.form["username"], password=hashed_pw)
        db.session.add(new_user)
        try:
            db.session.commit()
            # Devolvemos una vista recordad (deberia ser render_template)
            # Aqui nos basta con sacar que ha ido todo bien
            return trigger_action("register_ok")
            #return "You've registered successfully"
        except: # Podemos tener un error por ejemplo duplicando usernames
            pass # Se gestiona finalizando abajo con wrong_action()

    return trigger_action("register_error")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method=="POST": # Si venimos de hacer submit en un formulario
        ## Primero comprobamos que el usuario exista en la base de datos
        user = Users.query.filter_by(username=request.form["username"]).first()
        # SI ha encontrado usuario y el usuario tiene el password como el introducido...
        # Es importante el orden de check_password_hash ya que hace el hash al segundo parametro
        if user and check_password_hash(user.password, request.form["password"]):
            # Creamos la variable de session que se llamara 'username' y tomar el valor del objeto de la base de datos
            # proveniente de la query
            session["username"] = user.username
            #return "You are logged in"
            return trigger_action("login_ok")
        else:
            return trigger_action("login_error")

    return trigger_action("login_ok")


## Vamos a crear una ruta para eliminar la variable de session username y asi desloguearnos
@app.route("/logout")
def logout():
    # Para desloguearnos hacemos un session.pop(variableSession, valorPorDefecto)
    session.pop("username", None)
    # Devolvemos algo a la vista
    #return "You are logged out"
    return trigger_action("logout_ok")


def load_results(db, sorted_values="score"):
    if not os.path.isfile(db):
        f=open(db,"w+")
        f.write("name,score,utc")
        f.close()
        print("'{}' No exisitia! Creada.".format(db))
        return None
    else:
        data = pd.read_csv(db, sep=",")
        if sorted_values!="":
            data = data.sort_values(by=[sorted_values], ascending=False)
        return data

def display_results(results, items=-1, precision=5):
    # results: dataframe de pandas que se supone ordenado para ser impreso
    # items: Número de elementos a mostrar -> -1 muestra todos
    if results is None: pass
    else:
        users, result, iters = [], {}, 0
        for index, row in results.iterrows():
            #result.append([row['name'],row['score'],row['utc']])
            if row["name"] in users: continue # NO añadimos su resultado a la tabla
            result_time = datetime.fromtimestamp(row['utc']).strftime('%Y-%m-%d %H:%M:%S')
            entries = results.groupby('name').count().loc[row['name']]["score"]
            result[str(iters)] = [row['name'], round(row['score'],precision), str(entries), result_time]
            users.append(row['name'])

            iters+=1
            if iters==items:break
        return result


@app.route('/mnist')
def mnist(action={}):
    global current_page
    current_page = "mnist"
    # Main page
    data_mnist = load_results("mnist_results.txt")
    mnist_info = display_results(data_mnist, -1)
    return render_template('mnist.html', mnist_info=mnist_info, cifar10_info={}, show_modal={"modal_type":action}, username={"username":get_username()})


@app.route('/mnist_upload', methods = ['GET', 'POST'])
def mnist_upload(action={}):
    if request.method == 'POST':
        f = request.files['file']
        if f and allowed_file(f.filename):
            file_path = "tmp/" + secure_filename(f.filename)
            f.save(file_path)
            
            return 'file uploaded successfully'

        else: return trigger_action("wrong_extension")
    return "You have broken something?! :/"



@app.route('/cifar10')
def cifar10(action={}):
    global current_page
    current_page = "cifar10"
    # Main page
    data_cifar10 = load_results("cifar10_results.txt")
    cifar10_info = display_results(data_cifar10, -1)
    return render_template('cifar10.html', mnist_info={}, cifar10_info=cifar10_info, show_modal={"modal_type":action}, username={"username":get_username()})


@app.route('/', methods=['GET'])
def index():
    global current_page
    current_page = "index"
    # Main page
    data_mnist = load_results("mnist_results.txt")
    mnist_info = display_results(data_mnist, 3)
    data_cifar10 = load_results("cifar10_results.txt")
    cifar10_info = display_results(data_cifar10, 3)

    return render_template('index.html', mnist_info=mnist_info, cifar10_info=cifar10_info, username={"username":get_username()})

if __name__ == '__main__':
    db.create_all() # Comprueba si la db esta creada o no (si no lo esta la crea)
    # Serve the app with gevent
    app.debug = True
    port = int(os.environ.get('PORT', 5000))
    print("\n########################################")
    print('--- Running on port {} ---'.format(port))
    print("########################################\n")
    http_server = WSGIServer(('', port), app)
    http_server.serve_forever()