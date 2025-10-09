from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from db import Base

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, autoincrement=True)
    correo = Column(String(120), unique=True, nullable=False)
    nombre = Column(String(100), nullable=False)
    contrasena = Column(String(200), nullable=False)

    tareas = relationship("Tarea", back_populates="dueño")

    def __repr__(self):
        return f"<Usuario(id={self.id}, correo='{self.correo}', nombre='{self.nombre}')>"



class Tarea(Base):
    __tablename__ = "tareas"

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String(100))
    descripcion = Column(String(255))
    estado = Column(String(30), default="en progreso")
    fecha_creacion = Column(DateTime, default=datetime.today)
    fecha_finalizacion_esperada = Column(DateTime)
    fecha_finalizacion = Column(DateTime)
    
    # Clave foránea
    id_usuario = Column(Integer, ForeignKey("usuarios.id"))

    # Relación inversa
    dueño = relationship("Usuario", back_populates="tareas")