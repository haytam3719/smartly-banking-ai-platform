---
document_id: payments-payment-failures
document_type: payment_failures
title: Échecs de paiement
language: fr
version: "3.0"
synthetic: true
domain: payments
section: payments
locale: fr-FR
effective_from: 2026-01-01
active: true
---

# Échecs de paiement

Documentation synthétique destinée à l'environnement de démonstration Smartly Banking AI.

## Objet et périmètre
Un paiement peut échouer pour fonds insuffisants, plafond atteint, carte bloquée ou expirée, authentification non terminée, commerçant non pris en charge ou incident technique. Avant de réessayer, vérifier le statut afin d’éviter un doublon.



## Cycle et contrôles
Un paiement peut être `INITIATED`, `AUTHORIZED`, `PROCESSING`, `COMPLETED`, `REJECTED`, `FAILED` ou `REVERSED`. Une autorisation réserve des fonds; la comptabilisation crée le débit définitif. Les contrôles portent sur solde, plafond, instrument, créancier, référence, authentification et sécurité.

## Motifs et nouvelle tentative
Les motifs incluent `INSUFFICIENT_FUNDS`, `PAYMENT_LIMIT_EXCEEDED`, `ACCOUNT_RESTRICTED`, `CARD_BLOCKED`, `CARD_EXPIRED`, `INVALID_BILL_REFERENCE`, `BILL_ALREADY_PAID`, `BILL_EXPIRED`, `SECURITY_RESTRICTION` et `TECHNICAL_ERROR`. Un rejet métier se retente après correction seulement. Après erreur technique, vérifier historique et statut pour éviter un doublon.

## Doublon et remboursement
Deux lignes peuvent être une autorisation et sa comptabilisation. Un paiement `COMPLETED` n'est pas réputé annulable. Un remboursement est une nouvelle écriture de crédit; une `REVERSAL` contre-passe une autorisation ou une écriture. Conserver reçu, référence, montant, date et échanges.

## Exemple de question
« Échecs de paiement : quelles règles, quels états et quelle action sont applicables ? »

La réponse explique la règle générale sans inventer de solde, limite, statut ou opération propre à un client.
