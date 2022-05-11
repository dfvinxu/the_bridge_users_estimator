from pkgutil import get_data
import os
from sqlalchemy import create_engine
from flask import Flask, jsonify, request
from flask_restful import Api, Resource
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
from functions import do_train, do_predict, data_aws
from credentials import endpoint, password, user

########################################################################################

os.chdir(os.path.dirname(__file__))

app = Flask(__name__)
app.config["DEBUG"] = True

@app.route('/', methods=['GET'])
def home():
    return "THE BRIDGE MARKETING ESTIMATOR"
    # Open the home file
    # with open(os.path.dirname(app.root_path)+'home.md','r') as markdown_file:
    #     # read content 
    #     content = markdown_file.read()
    #     #convert to HTML
    #     return markdown.markdown(content)

@app.route('/api/predict', methods=['GET'])
def predict():
    n_weeks = int(request.args.get('n_weeks', None))
    predictions = do_predict(n_weeks)
    x = predictions.to_json()
    return "Our predictions for the number of people interacting with The Bridge in the following week in the format date : number users: " + str(x)

@app.route('/api/v1/train', methods=['GET'])
def retrain():
    db = data_aws(endpoint, password, user)
    do_train(db)
    return "The model has been retrained with the new data and saved in a file called autoarima"

@app.route('/endpoint/api/update', methods=['PUT'])
def update_data():
    # connectarse a la db en AWS y guardarla como db
    db = get_data(endpoint, password, user)
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
    return "The data has been updated"

app.run()