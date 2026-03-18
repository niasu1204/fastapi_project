from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def index():
    return{'message': 'hello, Fast API!!'}
# 라우팅
@app.get("/item")
def get_items():
    return ['apple','banana']
# 동적 url
@app.get("/item/{item_id}")
def get_item(item_id:int):
    return {'item_id':item_id}

