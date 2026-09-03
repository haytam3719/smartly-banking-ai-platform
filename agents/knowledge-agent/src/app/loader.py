from pathlib import Path
import frontmatter
import yaml
from pypdf import PdfReader
from app.models import LoadedDocument
class DocumentLoader:
    def load_directory(self,path:Path)->list[LoadedDocument]:
        return [self.load(p,path) for p in sorted(path.rglob('*')) if p.is_file() and p.suffix.lower() in {'.md','.txt','.pdf'}]
    def load(self,path:Path,root:Path|None=None)->LoadedDocument:
        suffix=path.suffix.lower()
        if suffix in {'.md','.txt'}:
            post=frontmatter.load(path,encoding='utf-8'); content=post.content; metadata=dict(post.metadata)
        elif suffix=='.pdf':
            reader=PdfReader(str(path)); content='\n'.join(page.extract_text() or '' for page in reader.pages)
            sidecar=path.with_suffix('.metadata.yaml')
            if not sidecar.is_file(): raise ValueError(f'Required PDF metadata sidecar missing: {sidecar.name}')
            metadata=yaml.safe_load(sidecar.read_text(encoding='utf-8')) or {}
        else: raise ValueError(f'Unsupported document format: {suffix}')
        # Preserve Markdown headings: ingestion uses them as semantic chunk boundaries.
        lines=[" ".join(line.split()) for line in content.splitlines()]
        content="\n".join(line for line in lines if line).strip()
        return LoadedDocument(content=content,source_filename=str(path.relative_to(root or path.parent)).replace('\\','/'),metadata=metadata)
