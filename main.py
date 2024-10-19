from fastapi import FastAPI,BackgroundTasks,HTTPException,Request,Depends
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import session
from fastapi.templating import Jinja2Templates
# from schemas import TranslationRequest
import schemas
import crud
import models
from database import get_db,engine
from typing import List
import uuid

models.Base.metadata.create_all(bind=engine)

app=FastAPI()

templates=Jinja2Templates(directory="templates")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], #Allow All origins
    allow_credentials=True,
    allow_methods=["*"], #Allow all methods
    allow_headers=["*"], #Allow all headers
)

@app.get('/index',response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("index.html",{"request":request})

@app.post("/translate",response_model=schemas.TaskResponse)
def translate(request:schemas.TranslationRequest,  background_tasks: BackgroundTasks = None,db:session=Depends(get_db)):

    task=crud.create_translation_task(db,request.text,request.languages)

    background_tasks.add_task(perform_translations,task.id,request.text,request.languages,db)

    return{"task_id":{task.id}}

@app.get("/translate/{task_id}",response_model=schemas.TranslationStatus)
def get_translate(task_id:int,db:session=Depends(get_db)):

    task=crud.get_translation_task(db,task_id)
    if not task :
        raise HTTPException(staus_code=404,detail="task not found")
 

    return{"task_id":task.id,"status":task.status,"translations":task.translations}


@app.get("/translate/content/{task_id}",response_model=schemas.TranslationStatus)
def get_translate_content(task_id:int,db:session=Depends(get_db)):

    task=crud.get_translation_task(db,task_id)
    if not task :
        raise HTTPException(staus_code=404,detail="task not found")
 

    return{task}

    
