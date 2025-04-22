from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class Predicao(Base):
    __tablename__ = 'predicoes'
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer)
    age = Column(Integer)
    gender = Column(String)
    ethnicity = Column(String)
    parental_education = Column(String)
    study_time_weekly = Column(Float)
    absences = Column(Float)
    tutoring = Column(String)
    parental_support = Column(String)
    extracurricular = Column(String)
    sports = Column(String)
    music = Column(String)
    volunteering = Column(String)
    predicted_grade = Column(String)

engine = create_engine('sqlite:///database/db.sqlite3')
Base.metadata.create_all(engine)

SessionLocal = sessionmaker(bind=engine)
