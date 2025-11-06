# app/test_connection.py
from sqlalchemy.orm import sessionmaker
from app.databases import engine,SessionLocal
from sqlalchemy import text

def test_connection():
    # Create a new session
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Test the connection by executing a simple query
        result = session.execute(text("SELECT 1"))
        print("Connection successful: ", result.fetchone())
    except Exception as e:
        print("Error connecting to the database: ", e)
    finally:
        session.close()

if __name__ == "__main__":
    test_connection()