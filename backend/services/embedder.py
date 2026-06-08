from __future__ import annotations
import torch
from transformers import AutoTokenizer, AutoModel

_tokenizer = None
_model = None


def _load():
    global _tokenizer, _model
    if _model is None:
        _tokenizer = AutoTokenizer.from_pretrained("ncbi/MedCPT-Article-Encoder")
        _model = AutoModel.from_pretrained("ncbi/MedCPT-Article-Encoder")
        _model.eval()


def embed_note(text: str) -> list[float]:
    _load()
    encoded = _tokenizer(
        [[text, text]],
        truncation=True,
        padding=True,
        return_tensors="pt",
        max_length=512,
    )
    with torch.no_grad():
        output = _model(**encoded)
    return output.last_hidden_state[:, 0, :].squeeze().tolist()
