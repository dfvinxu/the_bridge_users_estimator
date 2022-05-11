import os
import pickle
import pandas as pd
import numpy as np
import pymysql
import sqlalchemy
from datetime import date
from flask import Flask, jsonify, request
from sklearn.model_selection import train_test_split
from sklearn.linear_model import Lasso
from sklearn.metrics import mean_absolute_percentage_error
from sktime.forecasting.arima import AutoARIMA
from functions import do_train, do_predict, data_aws
from credentials import endpoint, password, user

os.chdir(os.path.dirname(__file__))

app = Flask(__name__)
app.config['DEBUG'] = True

@app.route("/", methods=['GET'])
def hello():
    return "THE BRIDGE MARKETING ESTIMATOR"

@app.route('/api/v1/train', methods=['GET'])
def train():
    data = data_aws(endpoint, password, user)
    do_train(data)
    return 'trained'
    

@app.route('/api/v1/predict', methods=['GET'])
def predict():
    # obtenemos el numero de semanas
    n_weeks = int(request.args.get('n_weeks', None))
    # con ello realizamos las predicciones, devuelve un dataframe
    predictions = do_predict(n_weeks)
    predictions.index.names = ['date']
    pred_table = predictions.reset_index()
    pred_table.users = pred_table.users.astype(int)
    # mandamos el dataframe a la nube
    engine = sqlalchemy.create_engine("mysql+pymysql://{user}:{pw}@{host}/{db}".format(user = user, pw = password, host = endpoint, db = 'users_web_db'))
    with engine.connect() as con:
        pred_table.to_sql(name = 'predict_users', con = con, if_exists='replace')
        con.close()
    # pasa la tabla a json
    pred_table.date = pred_table.date.dt.strftime('%Y-%m-%d')
    preds_json = pred_table.to_dict(orient = 'records')
    return jsonify(preds_json)

app.run()
