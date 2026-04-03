from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, JSON
from app.database import Base


class Analysis(Base):
    __tablename__ = "analyses"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String(2048), nullable=False)
    html_length = Column(Integer, nullable=False)
    tag_counts = Column(JSON)
    keyword_frequency = Column(JSON)
    link_stats = Column(JSON)
    image_stats = Column(JSON)
    text_stats = Column(JSON)
    dom_depth = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
