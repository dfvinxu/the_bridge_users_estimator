from flask import Flask, jsonify, request
from flask_restful import Api, Resource
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
import pandas as pd
import requests
import pickle
import os
import markdown
from funcs import do_train

## Connect to database
import mysql.connector
import sys
import boto3
import os
import pymysql

endpoint = "web-users.czjoi0srhr5i.eu-west-3.rds.amazonaws.com"
port = "3306"
password = "2AWS"
user = "admin"



cur.execute("""SELECT now()""")

from sqlalchemy import create_engine

# create sqlalchemy engine

engine = create_engine("mysql+pymysql://{user}:{pw}@{host}/{db}".format(user = user, pw = password, host = endpoint, db = 'users_web_db'))
# engine = create_engine("mysql+pymysql://my_user:my_password@my_host/my_database")



app = Flask(__name__)
app.config["DEBUG"] = True

#os.chdir(os.path.dirname(__file__))

@app.route('/', methods=['GET'])
def home():

    # Open the home file
    with open(os.path.dirname(app.root_path)+'home.md','r') as markdown_file:
        # read content 
        content = markdown_file.read()
        #convert to HTML
        return markdown.markdown(content)

@app.route('/api/predict', methods=['GET'])
def predict():
    model = pickle.load(open('arima.pickle','rb'))

    date = request.args['date']
    users = request.args['users']

    if date is None or users is None:
        return "Args empty, the data are not enough to predict"
    else:
        prediction = model.predict([[date, users]])
    
    return jsonify({'predictions': prediction[0]})

@app.route('/api/retrain', methods=['GET'])



def retrain():
    data = pd.read_csv('data/users_web.csv', index_col=0)

    X_train, X_test, y_train, y_test = train_test_split(data['date']),
                                                    data['users'],
                                                    test_size = 0.20,
                                                    random_state=42)

    model = Lasso(alpha=6000)
    model.fit(X_train, y_train)

    pickle.dump(model, open('ad_model.pkl', 'wb'))

    return "Model retrained. New evaluation metric MAPE: " + str(np.sqrt(mean_squared_error(y_test, model.predict(X_test))))

@app.route('endpoint/api/update', methods=['PUT'])
def update_data():
    # connectarse a la db en AWS y guardarla como db
    db = pymysql.connect(host = endpoint,
                        user = user,
                        password = password,
                        cursorclass = pymysql.cursors.DictCursor)
    # El objeto cursor es el que ejecutará las queries y devolverá los resultados
    cursor = db.cursor()
    # necesita que el usuario le de los datos nuevos (fecha y num. usuarios)
    df = request.args['df']
    # insertamos todo el dataframe
    df.to_sql(name='new_users', con=engine, if_exists= 'append', index=False)
    # commit los cambios 
    db.commit()

@app.update_model('/api/updatemodel', methods=['GET'])
def new_model():
    # necesita leer los datos para crear un modelo nuevo
    data = pd.read_csv('data/Advertising.csv', index_col=0)
    # train new model and save it into new pickle


app.run()