from datetime import date
from flask import Flask, jsonify, request
import os
import pickle
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import Lasso
from sklearn.metrics import mean_absolute_percentage_error
import numpy as np
import pymysql
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
        n_weeks = int(request.args.get('n_weeks', None))
        do_predict(n_weeks)
        return 'predictions done'

app.run()
