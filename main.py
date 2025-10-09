from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from typing import List
from datetime import datetime
from db import Base, engine, SessionLocal
from models import Usuario, Tarea
from schemas import UserCreate, UserLogin, TareaCreate, TareaResponse, UsuarioResponse, TareaEstadoResponse
from auth import hash_password, verify_password

Base.metadata.create_all(bind=engine)

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,          # Dominios que pueden acceder
    allow_credentials=True,
    allow_methods=["*"],            # Métodos permitidos (GET, POST, etc.)
    allow_headers=["*"],            # Headers permitidos
)

# Dependencia: obtener sesión
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ---------------------------
# Endpoint: Registrar usuario
# ---------------------------
@app.post("/register")
async def register(user:UserCreate, db: Session = Depends(get_db)):
    try:
        correo = user.correo.lower()
        # Revisar si el correo ya existe
        if db.query(Usuario).filter_by(correo=correo).first():
            return JSONResponse(status_code=400, content={"error": "Correo ya registrado"})
        # Crear usuario con contraseña hasheada
        nuevo_usuario = Usuario(
            correo=correo,
            nombre=user.nombre,
            contrasena=hash_password(user.contraseña)
        )
        db.add(nuevo_usuario)
        db.commit()
        db.refresh(nuevo_usuario)
        
        
        return JSONResponse(status_code=201, content={"message": "Usuario registrado exitosamente", "usuario": nuevo_usuario.nombre})
    except IntegrityError as e:
        db.rollback()  # revertir cambios en caso de error
        return JSONResponse(status_code=400, content={"error": "Error de integridad: " + str(e.orig)})
    
    except SQLAlchemyError as e:
        db.rollback()
        return JSONResponse(status_code=500, content={"error": "Error de base de datos: " + str(e)})
    
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": "Error inesperado: " + str(e)})
# ---------------------------
# Endpoint: Iniciar sesión
# ---------------------------
@app.post("/login")
async def login(user:UserLogin, db: Session = Depends(get_db)):
    try:
        correo = user.correo.lower()
        contrasena = user.contraseña
        
        usuario = db.query(Usuario).filter_by(correo=correo).first()
        if not usuario:
            return JSONResponse(status_code=404, content={"error": "Usuario no encontrado"})
        if not verify_password(contrasena, usuario.contrasena):
            raise JSONResponse(status_code=401, content={"error": "Contraseña incorrecta"})
        return {"mensaje": "Inicio de sesión exitoso", "usuario": usuario.nombre}
    except SQLAlchemyError as e:
        return JSONResponse(status_code=500, content={"error": "Error de base de datos: " + str(e)})
    
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": "Error inesperado: " + str(e)})
    
    
@app.get("/usuarios", response_model=List[UsuarioResponse])
async def listar_usuarios(db: Session = Depends(get_db)):
    try:
        usuarios = db.query(Usuario).all()
        resultado = [
            UsuarioResponse(
                id=usuario.id,
                nombre=usuario.nombre,
                correo=usuario.correo
            )
            for usuario in usuarios
        ]
        return resultado
    except SQLAlchemyError as e:
        return JSONResponse(status_code=500, content={"error": "Error de base de datos: " + str(e)})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": "Error inesperado: " + str(e)})


# ---------------------------
# Endpoint: Listar todas las tareas
# ---------------------------
@app.get("/tareas", response_model=List[TareaResponse])
async def listar_tareas(db: Session = Depends(get_db)):
    try:
        tareas = db.query(Tarea).all()
        resultado = [
            TareaResponse(
                id=tarea.id,
                titulo=tarea.titulo,
                descripcion=tarea.descripcion,
                estado=tarea.estado,
                fecha_creacion=tarea.fecha_creacion,
                fecha_finalizacion_esperada=tarea.fecha_finalizacion_esperada,
                fecha_finalizacion=tarea.fecha_finalizacion,
                id_usuario=tarea.id_usuario,
                nombre_usuario=tarea.dueño.nombre if tarea.dueño else ""
            )
            for tarea in tareas
        ]
        return resultado
    except SQLAlchemyError as e:
        return JSONResponse(status_code=500, content={"error": "Error de base de datos: " + str(e)})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": "Error inesperado: " + str(e)})

@app.post("/tareas")
async def crear_tarea(tarea: TareaCreate, db: Session = Depends(get_db)):
    try:
        nueva_tarea = Tarea(
            titulo=tarea.titulo,
            descripcion=tarea.descripcion,
            id_usuario=tarea.user_id,
            fecha_finalizacion_esperada=tarea.fecha,
            fecha_finalizacion=None
        )
        db.add(nueva_tarea)
        db.commit()
        db.refresh(nueva_tarea)
        return JSONResponse(status_code=201, content={"message": "Tarea registrada exitosamente", "id": nueva_tarea.id})
    except IntegrityError as e:
        db.rollback()
        return JSONResponse(status_code=400, content={"error": "Error de integridad: " + str(e.orig)})
    except SQLAlchemyError as e:
        db.rollback()
        return JSONResponse(status_code=500, content={"error": "Error de base de datos: " + str(e)})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": "Error inesperado: " + str(e)})


# ---------------------------
# Endpoint: Finalizar tarea
# ---------------------------
@app.put("/tareas/finalizar/{tarea_id}",response_model=TareaEstadoResponse)
async def finalizar_tarea(tarea_id: int, db: Session = Depends(get_db)):
    try:
        tarea = db.query(Tarea).filter(Tarea.id == tarea_id).first()
        if not tarea:
            return JSONResponse(status_code=404, content={"error": "Tarea no encontrada"})
        
        hoy = datetime.today()
        tarea.fecha_finalizacion = hoy
        print(type(hoy))
        print(type(tarea.fecha_finalizacion_esperada))
        print(type(tarea.fecha_creacion))
        
        
        if tarea.fecha_finalizacion_esperada is None or hoy <= tarea.fecha_finalizacion_esperada:
            tarea.estado = "finalizado"
        else:
            tarea.estado = "finalizado con retraso"

        db.commit()
        db.refresh(tarea)
        return JSONResponse(status_code=200, content={
            "message": "Tarea finalizada correctamente",
            "id": tarea.id,
            "estado": tarea.estado,
        })
    except SQLAlchemyError as e:
        db.rollback()
        return JSONResponse(status_code=500, content={"error": "Error de base de datos: " + str(e)})
    except Exception as e:
        db.rollback()
        return JSONResponse(status_code=500, content={"error": "Error inesperado: " + str(e)})

# ---------------------------
# Endpoint: Root, check api status
# ---------------------------
@app.get("/")
def read_root():
    return {"status": "ok"}
