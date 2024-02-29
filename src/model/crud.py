from sqlalchemy.orm import Session, sessionmaker
from .models import User, Base
from .database import SessionLocal, engine

Base.metadata.create_all(bind=engine)
db = SessionLocal()

def create_user(chat_id:int):
    db_user = User(id=chat_id, chain="ethereum", method = "wallet")
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
    except:
        return False
    return db_user

# Define the default chain updating function
def update_chain(id:int, chain:str):
    user = db.query(User).filter(User.id == id).update({"chain" : chain})
    try:
        db.commit()
    except:
        return False
    return user

# Define the default method updating function
def update_moethod(id:int, method:str):
    user = db.query(User).filter(User.id == id).update({"method" : method})
    try:
        db.commit()
    except:
        return False
    return user

# Define function to get user with id 
def get_user_by_id(id:int):
    user = db.query(User).filter(User.id == id).first()
    if not user:
        return False
    return user

def delete_user(id:int):
    try:
        db.query(User).filter(User.id == id).delete()
        db.commit()
        return True
    except:
        return False

 # Define count individual for groups
def count_individual_user():
    user_count = db.query(User).filter(User.id > 0).count()
    return user_count if user_count >= 0 else False

# Define count function for groups
def count_groups():
    user_group = db.query(User).filter(User.id < 0).count()
    return user_group if user_group >= 0 else False