from db import engine
from mysql_models import Base

Base.metadata.create_all(bind=engine)

print("Tables created.")