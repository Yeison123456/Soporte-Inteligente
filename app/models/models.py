from sqlalchemy import JSON, Column, Integer, String, ForeignKey, Text, DateTime
from sqlalchemy.orm import relationship
import datetime
from app.database import Base


# -------------------------
# Tabla ROLES
# -------------------------
class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(50), unique=True, nullable=False)
    descripcion = Column(String(200), nullable=True)

    # Relación inversa (opcional pero útil)
    usuarios = relationship("User", back_populates="role")


# -------------------------
# Tabla USERS
# -------------------------
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    correo = Column(String(120), unique=True, nullable=False)
    hashed_password = Column(String(256), nullable=True)
    antiguedad_contrato = Column(Integer, nullable=True)  # en meses
    segmento = Column(String(50), nullable=True)

    rol_id = Column(Integer, ForeignKey("roles.id"))
    role = relationship("Role", back_populates="usuarios")

    tickets_como_cliente = relationship(
        "Ticket",
        back_populates="cliente",
        foreign_keys="Ticket.cliente_id"
    )

    tickets_como_manager = relationship(
        "Ticket",
        back_populates="account_manager",
        foreign_keys="Ticket.account_manager_id"
    )


# -------------------------
# Tabla TICKETS
# -------------------------
class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(String(50), primary_key=True, index=True)
    titulo = Column(Text, nullable=False)
    descripcion = Column(Text, nullable=False)
    estado_actual = Column(String(50), default="Nuevo")
    fecha_creacion = Column(DateTime, default=datetime.datetime.utcnow)
    recomendacion_agente = Column(JSON, nullable=True)
    tipo_mantenimiento = Column(Text, nullable=True)
    riego_churn = Column(Integer, nullable=True)

    cliente_id = Column(Integer, ForeignKey("users.id"))
    account_manager_id = Column(Integer, ForeignKey("users.id"))

    cliente = relationship(
        "User",
        back_populates="tickets_como_cliente",
        foreign_keys=[cliente_id]
    )

    account_manager = relationship(
        "User",
        back_populates="tickets_como_manager",
        foreign_keys=[account_manager_id]
    )

    historial = relationship("TicketHistory", back_populates="ticket", cascade="all, delete")


# -------------------------
# Tabla HISTORIAL DE ESTADOS
# -------------------------
class TicketHistory(Base):
    __tablename__ = "ticket_history"

    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(String(50), ForeignKey("tickets.id"))
    estado = Column(String(50), nullable=False)
    comentario = Column(Text, nullable=True)
    fecha_cambio = Column(DateTime, default=datetime.datetime.utcnow)

    ticket = relationship("Ticket", back_populates="historial")
