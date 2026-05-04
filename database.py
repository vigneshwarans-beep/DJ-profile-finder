from sqlalchemy import Column, Integer, String, Text, ForeignKey, Table, create_engine, DateTime
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
import datetime

Base = declarative_base()

# Association table for Many-to-Many relationship between Candidates and Skills
candidate_skill = Table(
    'candidate_skill',
    Base.metadata,
    Column('candidate_id', Integer, ForeignKey('candidates.id'), primary_key=True),
    Column('skill_id', Integer, ForeignKey('skills.id'), primary_key=True)
)

class Candidate(Base):
    """Represents a scraped LinkedIn profile."""
    __tablename__ = 'candidates'
    
    id = Column(Integer, primary_key=True)
    linkedin_url = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    headline = Column(String)
    summary = Column(Text)
    location = Column(String)
    raw_data_path = Column(String) # Path to the raw JSON file on disk
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    experiences = relationship("Experience", back_populates="candidate", cascade="all, delete-orphan")
    educations = relationship("Education", back_populates="candidate", cascade="all, delete-orphan")
    skills = relationship("Skill", secondary=candidate_skill, back_populates="candidates")
    
    def __repr__(self):
        return f"<Candidate(name='{self.name}', headline='{self.headline}')>"

class Experience(Base):
    """Represents a single job experience for a candidate."""
    __tablename__ = 'experiences'
    
    id = Column(Integer, primary_key=True)
    candidate_id = Column(Integer, ForeignKey('candidates.id'), nullable=False)
    company = Column(String, nullable=False)
    title = Column(String, nullable=False)
    start_date = Column(String) # Storing as string for flexibility (e.g., "Jan 2020")
    end_date = Column(String)   # Can be "Present"
    description = Column(Text)
    
    candidate = relationship("Candidate", back_populates="experiences")

class Education(Base):
    """Represents an educational degree/schooling for a candidate."""
    __tablename__ = 'educations'
    
    id = Column(Integer, primary_key=True)
    candidate_id = Column(Integer, ForeignKey('candidates.id'), nullable=False)
    school = Column(String, nullable=False)
    degree = Column(String)
    field_of_study = Column(String)
    start_date = Column(String)
    end_date = Column(String)
    
    candidate = relationship("Candidate", back_populates="educations")

class Skill(Base):
    """Represents a unique skill."""
    __tablename__ = 'skills'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    
    candidates = relationship("Candidate", secondary=candidate_skill, back_populates="skills")
    
    def __repr__(self):
        return f"<Skill(name='{self.name}')>"

class JobSearchQuery(Base):
    """Stores the history of job descriptions the user provides to the bot."""
    __tablename__ = 'job_search_queries'
    
    id = Column(Integer, primary_key=True)
    job_description = Column(Text, nullable=False) 
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

import os

def init_db(db_path=None):
    """Initializes the database and creates tables if they don't exist."""
    if db_path is None:
        # Use an absolute path to prevent OperationalError on Streamlit Cloud
        base_dir = os.path.abspath(os.path.dirname(__file__))
        db_file = os.path.join(base_dir, "linkedin_bot.db")
        db_path = f"sqlite:///{db_file}"
        
    engine = create_engine(db_path, echo=False)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return engine, Session()

if __name__ == "__main__":
    print("Initializing database schema...")
    engine, session = init_db()
    print(f"Database schema created successfully at {engine.url}")
