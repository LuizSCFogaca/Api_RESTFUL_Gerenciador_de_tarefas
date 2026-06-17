from fastapi import FastAPI
from backend.database import engine, Base, SessionLocal
from backend.Controllers.tarefaController import router as tarefa_router
from backend.Controllers.usuarioController import router as usuario_router
from backend.Controllers.authController import router as auth_router
from backend.Services import usuarioService

from backend.Models import tarefaModel
from backend.Models import usuariosModel

Base.metadata.create_all(bind=engine)

# garante um admin fixo (admin@teste.com / 123456) sempre que a API sobe
with SessionLocal() as db:
    usuarioService.garantir_admin_padrao(db)

app = FastAPI()

app.include_router(auth_router)
app.include_router(tarefa_router)
app.include_router(usuario_router)

@app.get("/")
def read_root():
    return{"Status": "Running"}