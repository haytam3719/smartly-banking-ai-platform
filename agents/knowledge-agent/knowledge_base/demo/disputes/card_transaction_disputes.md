---
document_id: disputes-card-transaction-disputes
document_type: disputes
title: Contestation d’une opération carte
language: fr
version: "3.0"
synthetic: true
domain: disputes
section: disputes
locale: fr-FR
effective_from: 2026-01-01
active: true
---

# Contestation d’une opération carte

Documentation synthétique destinée à l'environnement de démonstration Smartly Banking AI.

## Objet et périmètre
Le client identifie l’opération, vérifie libellé et proches autorisés, puis contacte le commerçant si l’achat est reconnu mais incorrect. Pour fraude, il bloque la carte et conteste sans attendre. Les justificatifs et délais sont communiqués dans le canal authentifié.



## Qualification et preuves
Distinguer opération inconnue, achat reconnu mais incorrect, doublon, remboursement absent et retrait sans espèces. Relever référence, date, montant, devise, libellé, reçu et échanges, sans transmettre PIN, OTP, CVC ou mot de passe.

## Cycle de réclamation
Une réclamation suit `OPEN`, `UNDER_REVIEW`, `INFORMATION_REQUIRED`, puis `RESOLVED`, `REJECTED` ou `CLOSED`. `INFORMATION_REQUIRED` attend les pièces demandées. Pour une opération non autorisée, sécuriser d'abord accès et carte. Pour doublon ou remboursement, vérifier que les écritures sont `BOOKED`. Un virement erroné peut seulement faire l'objet d'un rappel sans garantie.

## Exemple de question
« Contestation d’une opération carte : quelles règles, quels états et quelle action sont applicables ? »

La réponse explique la règle générale sans inventer de solde, limite, statut ou opération propre à un client.
