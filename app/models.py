from sqlalchemy import Column, Integer, String, DateTime, Text, create_engine, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
import datetime

Base = declarative_base()

class Query(Base):
    __tablename__ = "queries"
    id = Column(Integer, primary_key=True)
    case_type = Column(String)
    case_no = Column(String)
    year = Column(String)
    fetched_at = Column(DateTime, default=datetime.datetime.utcnow)
    raw_response = Column(Text)
    documents = relationship("Document", back_populates="query")

class Document(Base):
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True)
    query_id = Column(Integer, ForeignKey("queries.id"))
    local_path = Column(String)
    remote_url = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    query = relationship("Query", back_populates="documents")
