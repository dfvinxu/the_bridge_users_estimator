# The Bridge Users Estimator API Documentation

1. Overview
The Bridge Users Estimator API is a JSON-based OAuth2 API. All requests are made to endpoints beginning: https://

Developer agreement
By using The Bridge Users Estimator API, you agree to our terms of service.

2. Resources
The API is RESTful all requests must be made using https.

3.1. Home
Getting the homepage with overview of the API and its creators

GET https://

3.2. Prediction
Returns the prediction of the number of users for the following 7 days 

GET https://

3.3. Update Data
Allows for new data to be inputted. When there is newly available data on number of users in a day, the user can input it and the Data Frame on RDS (on AWS) will be automatically updted.

GET https://

3.4. Retrain
Retrains the AUTOARIMA after new data has been inputted, the model is then saved in a file called arima.pickle.

GET https://

___________________________________________________________

Contributors: Alfonso, David, Hugo, Nicole, Oscar, Paco, Gonzalo

