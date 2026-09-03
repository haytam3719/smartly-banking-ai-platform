import json

import pytest

from orchestrator.llm import OpenAICompatibleStructuredRouter
from orchestrator.models import Capability, ChatRequest, Intent, IntentResult, RoutingMode


class Response:
    def __init__(self, result):
        self.result = result

    def raise_for_status(self):
        pass

    def json(self):
        return {"choices": [{"message": {"content": self.result.model_dump_json()}}]}


class IntentClient:
    def __init__(self, intent, **fields):
        self.result = IntentResult(intent=intent, **fields)
        self.requests = []

    async def post(self, url, headers, json, **kwargs):
        self.requests.append(json)
        return Response(self.result)


def request(message):
    return ChatRequest(customer_id="C1024", message=message, locale="fr-FR")


@pytest.mark.parametrize("message", [
    "Quel est mon solde ?", "mon solde ?", "solde ?",
    "quel est le solde de mon compte ?", "combien me reste-t-il ?",
])
async def test_balance_semantic_variants_map_to_one_capability(message):
    client = IntentClient(Intent.BALANCE)
    plan = await OpenAICompatibleStructuredRouter(client, "http://llm/v1", "key", "llama3.2").route(request(message))
    assert plan.mode == RoutingMode.TOOLS_ONLY
    assert [a.capability for a in plan.actions] == [Capability.ACCOUNT_BALANCE_READ]
    payload = client.requests[0]
    assert payload["temperature"] == 0
    assert payload["response_format"]["json_schema"]["name"] == "intent_result"
    schema = payload["response_format"]["json_schema"]["schema"]
    assert "mode" not in json.dumps(schema) and "capability" not in json.dumps(schema)


@pytest.mark.parametrize(("intent", "messages", "capability"), [
    (Intent.TRANSACTIONS, ["Affiche mes dernières transactions.", "mes transactions", "dernières opérations", "historique de mes paiements"], Capability.ACCOUNT_TRANSACTIONS_READ),
    (Intent.CARD_INFO, ["Quel est mon plafond de carte ?", "mon plafond ?", "ma carte est-elle active ?"], Capability.CARD_INFO_READ),
])
async def test_tool_intent_variants(intent, messages, capability):
    for message in messages:
        plan = await OpenAICompatibleStructuredRouter(IntentClient(intent), "http://llm/v1", "key", "llama3.2").route(request(message))
        assert plan.mode == RoutingMode.TOOLS_ONLY
        assert [a.capability for a in plan.actions] == [capability]


@pytest.mark.parametrize("message", ["statut TR4587 ?", "où en est TR4587 ?"])
async def test_transfer_status_variants(message):
    plan = await OpenAICompatibleStructuredRouter(IntentClient(Intent.TRANSFER_STATUS, transfer_id="tr-4587"), "http://llm/v1", "key", "llama3.2").route(request(message))
    assert plan.mode == RoutingMode.TOOLS_ONLY
    assert plan.actions[0].capability == Capability.TRANSFER_STATUS_READ
    assert plan.actions[0].arguments == {"transfer_id": "TR4587"}


@pytest.mark.parametrize("message", ["TR4587 a été refusé, pourquoi ?", "pourquoi mon virement TR4587 ne passe pas ?"])
async def test_transfer_explanation_variants_are_hybrid(message):
    plan = await OpenAICompatibleStructuredRouter(IntentClient(Intent.TRANSFER_EXPLANATION, transfer_id="TR4587"), "http://llm/v1", "key", "llama3.2").route(request(message))
    assert plan.mode == RoutingMode.HYBRID
    assert [a.capability for a in plan.actions] == [Capability.TRANSFER_STATUS_READ, Capability.KNOWLEDGE_SEARCH]


@pytest.mark.parametrize("message", ["bonjour", "bonjourrrrr", "hello", "helllllo", "merciiii", "what can you do?"])
async def test_direct_variants_have_no_actions(message):
    plan = await OpenAICompatibleStructuredRouter(IntentClient(Intent.DIRECT), "http://llm/v1", "key", "llama3.2").route(request(message))
    assert plan.mode == RoutingMode.DIRECT and plan.actions == []


@pytest.mark.parametrize("message", ["Quels sont les frais d'un virement international ?", "comment fonctionne le plafond d'une carte ?", "quels documents pour ouvrir un compte ?"])
async def test_banking_knowledge_variants_use_rag(message):
    plan = await OpenAICompatibleStructuredRouter(IntentClient(Intent.BANKING_KNOWLEDGE), "http://llm/v1", "key", "llama3.2").route(request(message))
    assert plan.mode == RoutingMode.RAG_ONLY
    assert [a.capability for a in plan.actions] == [Capability.KNOWLEDGE_SEARCH]


def test_missing_required_semantic_arguments_clarify():
    mapper = OpenAICompatibleStructuredRouter.to_routing_plan
    assert mapper(IntentResult(intent=Intent.TRANSFER_STATUS)).mode == RoutingMode.CLARIFY
    assert mapper(IntentResult(intent=Intent.ACCOUNT_OPENING)).mode == RoutingMode.CLARIFY
    assert mapper(IntentResult(intent=Intent.ACCOUNT_OPENING_STATUS)).mode == RoutingMode.CLARIFY


def test_account_opening_arguments_are_deterministically_mapped():
    mapper = OpenAICompatibleStructuredRouter.to_routing_plan
    start = mapper(IntentResult(intent=Intent.ACCOUNT_OPENING, account_type="savings", currency="eur"))
    status = mapper(IntentResult(intent=Intent.ACCOUNT_OPENING_STATUS, opening_id="ao-123"))
    assert start.actions[0].arguments == {"account_type": "SAVINGS", "currency": "EUR"}
    assert status.actions[0].arguments == {"opening_id": "AO123"}
