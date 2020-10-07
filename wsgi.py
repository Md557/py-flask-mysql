from main import app #from app.main.... but now moved main.py up a level
from main import connectToDB
from main import createProjectDB,createTables,addInitialRecords

if __name__ == "__main__":
	app.run()
    connectToDB()
    firstTimeSetup=True
    if firstTimeSetup:
        createProjectDB()
        createTables()
        addInitialRecords()