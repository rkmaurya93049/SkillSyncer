from db.session import engine
from models.evaluation import Base

def init_db():
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":

    init_db()
