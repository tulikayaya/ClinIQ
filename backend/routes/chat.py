from __future__ import annotations
import json
from openai import OpenAI
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from config import settings
from services.qdrant import search_clinical, search_radiomics, search_combined

router = APIRouter()

client = OpenAI(
    base_url=settings.llm_base_url,
    api_key=settings.llm_api_key,
)

SYSTEM_PROMPT = """You are ClinIQ, a clinical assistant that helps doctors find historically similar glioma/glioblastoma cases.

When the doctor describes a patient, extract the relevant clinical information and use the retrieval tools to find similar cases.

Rules:
- If the doctor provides only clinical information (age, diagnosis, molecular markers, treatment), use retrieve_by_clinical.
- If the doctor uploads an image (radiomic vector provided), use retrieve_by_radiomics.
- If both are available, use retrieve_combined for the best results.
- Present retrieved cases clearly: show the case ID, a summary of the note, and mention that images are available.
- Always explain WHY a case is similar based on shared clinical or imaging features.
"""

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "retrieve_by_clinical",
            "description": "Search for similar cases using a clinical note. Use when the doctor describes patient demographics, diagnosis, molecular markers, or treatment history.",
            "parameters": {
                "type": "object",
                "properties": {
                    "note": {
                        "type": "string",
                        "description": "A synthesized clinical note describing the patient."
                    },
                    "top_k": {
                        "type": "integer",
                        "description": "Number of similar cases to return.",
                        "default": 5
                    }
                },
                "required": ["note"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "retrieve_by_radiomics",
            "description": "Search for similar cases using radiomic features extracted from the patient's MRI scan.",
            "parameters": {
                "type": "object",
                "properties": {
                    "vector": {
                        "type": "array",
                        "items": {"type": "number"},
                        "description": "54-dimensional normalized radiomic feature vector."
                    },
                    "top_k": {"type": "integer", "default": 5}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "retrieve_combined",
            "description": "Search using both clinical note and radiomic features with RRF fusion. Best results when both are available.",
            "parameters": {
                "type": "object",
                "properties": {
                    "note":   {"type": "string"},
                    "vector": {"type": "array", "items": {"type": "number"}},
                    "top_k":  {"type": "integer", "default": 5}
                },
                "required": ["note"]
            }
        }
    }
]


def run_tool(name: str, arguments: dict, radiomic_vector: Optional[list[float]] = None) -> tuple[str, list]:
    top_k = arguments.get("top_k", 5)

    if name == "retrieve_by_clinical":
        results = search_clinical(arguments["note"], top_k)
    elif name == "retrieve_by_radiomics":
        vector = radiomic_vector or arguments.get("vector")
        results = search_radiomics(vector, top_k)
    elif name == "retrieve_combined":
        vector = radiomic_vector or arguments.get("vector")
        results = search_combined(arguments["note"], vector, top_k)
    else:
        return json.dumps({"error": f"Unknown tool: {name}"}), []

    return json.dumps({"results": results}), results


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: list[ChatMessage]
    radiomic_vector: Optional[list[float]] = None


@router.post("")
def chat(request: ChatRequest):
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages += [{"role": m.role, "content": m.content} for m in request.messages]

    if request.radiomic_vector:
        messages[-1]["content"] += (
            f"\n\n[System: Radiomic vector available — {len(request.radiomic_vector)} features extracted from uploaded scan.]"
        )

    response = client.chat.completions.create(
        model=settings.llm_model,
        messages=messages,
        tools=TOOLS,
        tool_choice="auto",
    )

    all_cases = []

    # Agentic loop — keep going until no more tool calls
    while response.choices[0].finish_reason == "tool_calls":
        assistant_msg = response.choices[0].message
        messages.append(assistant_msg)

        for tc in assistant_msg.tool_calls:
            tool_json, cases = run_tool(tc.function.name, json.loads(tc.function.arguments), request.radiomic_vector)
            all_cases.extend(cases)
            messages.append({
                "role":         "tool",
                "tool_call_id": tc.id,
                "content":      tool_json,
            })

        response = client.chat.completions.create(
            model=settings.llm_model,
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",
        )

    return {"reply": response.choices[0].message.content, "cases": all_cases}
