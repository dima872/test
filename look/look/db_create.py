from sqlalchemy import Column, ForeignKey, Integer, String  
from sqlalchemy.ext.declarative import declarative_base  
from sqlalchemy.orm import relationship  
from sqlalchemy import create_engine  
engine = create_engine("postgresql+psycopg2://dima:8726621331@localhost/dima", echo=True)

Base = declarative_base()  

class Album(Base):  
    __tablename__ = 'Albums'  
    
    id_album = Column(Integer, primary_key=True)  
    title = Column(String(250), nullable=False)  
    author_id = Column(Integer, ForeignKey("Authors.id_author"))  
    genre = Column(String(250))
    year = Column(String(250), nullable=False)
    author = relationship("Author") 
    song = relationship("Song")

class Author(Base):  
    __tablename__ = 'Authors'  
    
    id_author = Column(Integer, primary_key=True)  
    name = Column(String(250), nullable=False)  
    album = relationship("Album") # 1 ко многим

class Song(Base): 
    __tablename__ = 'Songs'

    id_song = Column(Integer, primary_key=True)
    title = Column(String(250), nullable=False)
    album_id = Column(Integer, ForeignKey("Albums.id_album"))
    album = relationship("Album")


Base.metadata.create_all(engine)   