from __future__ import print_function
from flask import Flask, json, Markup, make_response, render_template, request, send_from_directory
from flask import flash, redirect, url_for
from flask_basicauth import BasicAuth

#pip install pymysql
#pip install flask_sqlalchemy
from flask_sqlalchemy import SQLAlchemy
import pymysql

#pip install mysql-connector-python
import mysql.connector
from mysql.connector import errorcode

import os
import time
from datetime import datetime


app = Flask(__name__, template_folder='./templates/', static_folder='./frontend/',    static_url_path='/') 

basic_auth = BasicAuth(app)
app.config.from_pyfile('config.py')
from config import USER, PASSWORD, HOST, PORT, DB_NAME
#cnx.close()
MYDIR = os.path.dirname(__file__) #add for heroku 

#####################################################################################
db=SQLAlchemy(app) #Connection # 1: Notes database through pymysql, ORM & SQAlchemy
from Notes import * # moved Connection #1 class, ORM to separate file (notes.py)  
#####################################################################################


################################################################################################
#Connection #2: All databases (Notes & Project) through mysql-connector-python & cursor (no ORM)
# requires refreshing data with commit before running query
global cnx 
def connectToDB():  
    global cnx
    cnx = mysql.connector.connect(user=USER, password=PASSWORD, host=HOST, port=PORT)
    cursor= cnx.cursor()   
    try:
        cursor.execute("USE {}".format(DB_NAME))
    except:
        print("could not connect to database")
    cursor.close()
    
#############################################################
### For Gunicorn server, can call connectToDB() at this point, 
###  since will not be called via main

#############################################################
### Create database (first time setup)
#############################################################
def createProjectDB():
    global cnx
    cursor= cnx.cursor()
    
    try:
        cursor.execute("CREATE DATABASE {}".format(DB_NAME))
    except mysql.connector.Error as err:
        print("Will not create database, may already exist database: {}".format(err))
        try:
            cursor.execute("USE {}".format(DB_NAME))
        except:
            print("could not connect to database")
    cnx.commit()
    cursor.close()
#############################################################
### Create tables (first time setup)
#############################################################

def createTables():
    global cnx
    cursor= cnx.cursor()
    
    TABLES={} #new dictionary
    TABLES['projects'] = (
        "CREATE TABLE projects(id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,"
        "  title VARCHAR(200) NOT NULL,"
        "  start_date VARCHAR(19) NOT NULL,"
        "  status enum('In Progress','Pending','Complete') NOT NULL,"
        "  active enum('true','false') NOT NULL,"
        "  assignee VARCHAR(30) NOT NULL,"    
        "  percent_complete int(3) NOT NULL,"
        "  details_requestor_id int(4) NOT NULL,"
        "  details_requestor_name varchar(30) NOT NULL,"
        "  details_requestor_department varchar(50) NOT NULL,"
        "  details_summary varchar(1500) NOT NULL,"
        "  details_justification varchar(1500) NOT NULL)"    
        )
    TABLES['notes'] = (
        "CREATE TABLE notes(project_id INT NOT NULL ,"
        " note_id INT NOT NULL PRIMARY KEY,"
        "  note VARCHAR(2000) NOT NULL)"
        )

    #print(TABLES['projects'])
    for table_name in TABLES:
        try:
            table_schema = TABLES[table_name]
            print("Creating table {}: ".format(table_name))
            cursor.execute(table_schema)
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                print("already exists.")
            else:
                print(err.msg)
    cnx.commit()
    cursor.close()
    
