from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, String, BigInteger, PrimaryKeyConstraint, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import List
from pydantic import BaseModel

from auth.schemas import User
from auth.security import get_current_user
from auth.routes import router as auth_router

DATABASE_URL = "mysql+pymysql://root:root@localhost/hospital_bi"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()

class Covid(Base):
    __tablename__ = 'covid'
    state = Column(String(50), nullable=False)
    date = Column(String(20), nullable=False)
    critical_staffing_shortage_today_yes = Column(BigInteger, nullable=True)
    critical_staffing_shortage_today_no = Column(BigInteger, nullable=True)
    inpatient_beds_used_covid = Column(String(20), nullable=True)
    staffed_adult_icu_bed_occupancy = Column(String(20), nullable=True)
    total_adult_patients_hospitalized_confirmed_covid = Column(String(20), nullable=True)
    # Add more columns you want

    __table_args__ = (
        PrimaryKeyConstraint('state', 'date'),
    )

class CovidResponse(BaseModel):
    state: str
    date: str
    critical_staffing_shortage_today_yes: int | None
    critical_staffing_shortage_today_no: int | None
    inpatient_beds_used_covid: str | None
    staffed_adult_icu_bed_occupancy: str | None
    total_adult_patients_hospitalized_confirmed_covid: str | None
    class Config:
        orm_mode = True

app = FastAPI()
app.include_router(auth_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/covid", response_model=List[CovidResponse])
async def get_covid(user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    query = db.query(Covid)
    if user["role"] != "admin":
        query = query.filter(Covid.state == "ID")
    return query.all()

@app.get("/covid/kpis")
async def get_kpis(db: Session = Depends(get_db)):
    # Using func.sum and func.avg to calculate KPIs
    total_covid_patients = db.query(func.sum(Covid.total_adult_patients_hospitalized_confirmed_covid.cast(BigInteger))).scalar() or 0
    avg_icu_occupancy = db.query(func.avg(Covid.staffed_adult_icu_bed_occupancy.cast(BigInteger))).scalar() or 0
    staffing_shortage_yes = db.query(func.sum(Covid.critical_staffing_shortage_today_yes)).scalar() or 0

    return {
        "total_covid_patients": total_covid_patients,
        "avg_icu_occupancy": avg_icu_occupancy,
        "staffing_shortage_today_yes": staffing_shortage_yes,
    }