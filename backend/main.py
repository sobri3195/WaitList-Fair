from __future__ import annotations

from dataclasses import dataclass
from typing import List

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

app = FastAPI(
    title="WaitList-Fair API",
    description=(
        "API prioritisasi jadwal radioterapi berbasis estimasi risiko progression-while-waiting "
        "dengan komponen fairness sederhana antarkelompok."
    ),
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class PatientInput(BaseModel):
    patient_id: str = Field(..., description="ID pasien")
    age: int = Field(..., ge=0, le=120)
    waiting_days: int = Field(..., ge=0)
    stage: int = Field(..., ge=1, le=4, description="Stadium kanker 1-4")
    ecog: int = Field(..., ge=0, le=4, description="ECOG performance status")
    tumor_growth_rate: float = Field(..., ge=0.0, le=1.0)
    socioeconomic_index: float = Field(
        ..., ge=0.0, le=1.0, description="1.0 = paling rentan"
    )
    group: str = Field(..., description="Kelompok fairness (mis. wilayah/jenis pembiayaan)")


class PrioritizationRequest(BaseModel):
    patients: List[PatientInput]


@dataclass
class RiskWeights:
    waiting_days: float = 0.22
    stage: float = 0.28
    ecog: float = 0.15
    tumor_growth_rate: float = 0.25
    age: float = 0.05
    socioeconomic_index: float = 0.05


def normalize_waiting_days(days: int) -> float:
    return min(days / 90.0, 1.0)


def normalize_age(age: int) -> float:
    # Risiko sedikit meningkat pada usia lanjut untuk menjaga contoh model sederhana.
    return min(max((age - 40) / 40.0, 0.0), 1.0)


def estimate_progression_risk(patient: PatientInput, w: RiskWeights) -> float:
    score = (
        w.waiting_days * normalize_waiting_days(patient.waiting_days)
        + w.stage * (patient.stage / 4.0)
        + w.ecog * (patient.ecog / 4.0)
        + w.tumor_growth_rate * patient.tumor_growth_rate
        + w.age * normalize_age(patient.age)
        + w.socioeconomic_index * patient.socioeconomic_index
    )
    return round(min(max(score, 0.0), 1.0), 4)


def fairness_boost(patient: PatientInput) -> float:
    # Faktor fairness sederhana: kelompok rentan sosial mendapatkan dorongan kecil.
    return round(0.08 * patient.socioeconomic_index, 4)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/prioritize")
def prioritize(payload: PrioritizationRequest) -> dict:
    weights = RiskWeights()
    prioritized = []

    for p in payload.patients:
        risk = estimate_progression_risk(p, weights)
        boost = fairness_boost(p)
        priority_score = round(min(risk + boost, 1.0), 4)

        prioritized.append(
            {
                "patient_id": p.patient_id,
                "group": p.group,
                "risk_score": risk,
                "fairness_boost": boost,
                "priority_score": priority_score,
                "estimated_wait_impact": round(risk * p.waiting_days, 2),
                "suggested_priority": "HIGH" if priority_score >= 0.65 else "MEDIUM" if priority_score >= 0.45 else "LOW",
            }
        )

    prioritized.sort(key=lambda x: x["priority_score"], reverse=True)

    group_stats: dict[str, list[float]] = {}
    for row in prioritized:
        group_stats.setdefault(row["group"], []).append(row["priority_score"])

    avg_by_group = {
        g: round(sum(vals) / len(vals), 4)
        for g, vals in group_stats.items()
    }

    fairness_gap = 0.0
    if avg_by_group:
        fairness_gap = round(max(avg_by_group.values()) - min(avg_by_group.values()), 4)

    return {
        "manual_baseline": "Urutan berbasis judgement klinis tanpa skor AI terstruktur.",
        "prioritized": prioritized,
        "metrics": {
            "high_risk_count": sum(1 for p in prioritized if p["suggested_priority"] == "HIGH"),
            "avg_priority_by_group": avg_by_group,
            "equity_gap": fairness_gap,
        },
    }
