from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()
def to_dict(self):
    return {c.name: str(getattr(self, c.name, None)) for c in self.__table__.columns}
Base.to_dict = to_dict