#############################################################
### Add initial records (first time setup)
#############################################################
def addInitialRecords():
    global cnx
    cursor=cnx.cursor()
    for recordNum in range(3):
        print("Record Number:",recordNum)
        record=open("data{}.json".format(recordNum))
        p=json.load(record)
        details=p['details']
        notes=p['notes']
        #print("details:",details)
        #print("notes:",notes,"\n\n")

        #print(p)
        #print(p.keys())

        #for keys in p:
            #print(keys)
            #print(p[keys])
        statement=("INSERT INTO projects"
                     "(id, title, start_date, status, active, assignee, percent_complete,details_requestor_id,details_requestor_name,details_requestor_department,details_summary,details_justification )"
                     "VALUES ('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')"

                     )
        try:
            insert_statement=statement%(p['id'],p['title'],p['start_date'],p['status'],p['active'],p['assignee'],p['percent_complete'],details['requestor']['id'],details['requestor']['name'],details['requestor']['department'],details['summary'],details['justification'])
            #print("\n\ninsert_statement")
            #print(insert_statement)
            #print("\n\n")
            cursor.execute(insert_statement)
        except mysql.connector.Error as err:
            print("exception while inserting records into projects, ", err.msg)
        for keys in p['notes']:
            print("Notes i=",keys)
            statement=("INSERT INTO notes"
                      "(project_id,note_id,note) VALUES ('%s','%s','%s')"%(p['id'],keys['id'],keys['note'])

                      )
            try:
                cursor.execute(statement)
            except:
                print("Unable to add some notes to database")
    cnx.commit()         
    cursor.close()

    

#############################################################
### Frontend route, for using test options via buttons
#############################################################    
@app.route('/', methods = ["GET"])
@basic_auth.required
def serve_update_test():
    return render_template("update_test.html")


#############################################################
### API route, for adding notes
############################################################# 
@app.route('/API/notes/add', methods = ["POST"])
@basic_auth.required
def add_note_api():
    try:    
        data={} #Start of parsing request data      
        if request.is_json:
            print("request is json, will use get_json() method")
            data=request.get_json()
            print(data)
        else:
            print("Request was not json, using bytes & get_data() with json.loads() methods")
            data_s_bytes=request.content_length
            print("content length=%s"%(data_s_bytes))
            #decode data only if bytes < 100kb # Adjust this as necessary
            if data_s_bytes<100000:
                #print(request.get_data(as_text=True)) #cache=True, as_text=False, parse_form_data=False
                data_s=request.get_data( as_text=True)
                print(data_s)
                data=json.loads(data_s)
                print(data) 
        #End of parsing request data
        projectID=None
        noteID=None
        note=None
        for keys in data: #for keys,values in data.items()
            print("keys: ",keys," data:",data[keys])
            if keys=="Project_id":
                projectID=data[keys]
            if keys=="Note_id":
                noteID=data[keys]
            if keys=="note":
                note=data[keys]
                
        if projectID and noteID and note:
            if getNoteById(noteID):
                print("note %s already exists, returning"%noteID,400)
                return("note %s already exists, returning 400"%noteID,400)                
            addNote(projectID,noteID,note)
            return ("note added!", 200)        
        else:
            return("could not parse all note fields",400)
    except:
        print("could not add note, exception occured, returning ",400)
        #Should return reason why
        return ("Could not add note, exception occured", 400)
    
#############################################################
### API route, for updating notes
#############################################################     
@app.route('/API/notes/update', methods = ["PUT"])
@basic_auth.required
def update_note_api():
    try:    
        data={} #Start of parsing request data      
        if request.is_json:
            print("request is json, will use get_json() method")
            data=request.get_json()
            print(data)
        else:
            print("Request was not json, using bytes & get_data() with json.loads() methods")
            data_s_bytes=request.content_length
            print("content length=%s"%(data_s_bytes))
            #decode data only if bytes < 100kb
            if data_s_bytes<100000:
                #print(request.get_data(as_text=True)) #cache=True, as_text=False, parse_form_data=False
                data_s=request.get_data( as_text=True)
                print(data_s)
                data=json.loads(data_s)
                print(data) 
        #End of parsing request data
        projectID=None
        noteID=None
        note=None
        for keys in data:
            print("keys: ",keys," data:",data[keys])
            if keys=="Project_id":
                projectID=data[keys]
            if keys=="Note_id":
                noteID=data[keys]
            if keys=="note":
                note=data[keys]
                
        if projectID and noteID and note:
            if getNoteById(noteID):
                print("note %s exists, attempting to update"%noteID)
                updateNote(projectID,noteID,note)
                return ("note updated!", 200)      
            else:
                print("note %s was not found, will not add or update, returning "%noteID,400)
                return("note %s was not found, will not add or update"%noteID,400)
                
        else:
            print("could not parse all note fields during update, returning ",400)
            return("could not parse all note fields during update",400)
    except:
        print("could not update note, exception occured, returning ",400)
        return ("Could not update note, exception occured", 400)

    
