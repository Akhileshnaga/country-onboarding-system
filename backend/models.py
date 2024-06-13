from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from database import Base

class Country(Base):
    __tablename__ = 'countries'
    
    id = Column(Integer, primary_key=True, index=True)
    country_name = Column(String, index=True)
    country_code = Column(Integer, index=True)
    
    
class Detail(Base):
    __tablename__ = 'details'
    
    id = Column(Integer,primary_key=True, index=True)
    detail_name = Column(String, index=True)
    detail_type = Column(String)
    
    country_id = Column(Integer, ForeignKey("countries.id"))