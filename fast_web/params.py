from fastapi import FastAPI, Request, Form, UploadFile, File
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import os 
from uuid import uuid4 # 128비트 길이로 범용 고유 식별자 생성
import shutil

app = FastAPI()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

@app.get("/")
def read_root():
    return {"message":"Hello"}

# :GET /item/정수?q=문자열
@app.get('/item/{item_id}')
def read_param(item_id:int, q:str | None = None):
    return {'item_id':item_id, 'q':q } 

@app.get('/item', response_class=HTMLResponse)
def form_page(request: Request):
    return templates.TemplateResponse('item_form.html',{"request": request})

@app.post("/item")
def create_item(
    name: str = Form(...),           # form에서 name 필드. ... 은 필수(required) 를 의미
    price: float = Form(...),        # form에서 price 필드
    is_offer: str | None = Form(None)  # form에서 is_offer 선택값, 기본 None
):
    # is_offer 문자열 처리 ("true" → True, ""/None → False)
    is_offer_bool = (is_offer == "true")
    return {"name": name, "price": price, "is_offer": is_offer_bool}

@app.get('/member', response_class=HTMLResponse)
def member_form_page(request: Request):
    return templates.TemplateResponse('member.html',{"request": request})

@app.post('/member')
def create_member(id:str = Form(...),
                  pw:str = Form(...),
                  gender:str = Form(...),
                  comment:str = Form(...),
                  hobby:list[str] = Form(default=[])
                  ):
    # textarea에서 엔터 -> \r\n
    # html에서 줄바꿈을 그대로 표현하고 싶다면 <br>로 변경
    comment = comment.replace('\r\n', '<br>')
    return {'id':id, 'gender': gender, 'comment':comment, 'hobby':hobby }

@app.get('/file.up')
def fileGet(request:Request):
    return templates.TemplateResponse('file_input.html',{'request':request})

# async = "기다리는 동안 놀지 않고 다른 일하는 함수"
# DB 호출
# API 호출
# 파일 읽기/쓰기
# 업로드 처리 (UploadFile)
@app.post('/file.up')
async def fileUp(title:str = Form(),
           photo:UploadFile = File(...)):
    #파일 정보
    filename = photo.filename
    content_type = photo.content_type
    #업로드 경로
    folder = os.path.join(BASE_DIR,'upload')
    #업로드 될 파일 명(중복 방지)
    ext = filename[-4:]#   .png
    filename = filename.replace(ext,'')+str(uuid4()) + ext
    #파일 내용
    content = await photo.read()
    f = open(folder+'/'+filename, 'wb')  # 바이너리 파일 출력
    f.write(content)
    f.close()
    
    return {'title':title, 'type':content_type, 'name': filename}



@app.get('/file2.up')
def fileGet2(request:Request):
    return templates.TemplateResponse('file_input2.html',{'request':request})

@app.post('/file2.up')
async def fileUp2(title:str = Form(),
           photo1:list[UploadFile] = File(...),
           photo2:UploadFile = File(...)
           ):
    #업로드 경로
    folder = os.path.join(BASE_DIR,'upload')
 
    saved_file_names =[]
    for file in photo1:
        filename = file.filename
        ext = filename[-4:]#   .png
        filename = filename.replace(ext,'')+str(uuid4()) + ext

        with open(folder+'/'+filename, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        saved_file_names.append(filename)

    return {"message":'업로드 성공', 'files':saved_file_names}    