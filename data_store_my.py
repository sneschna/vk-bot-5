import sqlite3
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Profile(Base):
    __tablename__ = 'profiles'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)


class DataStore:
    def __init__(self):
        self.engine = create_engine(db_url_object)
        self.create_table()

    def create_table(self):
        Base.metadata.create_all(self.engine)

    def check_profile_in_database(self, profile):
        with Session(self.engine) as session:
            result = session.query(Profile).filter(Profile.user_id == profile['id']).first()
            return result is not None

    def add_profile(self, profile):
        with Session(self.engine) as session:
            to_bd = Profile(user_id=profile['id'], name=profile['name'], bdate=profile['bdate'],
                            home_town=profile['home_town'], sex=profile['sex'], city_id=profile['city'])
            session.add(to_bd)

    def close_database(self):
        self.data_store.close_database()