#############################################################################
### API route, for deleting notes. Takes ID to delete in URL (no JSON received)
#############################################################################     
@app.route('/API/notes/delete/<var1>', methods = ["DELETE"])
@basic_auth.required
def delete_note_api(var1): #var1=Note ID
    try:
        note=getNoteById(var1)
        if note:
            deleteNote(var1) 
            print ("Note# %s deleted, returning "%(var1),200)
            return ("Note# %s deleted"%(var1),200)
        else:
            print ("Note# %s was not found, returning"%(var1),400)
            return ("Note# %s was not found"%(var1),400)

    except:
        print ("Exception occured while deleting Note# %s, returning"%(var1),400)
        return ("Exception occured while deleting Note# %s"%(var1),400)

#############################################################
### API route, for displaying all projects & notes
#############################################################     
@app.route('/API/all', methods = ["GET"]) #Get all records
@basic_auth.required
def get_all_projects():
    global cnx
    if not cnx:
        connectToDB()
    cursor = cnx.cursor()
    try:
        cnx.commit() #cursor.execute("FLUSH TABLES projects")
    except:
        print("WARNING: API/all route, could not refresh mysql-connector connection")
    #######################################################
    ######### RETRIEVE Projects and set up empty Notes list
    #######################################################
    projectList=[]
    project_id_list=[]
    select="SELECT id, title, start_date, status, active, assignee, percent_complete, details_requestor_id, details_requestor_name,details_requestor_department,details_summary,details_justification FROM projects"
    result=cursor.execute(select)
    print("result of select")
    for (id,title,start_date,status,active,assignee,percent_complete,details_requestor_id,details_requestor_name,details_requestor_department,details_summary,details_justification) in cursor:
        details_requestor={"id":details_requestor_id,"name":details_requestor_name,"department":details_requestor_department}
        details={"requestor":details_requestor,"summary":details_summary,"justification":details_justification}

        dict_cur={"id":id,"title":title,"start_date":start_date,"status":status,"assignee":assignee,"percent_complete":percent_complete,"details":details,"notes":[]}

        projectList.append(dict_cur)
        print("\n\nid,title, etc:", id,title,start_date,status,active,assignee,percent_complete,details_requestor_id,details_requestor_name,details_requestor_department,details_summary,details_justification)
        project_id_list.append(id)
    #############################
    ######### ADD NOTES to project list
    ##############################
    select=("SELECT a.id, b.project_id, b.note_id, b.note "
            "FROM projects a "
            "INNER JOIN notes b ON a.id=b.project_id")
    cursor.execute(select)
    noteArchive = cursor.fetchall()
    for a,b,c,d in noteArchive:
        #TBD: comment out or delete print debug for production version
        print("project_id:",a)
        print("notes.project_id:",b)
        print("notes.note_id:",c)
        print("notes.note:",d)
        ################## Use following instead of for loop: 
        #if API is updated in future to only return X # of projects, add an additional check: #if: a in project_id_list
        #if a in project_id_list:
        try:
            project_index=project_id_list.index(a)
            projectList[project_index]["notes"].append({"id":c,"note":d})
        except:
            print("API/all error: will not add note id %s, project_id of note may not be in/not found in project_list "%c)
            # **** Should return a 400 error at this point "Some notes could not be added"? 
            #Check with lead developer or front-end dev for preferences
            
        ######### replace for loop with above block
        #for project in projectList:######## TBD: Optimize search instead of iterating all elements
        #    if project["id"]==a:
        #        project["notes"].append({"id":c,"note":d})
        #        break
        ###############################################
        
        
    print("\n------------------------------ENTIRE PROJECT LIST WITH NOTES ------------------------")
    print(projectList)

    cursor.close()


    response = app.response_class(response=json.dumps(projectList),status=200,mimetype='application/json')
    return response 


