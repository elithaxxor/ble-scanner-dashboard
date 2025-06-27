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
