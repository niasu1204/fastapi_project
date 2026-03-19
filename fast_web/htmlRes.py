from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import os 

app = FastAPI()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

@app.get("/html")
def html_test():
    html = "<html><head><meta charset=\"utf-8\"></head><body>"
    html += "<marquee>fast api 공부중!! </marquee>"
    html += "</body></html>"
    return HTMLResponse(html)

# html문서로 응답 결과 만들기
@app.get('/items', response_class=HTMLResponse)
def form_page(request: Request):
    return templates.TemplateResponse('form.html',{"request": request})

# Form(...) : 필수값. 반드시 들어와야 하는 값(없으면 422에러 발생)
# Form(기본값)
@app.post('/submit')
def submit(name:str = Form(...), age:int = Form(0), age2:int = Form(0)):
    return {'name':name, 'age': age, 'age2':age2 }
    