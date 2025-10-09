from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

# Para registro de usuario
class UserCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    correo: str
    nombre: str
    contraseña: str

# Para login
class UserLogin(BaseModel):
    correo: str
    contraseña: str

# Para crear una tarea
class TareaCreate(BaseModel):
    titulo: str
    descripcion: str
    user_id: int
    fecha: Optional[datetime]

class UsuarioResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    nombre: str
    correo: str


class TareaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    titulo: str
    descripcion: str
    estado: str
    fecha_creacion: datetime
    fecha_finalizacion_esperada: Optional[datetime]
    fecha_finalizacion: Optional[datetime]
    id_usuario: int
    nombre_usuario: str


class TareaEstadoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    estado: str
