from sqlalchemy import Column, Integer, String, Text
from database import Base

class Note(Base):
    __tablename__ = "notes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    # 파일 경로 또는 파일명을 저장할 컬럼 추가
    file_path = Column(String(255), nullable=True)
