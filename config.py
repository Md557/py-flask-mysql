BASIC_AUTH_USERNAME = 'user'
BASIC_AUTH_PASSWORD = 'pass'

#add for csv import
#added for csv import:
UPLOAD_FOLDER = './uploads' #used for send_from_directory serving #. is the directory where starting python.  On webserver, this will be one level deeper
#from os.path import join, dirname, realpath #UPLOADS_PATH = join(dirname(realpath(__file__)), 'static/uploads/..')

#UPLOAD_FOLDER = UPLOAD_FOLDER #only used on localhost, not used anymore with Heroku MYDIR
SECRET_KEY = b'_4a35%"Fgo4z\nxnc]/'


BASIC_AUTH_FORCE = False #enfore entire site
#@basic_auth.required #for individual routes when entire site is not enforced (Place after @app.route('/') line)

USER='user'
PASSWORD='pass'
HOST='localhost'
PORT='3306'
DB_NAME='projectBlue'
#or pip install  mysqlclient-1.4.6-cp37-cp37m-win32.whl
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://%s:%s@%s:%s/%s'%(USER,PASSWORD,HOST,PORT,DB_NAME)

