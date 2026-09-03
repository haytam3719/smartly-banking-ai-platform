from datetime import date
from pathlib import Path
from uuid import NAMESPACE_URL, uuid5
from app.loader import DocumentLoader
from app.models import Chunk, DocumentMetadata
from app.ports import EmbeddingPort, VectorStorePort

DISCLAIMER_MARKER="Documentation synthétique destinée à l'environnement de démonstration Smartly Banking AI."
class IngestionPipeline:
    def __init__(self,loader:DocumentLoader,embedder:EmbeddingPort,store:VectorStorePort,chunk_size:int=900,overlap:int=120): self.loader=loader; self.embedder=embedder; self.store=store; self.chunk_size=chunk_size; self.overlap=overlap
    async def ingest_directory(self,path:Path)->int:
        documents=self.loader.load_directory(path); chunks=[]
        for document in documents: chunks.extend(self._chunks(document.content,document.source_filename,document.metadata))
        await self.store.ensure_collection(self.embedder.dimensions)
        vectors=await self.embedder.embed([c.content for c in chunks]) if chunks else []
        await self.store.replace_all(chunks,vectors)
        return len(chunks)
    def _chunks(self,content,source_filename,raw):
        if DISCLAIMER_MARKER not in content: raise ValueError(f"Required synthetic disclaimer missing: {source_filename}")
        required={"document_type","title","section","language","version","synthetic","domain","locale","effective_from","active"}
        if missing:=required-raw.keys(): raise ValueError(f"Missing metadata {sorted(missing)}: {source_filename}")
        if raw["synthetic"] is not True: raise ValueError(f"Synthetic metadata must be true: {source_filename}")
        document_id=str(uuid5(NAMESPACE_URL,f"smartly-demo:{source_filename}:{raw['version']}"))
        # Prefer Markdown section boundaries, then apply bounded windows to long sections.
        sections=[]; current=[]
        for line in content.splitlines():
            if line.startswith("## ") and current:
                sections.append("\n".join(current).strip()); current=[line]
            else: current.append(line)
        if current: sections.append("\n".join(current).strip())
        pieces=[]
        for section in sections:
            start=0
            while start<len(section):
                end=min(len(section),start+self.chunk_size); piece=section[start:end].strip()
                if piece: pieces.append(piece)
                if end==len(section): break
                start=end-self.overlap
        result=[]
        for index,piece in enumerate(pieces):
            metadata=DocumentMetadata(document_id=document_id,document_type=raw["document_type"],title=raw["title"],section=raw["section"],language=raw["language"],version=str(raw["version"]),synthetic=raw["synthetic"],domain=raw["domain"],locale=raw["locale"],effective_from=raw["effective_from"],effective_to=raw.get("effective_to"),active=raw["active"],source_filename=source_filename,chunk_index=index)
            result.append(Chunk(id=str(uuid5(NAMESPACE_URL,f"{document_id}:{index}")),content=piece,metadata=metadata))
        return result
