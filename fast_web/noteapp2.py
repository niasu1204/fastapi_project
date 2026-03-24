from fastapi import FastAPI, Depends, HTTPException, Form, File, UploadFile
from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base
import models
from schemas import NoteCreate, NoteUpdate, NoteOut
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from uuid import uuid4

#테이블 생성
Base.metadata.create_all(bind=engine)

app = FastAPI()

#CORS 추가
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173","http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 1. 업로드할 폴더 경로 설정
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")

# 2. 폴더가 없으면 자동으로 생성하는 코드
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

# 3. /uploads URL로 요청이 오면, 서버의 "uploads" 폴더 안의 파일들을 보여줍니다.
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

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


# # 3. 생성
# @app.post("/notes", response_model=NoteOut)
# def create_note(note: NoteCreate, db: Session = Depends(get_db)):
#     # JSON -> note: NoteCreate(Pydantic 모델) -> Python dict로 변경
#     db_note = models.Note(**note.model_dump())
#     db.add(db_note)
#     db.commit()
#     db.refresh(db_note) # DB에 반영된 최신 상태를 다시 객체에 가져오는 함수
#                         # INSERT 후 자동 생성 값 가져올 때 사용
#     return db_note

@app.post("/notes", response_model=NoteOut)
async def create_note(    
    # 1. 텍스트 데이터는 Form(...)
    title: str = Form(...),
    content: str = Form(...),
    # 2. 파일(기본값 None)
    file: UploadFile | None = File(None),
    db: Session = Depends(get_db)
):
    # 3. 받은 폼 데이터 NoteCreate에 넣어 검증    
    note_data = NoteCreate(title=title, content=content)

    # 4. 파일 처리 로직 (파일이 들어왔을 때만 실행)
    file_path = None
    if file is not None:
        # 실제 환경에서는 uuid 등을 써서 파일명 중복을 방지하는 것이 좋습니다.
        folder = os.path.join(BASE_DIR,'uploads')
        #업로드 될 파일 명(중복 방지)
        name, ext = os.path.splitext(file.filename)#   .png
        filename = name +str(uuid4()) + ext
        #파일 내용
        content = await file.read()
        f = open(folder+'/'+filename, 'wb')  # 바이너리 파일 출력
        f.write(content)
        f.close()

        file_path = f"uploads/{filename}"

    # 5. DB에 저장할 SQLAlchemy 모델 객체 생성
    db_note = models.Note(
        title=note_data.title, 
        content=note_data.content, 
        file_path=file_path # 파일이 없으면 None이 들어감
    )
    
    # 6. DB 커밋
    db.add(db_note)
    db.commit()
    db.refresh(db_note)

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