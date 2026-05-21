from fastapi import FastAPI
from backend.database import engine, Base
from backend.Controllers.tarefaController import router as tarefa_router

from backend.Models import tarefaModel
from backend.Models import usuariosModel

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(tarefa_router)

@app.get("/")
def read_root():
    return{"Status": "Running"}