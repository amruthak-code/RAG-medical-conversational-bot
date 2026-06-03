from typing import Optional
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from database import Base


class Patient(Base):
    __tablename__ = "patients"

    patient_id: Mapped[str] = mapped_column(String, primary_key=True)
    patient_name: Mapped[str] = mapped_column(String)
    email: Mapped[str] = mapped_column(String)
    dob: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    emergency_contact_name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    emergency_contact_email: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    procedure_name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    procedure_date: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    followup_date: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    followup_contact: Mapped[Optional[str]] = mapped_column(String, nullable=True)
