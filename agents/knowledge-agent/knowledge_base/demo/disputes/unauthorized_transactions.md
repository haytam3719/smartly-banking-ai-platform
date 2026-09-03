---
document_id: disputes-unauthorized-transactions
document_type: disputes
title: Transactions non autorisées
language: fr
version: "3.0"
synthetic: true
domain: disputes
section: disputes
locale: fr-FR
effective_from: 2026-01-01
active: true
---

# Transactions non autorisées

Documentation synthétique destinée à l'environnement de démonstration Smartly Banking AI.

## Objet et périmètre
Après une transaction non autorisée : bloquer la carte ou l’accès, changer les identifiants depuis un appareil sûr, signaler immédiatement l’opération et conserver les preuves. Ne pas contacter un numéro fourni par un message suspect.

## Ordre des actions
Bloquer carte ou accès, changer le mot de passe depuis un appareil sûr, révoquer les sessions inconnues, signaler l'opération avec ses références et conserver les preuves. Une autorisation `PENDING` inconnue doit aussi être signalée. Ne pas attendre une réponse d'un commerçant inconnu avant de sécuriser le compte.

## Qualification et preuves
Distinguer opération inconnue, achat reconnu mais incorrect, doublon, remboursement absent et retrait sans espèces. Relever référence, date, montant, devise, libellé, reçu et échanges, sans transmettre PIN, OTP, CVC ou mot de passe.

## Cycle de réclamation
Une réclamation suit `OPEN`, `UNDER_REVIEW`, `INFORMATION_REQUIRED`, puis `RESOLVED`, `REJECTED` ou `CLOSED`. `INFORMATION_REQUIRED` attend les pièces demandées. Pour une opération non autorisée, sécuriser d'abord accès et carte. Pour doublon ou remboursement, vérifier que les écritures sont `BOOKED`. Un virement erroné peut seulement faire l'objet d'un rappel sans garantie.

## Exemple de question
« Transactions non autorisées : quelles règles, quels états et quelle action sont applicables ? »

La réponse explique la règle générale sans inventer de solde, limite, statut ou opération propre à un client.
