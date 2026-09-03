from datetime import date
from typing import Any
from pydantic import BaseModel, ConfigDict, Field

DOCUMENT_TYPES = str
class SearchFilters(BaseModel):
    model_config=ConfigDict(extra="forbid")
    document_type: DOCUMENT_TYPES | None=None
    version: str | None=None
class SearchRequest(BaseModel):
    model_config=ConfigDict(extra="forbid")
    query: str=Field(min_length=1,max_length=1000)
    top_k: int=Field(default=4,ge=1,le=20)
    locale: str=Field(pattern=r"^[a-z]{2,3}(?:-[A-Z]{2})?$")
    filters: SearchFilters=Field(default_factory=SearchFilters)
    score_threshold: float=Field(default=.15,ge=0,le=1)
class DocumentMetadata(BaseModel):
    model_config=ConfigDict(extra="forbid")
    document_id: str; document_type: DOCUMENT_TYPES; version: str; locale: str
    title: str; section: str; language: str; synthetic: bool; domain: str
    effective_from: date; effective_to: date | None=None; active: bool
    source_filename: str; chunk_index: int=Field(ge=0)
class Chunk(BaseModel):
    id: str; content: str; metadata: DocumentMetadata
class SearchHit(BaseModel):
    content: str; document_id: str; document_type: DOCUMENT_TYPES; score: float=Field(ge=0,le=1); metadata: DocumentMetadata
class SearchResponse(BaseModel):
    results: list[SearchHit]; context_characters: int=Field(ge=0)
class LoadedDocument(BaseModel):
    content: str; source_filename: str; metadata: dict[str,Any]
