import asyncio
import os
from pathlib import Path

from app.embeddings import DeterministicEmbedding
from app.models import SearchRequest
from app.service import KnowledgeSearchService
from app.ingestion import IngestionPipeline
from app.loader import DocumentLoader
from app.stores import InMemoryVectorStore, QdrantVectorStore

CASES = [
    ("Quels sont les frais d'un virement international ?", "transfers/international_transfer_fees.md", None),
    ("Comment fonctionne le plafond d'une carte ?", "cards/card_limits.md", None),
    ("Quels documents faut-il pour ouvrir un compte ?", "account-opening/required_documents.md", None),
    ("Que faire si je perds ma carte ?", "cards/lost_or_stolen_card.md", None),
    ("Pourquoi un virement peut-il être rejeté ?", "transfers/transfer_rejection_policy.md", None),
    ("Que signifie PAYMENT_LIMIT_EXCEEDED ?", "transfers/transfer_rejection_policy.md", "transfer_policy"),
    ("Que faire après une transaction non autorisée ?", "disputes/unauthorized_transactions.md", None),
    ("Quelle différence entre plafond de paiement et plafond de retrait ?", "cards/card_payment_limits.md", None),
    ("Comment sécuriser mon application bancaire ?", "security/device_security.md", None),
    ("Mon virement TR4587 a été refusé. Pourquoi et que dois-je faire ? Tool: PAYMENT_LIMIT_EXCEEDED", "transfers/transfer_rejection_policy.md", "transfer_policy"),
    ("Pourquoi un virement peut-il être rejeté ?", "transfers/transfer_rejection_policy.md", None),
    ("Que faire après PAYMENT_LIMIT_EXCEEDED ?", "transfers/transfer_rejection_policy.md", "transfer_policy"),
    ("Pourquoi un paiement par carte peut-il être refusé ?", "cards/failed_card_payments.md", None),
    ("Que signifie KYC_PENDING ?", "account-opening/kyc_process.md", None),
    ("Pourquoi une ouverture de compte peut-elle être rejetée ?", "account-opening/account_opening_rejections.md", None),
    ("Pourquoi le paiement de ma facture a-t-il échoué ?", "payments/bill_payments.md", None),
    ("Que signifie BILL_ALREADY_PAID ?", "payments/bill_payments.md", "bill_payments"),
    ("Que faire si un distributeur débite mon compte sans délivrer d'espèces ?", "disputes/atm_cash_not_received.md", None),
]

async def main():
    embedder=DeterministicEmbedding(int(os.getenv("EMBEDDING_DIMENSIONS","128")))
    if os.getenv("VERIFY_STORE", "qdrant") == "memory":
        store=InMemoryVectorStore()
        corpus=Path(__file__).parents[3] / "knowledge_base" / "demo"
        await IngestionPipeline(DocumentLoader(),embedder,store).ingest_directory(corpus)
    else:
        store=QdrantVectorStore(os.getenv("QDRANT_URL","http://qdrant:6333"),os.getenv("QDRANT_COLLECTION","smartly_knowledge"))
    service=KnowledgeSearchService(embedder,store)
    failures=0
    for question,expected,document_type in CASES:
        request=SearchRequest(query=question,top_k=5,locale="fr-FR",score_threshold=0,filters={"document_type":document_type} if document_type else {})
        response=await service.search(request)
        sources=[hit.metadata.source_filename for hit in response.results]
        passed=expected in sources
        failures+=not passed
        top=response.results[0] if response.results else None
        section=(top.content.splitlines()[0] if top else "NONE")
        score=f"{top.score:.4f}" if top else "-"
        print(f"{'PASS' if passed else 'FAIL'} | {question} | top={sources[0] if sources else 'NONE'} | type={top.document_type if top else '-'} | score={score} | section={section} | expected_rank={(sources.index(expected)+1) if passed else '-'}")
    if failures: raise SystemExit(f"{failures} retrieval case(s) failed")

if __name__=="__main__": asyncio.run(main())
