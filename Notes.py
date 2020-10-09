from main import db
from sqlalchemy.orm import sessionmaker

class Notes(db.Model): #ORM for notes database. TBD: add ORM for projects database
    project_id=db.Column(db.Integer,unique=False)
    note_id=db.Column(db.Integer,primary_key=True)
    note=db.Column(db.String(2000),unique=False)
    def __init__(self,project_id,note_id,note):
        self.project_id=project_id
        self.note_id=note_id
        self.note=note

        
def addNote(projectID,noteID,note):
    newNote=Notes(projectID,noteID,note)    
    db.session.add(newNote)
    db.session.commit()
    #Should exception be caught, or message from SQLAlchemy returned to API, to make sure note actually updted?
    print("Added note ",noteID)
    
def updateNote(projectID,noteID,note):
    #Should exception be caught, or message from SQLAlchemy returned to API, to make sure note actually updted?
    Notes.query.filter_by(note_id=noteID).update({"note":note})
    db.session.commit()
    print("Updated note ",noteID)


def deleteNote(noteID):
    Notes.query.filter_by(note_id=noteID).delete()
    db.session.commit()
    #Should exception be caught, or message from SQLAlchemy returned to API, to make sure note actually updted?
    print("Deleted note ",noteID)
    
def printNotes():    
    allNotes = Notes.query.all()
    print(allNotes)    
def getNoteById(note_id):
    note=Notes.query.filter_by(note_id=note_id).first()
    return note
def isNoteWithId(note_id):
    note=Notes.query.filter_by(note_id=note_id).first()
    if note:
        return True
    else:
        return False
    
def testAddDeleteNotes(): #Used for debugging or creating notes without a frontend
    try:
        addNote(1,200,"This note was a test add on 2020-10-3")
        addNote(1,201,"This note was a 2nd test add on 2020-10-3")
    except:
        db.session.rollback()
        print("could not add note(s), does note already exist?")

    try:
        printNotes()
        deleteNote(200)
        printNotes()
    except:
        print("could not delete note, does note exist?")

def checkForTable(tableName):
    try:
        Session=sessionmaker()
        engine=db.get_engine()
        Session.configure(bind=engine)
        sess=Session()#Was this required for next statment?
        if not engine.dialect.has_table(engine,tableName): 
            print("WARNING, Table %s hasn't been set up yet --checkForTable() method--"%tableName) 
            #db.create_all() #
        else:
            print("SQLAlchemy db has table '%s'"%tableName)
    except:
        print("exception occured in method checkForTable(), using sessionmaker(), db.get_engine(), and engine.dialect.has_table()")
