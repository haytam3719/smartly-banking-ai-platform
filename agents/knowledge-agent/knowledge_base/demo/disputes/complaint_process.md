---
document_id: disputes-complaint-process
document_type: complaints
title: Processus de réclamation
language: fr
version: "3.0"
synthetic: true
domain: disputes
section: disputes
locale: fr-FR
effective_from: 2026-01-01
active: true
---

# Processus de réclamation

Documentation synthétique destinée à l'environnement de démonstration Smartly Banking AI.

## Objet et périmètre
Une réclamation reçoit un identifiant et un accusé sous deux jours ouvrés. Une réponse cible est fournie sous quinze jours ouvrés, ou une notification explique le retard, sans dépasser trente-cinq jours dans ce scénario. Une escalade interne est disponible.



## Qualification et preuves
Distinguer opération inconnue, achat reconnu mais incorrect, doublon, remboursement absent et retrait sans espèces. Relever référence, date, montant, devise, libellé, reçu et échanges, sans transmettre PIN, OTP, CVC ou mot de passe.

## Cycle de réclamation
Une réclamation suit `OPEN`, `UNDER_REVIEW`, `INFORMATION_REQUIRED`, puis `RESOLVED`, `REJECTED` ou `CLOSED`. `INFORMATION_REQUIRED` attend les pièces demandées. Pour une opération non autorisée, sécuriser d'abord accès et carte. Pour doublon ou remboursement, vérifier que les écritures sont `BOOKED`. Un virement erroné peut seulement faire l'objet d'un rappel sans garantie.

## Exemple de question
« Processus de réclamation : quelles règles, quels états et quelle action sont applicables ? »

La réponse explique la règle générale sans inventer de solde, limite, statut ou opération propre à un client.