#############################################################
### API route, for updating projects
############################################################# 
@app.route('/API/update', methods = ["PUT","PATCH"])
@basic_auth.required
def update_project():
    if request.method == 'PUT':
        #request.args.get('url')   
        data_s=""
        data={}        
        if request.is_json:
            print("request is json, will use get_json() method")
            data=request.get_json()
            print(data)
        else:
            print("Request was not json, using bytes & get_data() with json.loads() methods")
            data_s_bytes=request.content_length
            print("content length=%s"%(data_s_bytes))
            #decode data only if bytes < 100kb
            if data_s_bytes<100000:
                #print(request.get_data(as_text=True)) #cache=True, as_text=False, parse_form_data=False
                data_s=request.get_data( as_text=True)
                print(data_s)
                data=json.loads(data_s)
                print(data) 
        global cnx
        if not cnx:
            connectToDB()
        cursor = cnx.cursor()
        try:
            cnx.commit() #cursor.execute("FLUSH TABLES projects")        
        except:
            print("WARNING: API/update could not refresh mysql-connector connection")
        id=data['id']
        print("id=",id)
        skip1=["id","details","requestor","notes"] #Do not update "id"
        valid1=["title","start_date","status","active","assignee","percent_complete"]
        update_base=("UPDATE Projects "
        "SET "
        "%s='%s'"
        " WHERE id=%s")        
        for keys in data: #non iterator: keys = list(data.keys()), keys=[*data.keys()] #for keys,values in data.items()
            #print("keys: ",keys," data:",data[keys])
            if keys not in skip1 and keys in valid1:
                update_s=update_base%(keys,data[keys],id)
                print(update_s)
                cursor.execute(update_s)
            if keys=='details':#data['details']:
                details=data['details']
                #print("Details data to update (pending):", details)
                valid2=["id","name","department"]
                db_map2={"id":"details_requestor_id","name":"details_requestor_name","department":"details_requestor_department"}
                valid3=["summary","justification"]
                db_map3={"summary":"details_summary","justification":"details_justification"}              
                for keys in details:
                    #print("Details keys: ",keys," details:",details[keys])
                    if keys=='requestor':
                        #print("requestor data, keys:",details[keys],details[keys].keys())
                        for requestorKey in details[keys].keys():
                            #print("item=",requestorKey,"value=",details[keys][requestorKey])
                            if requestorKey in valid2: #if db_key
                                update_s=update_base%(db_map2[requestorKey],details[keys][requestorKey],id) #%(db_key,details[keys][requestorKey],id)
                                print(update_s)
                                cursor.execute(update_s)                                                
                    else:
                        #db_key=None #if keys=='summary': #    db_key='details_summary' #if keys=='justification': #    db_key='details_justification'
                        if keys in valid3: #if db_key:
                            update_s=update_base%(db_map3[keys],details[keys],id) #%(db_key,details[keys],id)
                            print('\n',update_s)
                            cursor.execute(update_s)                        
        cnx.commit()        
        cursor.close()
    return ("Data updated! Request was json=%s"%(request.is_json), 200)

    
@app.before_request
def fn_before():
    #print("before request")
    pass

@app.after_request
def add_header(r):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    autoClearCache=True # if using true, use render_template instead of redirect for login to display flash errors
    if autoClearCache:
        r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        r.headers["Pragma"] = "no-cache"
        r.headers["Expires"] = "0"
        r.headers['Cache-Control'] = 'public, max-age=0'
    return r


if __name__ == "__main__":
  # This is used when running locally only. When deploying use a webserver process 
  # such as Gunicorn to serve the app.    

    print("main: fn")
    
    connectToDB()  
    firstTimeSetup=True
    
    if firstTimeSetup:
        createProjectDB()
        createTables()
        addInitialRecords()
        
    checkForTable('Projects')    
    checkForTable('Notes')
    #checkForTable('NotARealTableName')
    
    #testAddDeleteNotes()
    app.run()#(host='0.0.0.0', port=8080) #(host='127.0.0.1', port=8080, debug=True)

