from datetime import datetime
from enum import Enum as BaseEnum
from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    String,
    Enum,
    Date,
    CHAR,
    Boolean,
    DateTime,
    Float,
)

from .hotel import Base


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True)
    client_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    room = Column(Integer, ForeignKey("hotel_rooms.id"), nullable=False)
    arrival_date = Column(DateTime, nullable=False)
    eviction_date = Column(DateTime, nullable=False)
    is_paid = Column(Boolean, default=False)


class Service(Base):
    __tablename__ = "services"

    id = Column(Integer, primary_key=True)
    name = Column(String(32), nullable=False)
    description = Column(String(128), nullable=False)


class OrderService(Base):
    __tablename__ = "order_service"

    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    service_id = Column(Integer, ForeignKey("services.id"), nullable=False)
