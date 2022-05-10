from datetime import date
from flask import Flask, jsonify, request
import os
import pickle
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import Lasso
from sklearn.metrics import mean_absolute_percentage_error
import numpy as np

os.chdir(os.path.dirname(__file__))

app = Flask(__name__)
app.config['DEBUG'] = True

@app.route("/", methods=['GET'])
def hello():
    return "THE BRIDGE MARKETING ESTIMATOR"


@app.route('/api/v1/predict', methods=['GET'])
def predict():

    model = pickle.load(open('ad_model.pkl','rb'))
    
    date = request.args.get('Date', None)
    users = request.args.get('Users', None)

    if date is None or users is None:
        return "Args empty, the data are not enough to predict"
    else:
        prediction = model.predict([[date,users]])
    
    return jsonify({'predictions': prediction[0]})

@app.route('/api/v1/retrain', methods=['PUT'])
def retrain():
    data = pd.read_csv('data/users_web.csv', index_col=0)

    X_train, X_test, y_train, y_test = train_test_split(data.drop(columns=['Date']),
                                                    data['Date'],
                                                    test_size = 0.20,
                                                    random_state=42)

    model = Lasso(alpha=6000)
    model.fit(X_train, y_train)

    pickle.dump(model, open('ad_model.pkl', 'wb'))

    return "Model retrained. New evaluation metric MAPE: " + str(np.sqrt(mean_absolute_percentage_error(y_test, model.predict(X_test))))

app.run()