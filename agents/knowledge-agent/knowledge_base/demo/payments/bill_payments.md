---
document_id: payments-bill-payments
document_type: bill_payments
title: "Pourquoi le paiement d'une facture échoue : échecs et rejets"
language: fr
version: "3.0"
synthetic: true
domain: payments
section: payments
locale: fr-FR
effective_from: 2026-01-01
active: true
---

# Pourquoi le paiement d'une facture échoue : échecs et rejets

Documentation synthétique destinée à l'environnement de démonstration Smartly Banking AI.

## Objet et périmètre
Le paiement de facture utilise une référence créancier et une référence de facture. Le client contrôle l’échéance, le montant et le bénéficiaire. Une programmation n’assure pas l’exécution si le solde ou les limites sont insuffisants le jour venu.

## Factures et codes dédiés
Le paiement exige fournisseur, référence, montant, compte de débit et devise compatible. Une facture est `PENDING`, `PAID`, `EXPIRED` ou `CANCELLED`. `BILL_ALREADY_PAID` signifie qu'elle est déjà réglée : vérifier historique, fournisseur, référence et montant, puis ne pas retenter. `BILL_EXPIRED` exige une nouvelle facture. `INVALID_BILL_REFERENCE` impose une correction. `PAYMENT_LIMIT_EXCEEDED`, `INSUFFICIENT_FUNDS` et `ACCOUNT_RESTRICTED` nécessitent respectivement une limite disponible, des fonds ou la levée d'une restriction. Une programmation est intégralement revérifiée à l'échéance.

## Cycle et contrôles
Un paiement peut être `INITIATED`, `AUTHORIZED`, `PROCESSING`, `COMPLETED`, `REJECTED`, `FAILED` ou `REVERSED`. Une autorisation réserve des fonds; la comptabilisation crée le débit définitif. Les contrôles portent sur solde, plafond, instrument, créancier, référence, authentification et sécurité.

## Motifs et nouvelle tentative
Les motifs incluent `INSUFFICIENT_FUNDS`, `PAYMENT_LIMIT_EXCEEDED`, `ACCOUNT_RESTRICTED`, `CARD_BLOCKED`, `CARD_EXPIRED`, `INVALID_BILL_REFERENCE`, `BILL_ALREADY_PAID`, `BILL_EXPIRED`, `SECURITY_RESTRICTION` et `TECHNICAL_ERROR`. Un rejet métier se retente après correction seulement. Après erreur technique, vérifier historique et statut pour éviter un doublon.

## Doublon et remboursement
Deux lignes peuvent être une autorisation et sa comptabilisation. Un paiement `COMPLETED` n'est pas réputé annulable. Un remboursement est une nouvelle écriture de crédit; une `REVERSAL` contre-passe une autorisation ou une écriture. Conserver reçu, référence, montant, date et échanges.

## Exemple de question
« Paiement de factures : quelles règles, quels états et quelle action sont applicables ? »

La réponse explique la règle générale sans inventer de solde, limite, statut ou opération propre à un client.
