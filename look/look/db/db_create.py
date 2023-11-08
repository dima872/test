from sqlalchemy import Column, ForeignKey, Integer, String  
from sqlalchemy.ext.declarative import declarative_base  
from sqlalchemy.orm import relationship, sessionmaker  
from sqlalchemy import create_engine  
engine = create_engine("postgresql+psycopg2://dima:8726621331@localhost/dima", echo=True)
engine.connect()
session = sessionmaker(bind=engine)

Base = declarative_base()  

class Album(Base):  
    __tablename__ = 'Albums'  
    
    id_album = Column(Integer, primary_key=True)  
    title = Column(String(250), nullable=False)  
    author_id = Column(Integer, ForeignKey("Authors.id_author"))  
    genre = Column(String(250), nullable=False)
    year = Column(String(250), nullable=False)
    author = relationship("Author") 
    song = relationship("Song")

class Author(Base):  
    __tablename__ = 'Authors'  
    
    id_author = Column(Integer, primary_key=True)  
    Name = Column(String(250), nullable=False)  
    album = relationship("Album") # 1 ко многим

class Song(Base): 
    __tablename__ = 'Songs'

    id_song = Column(Integer, primary_key=True)
    title = Column(String(250), nullable=False)
    album_id = Column(Integer, ForeignKey("Albums.id_album"))
    album = relationship("Album")

class User(Base):
    __tablename__ = 'Users'
    id_user = Column(Integer, primary_key=True)
    login_1 = Column(String(250), nullable=False)
    password_1 = Column(String(250), nullable=False)

Base.metadata.create_all(engine)   