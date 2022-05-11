from pkgutil import get_data
import os
from sqlalchemy import create_engine
from flask import Flask, jsonify, request
from flask_restful import Api, Resource
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
from funcs import do_train, do_predict, get_data
from credentials import endpoint, port, password, user

########################################################################################

os.chdir(os.path.dirname(__file__))

app = Flask(__name__)
app.config["DEBUG"] = True

@app.route('/', methods=['GET'])
def home():
    return 'Hello'
    # Open the home file
    # with open(os.path.dirname(app.root_path)+'home.md','r') as markdown_file:
    #     # read content 
    #     content = markdown_file.read()
    #     #convert to HTML
    #     return markdown.markdown(content)

@app.route('/api/predict', methods=['GET'])
def predict():
    predictions = do_predict()
    return "Our predictions for the number of people interacting with The Bridge in the following week: " + predictions

@app.route('/api/retrain', methods=['GET'])
def retrain():
    db = get_data(endpoint, port, password, user)
    do_train(db)

@app.route('/endpoint/api/update', methods=['PUT'])
def update_data():
    # connectarse a la db en AWS y guardarla como db
    db = get_data(endpoint, port, password, user)
    # El objeto cursor es el que ejecutará las queries y devolverá los resultados
    cursor = db.cursor()
    # necesita que el usuario le de los datos nuevos (fecha y num. usuarios)
    df = request.args['df']
    # create sqlalchemy engine
    engine = create_engine("mysql+pymysql://{user}:{pw}@{host}/{db}".format(user = user, pw = password, host = endpoint, db = 'country_database'))
    # insertamos todo el dataframe
    df.to_sql(name='new_users', con=engine, if_exists= 'append', index=False)
    # commit los cambios 
    db.commit()

app.run()