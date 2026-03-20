from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base
import models
from schemas import NoteCreate, NoteUpdate, NoteOut
from fastapi.middleware.cors import CORSMiddleware


#테이블 생성
Base.metadata.create_all(bind=engine)

app = FastAPI()

#CORS 추가
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# DB 세션 의존성 : 요청할때마다 DB 연결 열고 -> 사용 -> 연결 종료
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()  

# 1. 전체 조회
# response_model : 리턴 데이터의 타입을 검증 + 변환 + 필터링(타입 틀리면, 누락된 필드 있으면 에러)
# -NoteOut 구조와 맞는지 확인
# -ORM 객체를 JSON으로 자동 변환
# -필터링(NoteOut에 없는 데이터는 반환X)- 'a'컬럼이 있어서 가져왔어도 NoteOut에 없으면 필터로 걸러냄
@app.get("/notes", response_model=list[NoteOut])
def get_notes(db: Session = Depends(get_db)):
    return db.query(models.Note).all()


# 2. 상세 조회
@app.get("/notes/{note_id}", response_model=NoteOut)
def get_note(note_id: int, db: Session = Depends(get_db)):
    note = db.query(models.Note).get(note_id)
    if not note:
        raise HTTPException(404, "Not found")
    return note


# 3. 생성
@app.post("/notes", response_model=NoteOut)
def create_note(note: NoteCreate, db: Session = Depends(get_db)):
    # JSON -> note: NoteCreate(Pydantic 모델) -> Python dict로 변경
    db_note = models.Note(**note.model_dump())
    db.add(db_note)
    db.commit()
    db.refresh(db_note) # DB에 반영된 최신 상태를 다시 객체에 가져오는 함수
                        # INSERT 후 자동 생성 값 가져올 때 사용
    return db_note


# 4. 수정
@app.put("/notes/{note_id}", response_model=NoteOut)
def update_note(note_id: int, data: NoteUpdate, db: Session = Depends(get_db)):
    note = db.query(models.Note).get(note_id)
    if not note:
        raise HTTPException(404)

    note.title = data.title
    note.content = data.content
    db.commit()
    return note


# 5. 삭제
@app.delete("/notes/{note_id}")
def delete_note(note_id: int, db: Session = Depends(get_db)):
    note = db.query(models.Note).get(note_id)
    if not note:
        raise HTTPException(404)

    db.delete(note)
    db.commit()
    return {"message": "deleted"}        