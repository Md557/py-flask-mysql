# Python API Development with Flask & Mysql


# Setup
These instructions assume knowledge of flask, so installing flask will be skipped
Optional flask-basicauth module is included, username/pass set in *config.py* (default: user/pass)
The main *data.json* file was split up into 3 files (*data0-data2.json*) to allow easier json.load parsing within python for first time records setup

## Install required modules
pip install pymysql; 
pip install flask_sqlalchemy; 
pip install sqlalchemy;
pip install mysql-connector-python; 
pip install flask-basicauth;


## Mysql setup
Setup assumes mysql installed on localhost, 
__USER,PASS,HOST,PORT__ & DB URI's set in *config.py*

Two database connections are used concurrently:
__Connection # 1:__ *Notes* table through pymysql, ORM & SQLAlchemy, 
    Modules: *notes.py* file
    
__Connection # 2__: All tables (*Notes* & *Projects*) through mysql-connector-python & cursor (no ORM)
    Modules: *main.py* file

## First time database setup: 
A boolean flag *firstTimeSetup* is set to *True* and will create the database, tables, and populate the 3 records from the 3 json files (using connection *mysql-connector*).  After running the  app the first time, this flag can optionally be set to False.  If the database name is changed from *projectBlue*, it should be changed within *config.py*. For local deployment, change the flag in __main__ in *main.py* and for cloud deployment, change the flag variable in *wsgi.py*

## Deployment
Can be set up locally for testing with __>> python main.py__  
Then navigate your browser to localhost displayed by python in the commandline (i.e. http://127.0.0.1:Port/)  
## Frontend 
included at url path '/' allows API testing and displaying of results

## Cloud Deployment
Can be set up in cloud with Gunicorn, __>> gunicorn wsgi__  
For cloud deployment, *requirements.txt* will need to be added (*pip3 freeze > requirements.txt*) and SECRET_KEY changed

##  API Documentation
API routes are documented within the *main.py* file, and linked to within the frontend (URL /) and include:

## Project list:
'/API/all', methods = ["GET"]

## Project update:
'/API/update', methods = ["PUT","PATCH"]
(Currently only PUT is used)

## Create note:
'/API/notes/add', methods = ["POST"]

## Update note:
'/API/notes/update', methods = ["PUT"]

## Delete note:
'/API/notes/delete/*var1*', methods = ["DELETE"]
*var1* is the note_id to be deleted

## Example of data types assumed to be sent from the frontend can be viewed within the frontend or frontend/js/update.js


## Example images at /example_images