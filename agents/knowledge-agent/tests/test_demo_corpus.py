from pathlib import Path

import pytest

from app.embeddings import DeterministicEmbedding
from app.ingestion import IngestionPipeline
from app.loader import DocumentLoader
from app.models import SearchRequest
from app.service import KnowledgeSearchService
from app.stores import InMemoryVectorStore

CORPUS = Path(__file__).parents[1] / "knowledge_base" / "demo"

QUESTIONS = [
    ("Quels sont les frais d'un virement international ?", "transfers/international_transfer_fees.md"),
    ("Comment fonctionne le plafond d'une carte ?", "cards/card_limits.md"),
    ("Quels documents faut-il pour ouvrir un compte ?", "account-opening/required_documents.md"),
    ("Que faire si je perds ma carte ?", "cards/lost_or_stolen_card.md"),
    ("Pourquoi un virement peut-il être rejeté ?", "transfers/transfer_rejection_policy.md"),
    ("Que signifie PAYMENT_LIMIT_EXCEEDED ?", "transfers/transfer_rejection_policy.md"),
    ("Que faire après une transaction non autorisée ?", "disputes/unauthorized_transactions.md"),
    ("Quelle différence entre plafond de paiement et plafond de retrait ?", "cards/card_payment_limits.md"),
    ("Comment sécuriser mon application bancaire ?", "security/device_security.md"),
]

@pytest.fixture
async def corpus_service():
    embedder = DeterministicEmbedding()
    store = InMemoryVectorStore()
    count = await IngestionPipeline(DocumentLoader(), embedder, store).ingest_directory(CORPUS)
    return count, KnowledgeSearchService(embedder, store)

@pytest.mark.parametrize(("question", "expected_source"), QUESTIONS)
async def test_required_rag_questions(corpus_service, question, expected_source):
    _, service = corpus_service
    response = await service.search(SearchRequest(query=question, top_k=5, locale="fr-FR", score_threshold=0))
    assert expected_source in [result.metadata.source_filename for result in response.results]

async def test_hybrid_transfer_uses_tool_reason_then_rag(corpus_service):
    _, service = corpus_service
    tool_result = {"transfer_id": "TR4587", "status": "REJECTED", "rejection_reason": "PAYMENT_LIMIT_EXCEEDED"}
    response = await service.search(SearchRequest(
        query=f"Motif de rejet {tool_result['rejection_reason']}: signification et action recommandée",
        top_k=4,
        locale="fr-FR",
        filters={"document_type": "transfer_policy"},
        score_threshold=0,
    ))
    assert response.results[0].metadata.source_filename == "transfers/transfer_rejection_policy.md"
    assert "PAYMENT_LIMIT_EXCEEDED" in response.results[0].content
    assert "TR4587" in response.results[0].content

async def test_corpus_count_and_governance(corpus_service):
    count, _ = corpus_service
    assert len(list(CORPUS.rglob("*.md"))) == 60
    assert count > 0
    for document in DocumentLoader().load_directory(CORPUS):
        assert document.metadata["synthetic"] is True
        assert document.metadata["language"] == "fr"
        assert "Documentation synthétique destinée à l'environnement de démonstration Smartly Banking AI." in document.content
