from __future__ import annotations
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from services.qdrant import search_clinical, search_radiomics, search_combined

router = APIRouter()


class ClinicalQuery(BaseModel):
    note: str
    top_k: int = 5


class RadiomicsQuery(BaseModel):
    vector: list[float]   # 54-dim normalized
    top_k: int = 5


class CombinedQuery(BaseModel):
    note: str
    vector: list[float]
    top_k: int = 5


@router.post("/clinical")
def retrieve_clinical(query: ClinicalQuery):
    results = search_clinical(query.note, query.top_k)
    return {"results": results}


@router.post("/radiomics")
def retrieve_radiomics(query: RadiomicsQuery):
    results = search_radiomics(query.vector, query.top_k)
    return {"results": results}


@router.post("/combined")
def retrieve_combined(query: CombinedQuery):
    results = search_combined(query.note, query.vector, query.top_k)
    return {"results": results}
