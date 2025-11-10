from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
from typing import List

from auth.schemas import User, Token
from auth.security import get_current_user, role_required
from auth.routes import router as auth_router

from pydantic import BaseModel

app = FastAPI(title="Hospital BI with FHIR and Security")

app.include_router(auth_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

df_visits = pd.read_csv("dinkes-od_17406_jml_kunjungan_pasien_di_fslts_pelayanan_kesehatan__v1_data.csv")
df_cases = pd.read_csv("dinkes-od_15940_jumlah_kasus_penyakit_berdasarkan_jenis_penyakit_data.csv")

# FHIR Observation Simulation (simplified)
class Observation(BaseModel):
    resourceType: str = "Observation"
    id: str
    status: str = "final"
    category: dict
    code: dict
    subject: dict
    effectiveDateTime: str
    valueQuantity: dict


@app.get("/visits")
async def get_visits(user: User = Depends(get_current_user)):
    if user["role"] == "admin":
        data = df_visits.to_dict(orient="records")
    else:
        data = df_visits[df_visits["nama_provinsi"] == "JAWA BARAT"].to_dict(orient="records")
    return data


@app.get("/cases")
async def get_cases(user: User = Depends(get_current_user)):
    if user["role"] == "admin":
        data = df_cases.to_dict(orient="records")
    else:
        data = df_cases[df_cases["nama_provinsi"] == "JAWA BARAT"].to_dict(orient="records")
    return data


@app.get("/fhir/observations", response_model=List[Observation])
async def get_observations(user: User = Depends(get_current_user)):
    observations = []
    for idx, row in df_visits.iterrows():
        obs = Observation(
            id=f"obs-{idx}",
            category={"coding": [{"system": "http://terminology.hl7.org/CodeSystem/observation-category", "code": "administrative"}]},
            code={"coding": [{"system": "http://loinc.org", "code": "81298-1", "display": "Number of visits"}]},
            subject={"reference": f"Hospital/{row['nama_rumah_sakit']}"},
            effectiveDateTime=f"{row['tahun']}-01-01T00:00:00Z",
            valueQuantity={"value": row["jumlah_kunjungan"], "unit": row["satuan"]},
        )
        observations.append(obs)
    return observations