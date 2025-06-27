
from datetime import datetime
from typing import Optional

from sqlmodel import SQLModel
from sqlalchemy import Column, String, Integer, DateTime, LargeBinary, ForeignKey


class Device(SQLModel):
    __tablename__ = "devices"
    mac = Column(String, primary_key=True)
    vendor = Column(String)
    first_seen = Column(DateTime, default=datetime.utcnow)
    last_seen = Column(DateTime, default=datetime.utcnow)
    rssi_history = Column(String, default="[]")


class RawPacket(SQLModel):
    __tablename__ = "rawpacket"
    id = Column(Integer, primary_key=True, autoincrement=True)
    device_mac = Column(String, ForeignKey("devices.mac"))
    timestamp = Column(DateTime, default=datetime.utcnow)
    rssi = Column(Integer)
    data = Column(LargeBinary)


class DecodedEvent(SQLModel):
    __tablename__ = "decodedevent"
    id = Column(Integer, primary_key=True, autoincrement=True)
    packet_id = Column(Integer, ForeignKey("rawpacket.id"))
    event_type = Column(String)
    data = Column(String)


class CaptureSession(SQLModel):
    __tablename__ = "capturesession"
    id = Column(Integer, primary_key=True, autoincrement=True)
    started_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime, nullable=True)
    description = Column(String, nullable=True)


class AlertRule(SQLModel):
    __tablename__ = "alertrule"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    condition = Column(String)
    enabled = Column(Integer, default=1)

from __future__ import annotations
from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel


class Device(SQLModel, table=True):
    mac: str = Field(primary_key=True)
    vendor: Optional[str] = None
    first_seen: Optional[datetime] = None
    last_seen: Optional[datetime] = None
    rssi_history: Optional[str] = None


class RawPacket(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    timestamp: datetime
    phy: Optional[str] = None
    channel: Optional[int] = None
    rssi: Optional[int] = None
    address: Optional[str] = None
    payload: Optional[bytes] = None


class CaptureSession(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    start_time: datetime
    end_time: Optional[datetime] = None


class DecodedEvent(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    session_id: Optional[int] = Field(default=None, foreign_key="capturesession.id")
    timestamp: datetime
    event_type: str
    data: Optional[str] = None


class AlertRule(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    pattern: str
    threshold: Optional[int] = None

