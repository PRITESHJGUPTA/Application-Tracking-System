from sqlalchemy import Column, Integer, Text, ARRAY, Boolean, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import datetime
from sqlalchemy import Boolean

# Inside Candidate class
is_selected = Column(Boolean, default=False)

DATABASE_URL = "postgresql+psycopg2://postgres:password@localhost:5432/ats_db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class Candidate(Base):
    __tablename__ = 'candidates'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(Text)
    email = Column(Text)
    phone = Column(Text)
    skills = Column(ARRAY(Text))
    experience = Column(ARRAY(Text))

    # NEW fields
    qualification = Column(Text)
    location_state = Column(Text)
    location_city = Column(Text)
    gender = Column(Text)
    kanaka_employee = Column(Boolean, default=False)
    aptitude_status = Column(Text)  # Cleared / Not Cleared / Performing Test
    interview_round_1 = Column(Text)
    interview_round_2 = Column(Text)
    applied_on = Column(Date, default=datetime.date.today)
    # Inside Candidate class
    is_selected = Column(Boolean, default=False)

