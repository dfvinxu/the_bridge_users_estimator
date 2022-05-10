from flask import Flask, jsonify, request
from flask_restful import Api, Resource
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
import pandas as pd
import requests
import pickle
import os
import markdown

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
    model = pickle.load(open('ad_model.pkl','rb'))

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

@app.route('/api', methods=['PUT'])
def update_data():
    # necesita leer los datos para modificarlos?
    data = pd.read_csv('data/Advertising.csv', index_col=0)
    # necesita que el usuario le de los datos nuevos (fecha y num. usuarios)
    date = request.args['date']
    users = request.args['users']

@app.update_model('/api/updatemodel', methods=['GET'])
def new_model():
    # necesita leer los datos para crear un modelo nuevo
    data = pd.read_csv('data/Advertising.csv', index_col=0)
    # train new model and save it into new pickle


app.run()