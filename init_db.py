from database import engine, Base
from models import User, Note

Base.metadata.create_all(bind = engine)