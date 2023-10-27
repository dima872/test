from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .db_create import Base, Album, Author, Song

engine = create_engine("postgresql+psycopg2://dima:8726621331@localhost/dima", echo=True)
engine.connect()
#echo включает ведение лога

session = sessionmaker(bind=engine)
s = session()
#author_one = Author(name="Линда") 
#s.add(author_one) 
#s.commit()
s.add_all([Author(name="Линда"),
           Author(name="ДДТ"),
           Author(name="Hi-Fi")
           ])
s.commit()

s.add_all([Album(title="Ворона", author_id=1, genre="Инди-рок", year="1996"),
           Album(title="Актриса Весна", author_id=2, genre="Рок", year="1992"),
           Album(title="Первый контакт", author_id=3, genre="Попса", year="2009"),  
           Album(title="Best", author_id=3, genre="Попса", year="2002"),
           Album(title="Метель августа", author_id=2, genre="Рок", year="1993"),
            ])
s.commit()


s.add_all([Song(title="Холод", album_id=1),
           Song(title="Северный ветер", album_id=1),
           Song(title="Никогда", album_id=1),
           Song(title="Дождь", album_id=2),
           Song(title="В последнюю осень", album_id=2),
           Song(title="Фома", album_id=2),
           Song(title="Besprizornik", album_id=3),
           Song(title="Call me Misha", album_id=3),
           Song(title="Childhood", album_id=3),
           Song(title="Он", album_id=4),
           Song(title="Песня царевный", album_id=4),
           Song(title="Черный ворон", album_id=4),
           Song(title="Потолок", album_id=5),
           Song(title="Питер", album_id=5),
           Song(title="Свобода", album_id=5),
        ])
s.commit()