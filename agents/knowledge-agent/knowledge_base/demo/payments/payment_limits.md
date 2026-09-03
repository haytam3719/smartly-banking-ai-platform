---
document_id: payments-payment-limits
document_type: payment_limits
title: Limites de paiement
language: fr
version: "3.0"
synthetic: true
domain: payments
section: payments
locale: fr-FR
effective_from: 2026-01-01
active: true
---

# Limites de paiement

Documentation synthétique destinée à l'environnement de démonstration Smartly Banking AI.

## Objet et périmètre
Les limites protègent le compte par montant unitaire, cumul journalier ou fenêtre glissante. Un paiement peut aussi être soumis au plafond de carte, au solde disponible et aux contrôles de sécurité.



## Cycle et contrôles
Un paiement peut être `INITIATED`, `AUTHORIZED`, `PROCESSING`, `COMPLETED`, `REJECTED`, `FAILED` ou `REVERSED`. Une autorisation réserve des fonds; la comptabilisation crée le débit définitif. Les contrôles portent sur solde, plafond, instrument, créancier, référence, authentification et sécurité.

## Motifs et nouvelle tentative
Les motifs incluent `INSUFFICIENT_FUNDS`, `PAYMENT_LIMIT_EXCEEDED`, `ACCOUNT_RESTRICTED`, `CARD_BLOCKED`, `CARD_EXPIRED`, `INVALID_BILL_REFERENCE`, `BILL_ALREADY_PAID`, `BILL_EXPIRED`, `SECURITY_RESTRICTION` et `TECHNICAL_ERROR`. Un rejet métier se retente après correction seulement. Après erreur technique, vérifier historique et statut pour éviter un doublon.

## Doublon et remboursement
Deux lignes peuvent être une autorisation et sa comptabilisation. Un paiement `COMPLETED` n'est pas réputé annulable. Un remboursement est une nouvelle écriture de crédit; une `REVERSAL` contre-passe une autorisation ou une écriture. Conserver reçu, référence, montant, date et échanges.

## Exemple de question
« Limites de paiement : quelles règles, quels états et quelle action sont applicables ? »

La réponse explique la règle générale sans inventer de solde, limite, statut ou opération propre à un client.
