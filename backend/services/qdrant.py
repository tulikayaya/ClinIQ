from __future__ import annotations
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, VectorParams, Distance, Prefetch, FusionQuery, Fusion
from config import settings
from services.embedder import embed_note

_client = QdrantClient(host=settings.qdrant_host, port=settings.qdrant_port)
COLLECTION = settings.qdrant_collection


def _format_results(hits: list) -> list[dict]:
    return [
        {
            "case_id":   hit.payload.get("case_id"),
            "note":      hit.payload.get("note"),
            "image_url": hit.payload.get("image_url"),
            "score":     hit.score,
        }
        for hit in hits
    ]


def search_clinical(note: str, top_k: int = 5) -> list[dict]:
    vector = embed_note(note)
    hits = _client.query_points(
        collection_name=COLLECTION,
        query=vector,
        using="clinical",
        limit=top_k,
    ).points
    return _format_results(hits)


def search_radiomics(vector: list[float], top_k: int = 5) -> list[dict]:
    hits = _client.query_points(
        collection_name=COLLECTION,
        query=vector,
        using="radiomics",
        limit=top_k,
    ).points
    return _format_results(hits)


def search_combined(note: str, vector: list[float], top_k: int = 5) -> list[dict]:
    clinical_vector = embed_note(note)
    hits = _client.query_points(
        collection_name=COLLECTION,
        prefetch=[
            Prefetch(query=vector,           using="radiomics", limit=top_k * 3),
            Prefetch(query=clinical_vector,  using="clinical",  limit=top_k * 3),
        ],
        query=FusionQuery(fusion=Fusion.RRF),
        limit=top_k,
    ).points
    return _format_results(hits)


def upsert_point(
    point_id: int,
    case_id: str,
    note: str,
    radiomic_vector: list[float],
    clinical_vector: list[float],
    image_url: str = "",
):
    _client.upsert(
        collection_name=COLLECTION,
        points=[
            PointStruct(
                id=point_id,
                vector={
                    "radiomics": radiomic_vector,
                    "clinical":  clinical_vector,
                },
                payload={
                    "case_id":   case_id,
                    "note":      note,
                    "image_url": image_url,
                },
            )
        ],
    )
