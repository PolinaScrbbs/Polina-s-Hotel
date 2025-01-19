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

from .user import Base


class RoomCategory(BaseEnum):
    SINGLE_STANDARD = "Одноместный стандарт"
    SINGLE_ROOM_ECONOMY = "Одноместный эконом"
    STANDARD_DOUBLE_ROOM_WITH_TWO_SEPARATE_BEDS = (
        "Стандарт двухмесный с двумя раздельными кроватями"
    )
    ROOM_ECONOMY_DOUBLE_ROOM_WITH_TWO_SEPARATE_BEDS = (
        "Эконом двухмесный с двумя раздельными кроватями"
    )
    TRIPLE_BUDGET = "Трехместный бюджет"
    ONE_BED_BUSINESS = "Бизнес с одной кроватью"
    BUSINESS_WITH_TWO_BEDS = "Бизнес с двумя кроватями"
    TWO_ROOM_STANDARD_DOUBLE_ROOM_WITH_ONE_BED = (
        "Двухкомнатный двухместный стандарт с одной кроватью"
    )
    TWO_ROOM_DOUBLE_STANDARD_WITH_TWO_BEDS = (
        "Двухкомнатный двухместный стандарт с двумя кроватями"
    )
    ATELIER = "Студия"
    A_SUITE_WITH_A_DOUBLE_BED = "Люкс с двухспальной кроватью"


class RoomStatus(BaseEnum):
    FREE = "free"
    BUSY = "busy"
    CLEANING = "cleaning"


class HotelRoom(Base):
    __tablename__ = "hotel_rooms"

    id = Column(Integer, primary_key=True)
    name = Column(String(32), nullable=False)
    description = Column(String(128), nullable=False)
    category = Column(
        Enum(RoomCategory), default=RoomCategory.SINGLE_STANDARD, nullable=False
    )
    floor = Column(Integer, default=1, nullable=False)
    status = Column(Enum(RoomStatus), default=RoomStatus.FREE, nullable=False)
    price = Column(Float, default=1500.00, nullable=False)


class EquirementElement(Base):
    __tablename__ = "equirement_elements"

    id = Column(Integer, primary_key=True)
    name = Column(String(32), unique=True, nullable=False)


class RoomEquirementElement(Base):
    __tablename__ = "room_equirement_elements"

    id = Column(Integer, primary_key=True)
    room_id = Column(Integer, ForeignKey("hotel_rooms.id"), nullable=False)
    element_id = Column(Integer, ForeignKey("equirement_elements.id"), nullable=False)
