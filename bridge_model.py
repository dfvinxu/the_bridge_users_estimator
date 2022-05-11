import os
import pickle
import pandas as pd
import numpy as np
import pymysql
import sqlalchemy
import pathlib
from datetime import date
from flask import Flask, jsonify, request
from sklearn.model_selection import train_test_split
from sklearn.linear_model import Lasso
from sklearn.metrics import mean_absolute_percentage_error
from sktime.forecasting.arima import AutoARIMA
from functions import do_train, do_predict, data_aws
from credentials import endpoint, password, user

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

@app.route('/api/v1/update', methods=['GET'])
def update():
    # nos sacamos todas las tablas de AWS
    engine = sqlalchemy.create_engine("mysql+pymysql://{user}:{pw}@{host}/{db}".format(user = user, pw = password, host = endpoint, db = 'users_web_db'))
    with engine.connect() as con:
        query = """select * from users_web"""
        users_table = pd.read_sql(query, con=con)
        users_table.columns = users_table.columns.str.lower()
        users_table.date = pd.to_datetime(users_table.date)
        query = """select * from predict_users"""
        predictions_table = pd.read_sql(query, con=con)
        query = """select * from new_data"""
        new_data_table = pd.read_sql(query, con=con)
        new_data_table.columns = new_data_table.columns.str.lower()
        new_data_table.date = pd.to_datetime(new_data_table.date)
        con.close()
    # sacamos la siguiente fecha de nuestras predicciones
    next_predicted_date = predictions_table.date.min()
    # ver si nuestra next_predicted_date esta en new_data_table
    # significa que tenemos datos de una fecha predicha
    cond = next_predicted_date in new_data_table.date.values
    if cond:
        # nuestra siguiente fecha predicha esta en la tabla de nuevos datos
        mask = predictions_table.date == next_predicted_date
        y_pred = predictions_table.loc[mask,'users'].values
        # y_true lo obtenemos de agrupar los nuevos datos por semana
        weekly = new_data_table.set_index('date').asfreq('D').groupby(pd.Grouper(freq='W')).sum()
        y_true = weekly.loc[next_predicted_date].values
        # calculamos mape
        mape = mean_absolute_percentage_error(y_true=y_true, y_pred=y_pred)
        # añadimos nuevos datos a la tabla users
        mask = new_data_table.date <= next_predicted_date
        users_table = pd.concat([users_table, new_data_table[mask]])
        # quitamos datos nuevos de new_data_table
        new_data_table = new_data_table[~mask]
        # quitamos la ultima prediccion de predictions_table
        predictions_table = predictions_table[predictions_table.date > next_predicted_date]
        if mape >= 0.2:
            do_train(users_table)
        # push de tablas a AWS
        with engine.connect() as con:
            new_data_table.to_sql(name = 'new_data', con=con, if_exists='replace', index=False)
            users_table.to_sql(name='users_web', con=con, if_exists='replace', index=False)
            predictions_table.to_sql(name='predict_users', con=con, if_exists='replace', index=False)
        con.close()

    return 'MAPE: {}'.format(mape) if cond else 'no new data available, next date {}'.format(next_predicted_date)

@app.route('/api/v1/reset', methods=['GET'])
def reset():
    reset_date = '2022-04-03'
    engine = sqlalchemy.create_engine("mysql+pymysql://{user}:{pw}@{host}/{db}".format(user = user, pw = password, host = endpoint, db = 'users_web_db'))
    with engine.connect() as con:
        query = """select * from full_data"""
        data = pd.read_sql(query, con=con)
        data.columns = data.columns.str.lower()
        data.date = pd.to_datetime(data.date)
        con.close()
    # nuevos datos > reset date
    mask = data.date > reset_date
    nuevos_datos = data[mask]
    datos = data[~mask]
    # reiniciar tablas en la base de datos
    with engine.connect() as con:
        nuevos_datos.to_sql(name = 'new_data', con=con, if_exists='replace', index=False)
        datos.to_sql(name='users_web', con=con, if_exists='replace', index=False)
        con.close()
    # entrenariamos el modelo
    do_train(datos)
    # predeciriamos y actualizariamos predicciones
    n_weeks = 4
    predictions = do_predict(n_weeks)
    predictions.index.names = ['date']
    pred_table = predictions.reset_index()
    pred_table.users = pred_table.users.astype(int)
    # mandamos el dataframe a la nube
    with engine.connect() as con:
        pred_table.to_sql(name = 'predict_users', con = con, if_exists='replace', index=False)
        con.close()
    return 'user data reset to {}'.format(reset_date)

@app.route('/api/v1/get_table_new_data', methods=['GET'])
def new_data_table():
    engine = sqlalchemy.create_engine("mysql+pymysql://{user}:{pw}@{host}/{db}".format(user = user, pw = password, host = endpoint, db = 'users_web_db'))
    with engine.connect() as con:
        query = """select * from new_data"""
        new_data_table = pd.read_sql(query, con=con)
        new_data_table.columns = new_data_table.columns.str.lower()
        new_data_table.date = pd.to_datetime(new_data_table.date)
        con.close()
    new_data_table.date = new_data_table.date.dt.strftime('%Y-%m-%d')
    res_json = new_data_table.to_dict(orient = 'records')
    return jsonify(res_json)

@app.route('/api/v1/get_table_predictions', methods=['GET'])
def predictions_table():
    engine = sqlalchemy.create_engine("mysql+pymysql://{user}:{pw}@{host}/{db}".format(user = user, pw = password, host = endpoint, db = 'users_web_db'))
    with engine.connect() as con:
        query = """select * from predict_users"""
        predictions_table = pd.read_sql(query, con=con)
        con.close()
    predictions_table.date = predictions_table.date.dt.strftime('%Y-%m-%d')
    res_json = predictions_table.to_dict(orient = 'records')
    return jsonify(res_json)

@app.route('/api/v1/get_table_users', methods=['GET'])
def users_table():
    n_users = int(request.args.get('n_users', None))
    engine = sqlalchemy.create_engine("mysql+pymysql://{user}:{pw}@{host}/{db}".format(user = user, pw = password, host = endpoint, db = 'users_web_db'))
    with engine.connect() as con:
        query = """select * from users_web"""
        users_table = pd.read_sql(query, con=con)
        users_table.columns = users_table.columns.str.lower()
        users_table.date = pd.to_datetime(users_table.date)
        con.close()
    users_table.date = users_table.date.dt.strftime('%Y-%m-%d')
    res_json = users_table[-n_users:].to_dict(orient = 'records')
    return jsonify(res_json)

app.run()
