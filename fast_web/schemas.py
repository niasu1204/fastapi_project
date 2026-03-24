from pydantic import BaseModel
# pydantic: 데이터의 검증

# JSON API면 BaseModel 필수
# Form 기반이면 BaseModel 필요 없음
# FastAPI가 요청/응답 처리할 때 자동으로 사용

# 요청시 JSON -> py객체로 변환

# 공통 필드 정의 (재사용) - 검사 대상
class NoteBase(BaseModel):
    title: str
    content: str

class NoteCreate(NoteBase):
    pass

class NoteUpdate(NoteBase):
    pass

class NoteOut(NoteBase):
    id: int
    file_path: str | None = None
    class Config:
        orm_mode = True   # ORM 객체를 자동으로 dict처럼 읽음 -> JSON으로 변환