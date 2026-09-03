---
document_id: cards-lost-or-stolen-card
document_type: lost_card_procedure
title: Carte perdue ou volée
language: fr
version: "3.0"
synthetic: true
domain: cards
section: cards
locale: fr-FR
effective_from: 2026-01-01
active: true
---

# Carte perdue ou volée

Documentation synthétique destinée à l'environnement de démonstration Smartly Banking AI.

## Objet et périmètre
Le client doit bloquer immédiatement la carte dans l’application ou appeler le support 24 h/24, puis vérifier les opérations récentes. Le blocage temporaire convient à une carte égarée; une opposition définitive et un remplacement conviennent au vol ou à la perte confirmée.



## Cycle de vie de la carte
`PENDING_ACTIVATION` précède l'utilisation complète; `ACTIVE` permet les opérations sous réserve des contrôles; `BLOCKED` refuse les nouvelles autorisations; `EXPIRED` indique la fin de validité; `CANCELLED` est définitif. Une autorisation accordée avant blocage peut encore être comptabilisée. Le gel temporaire convient à une carte égarée; perte, vol ou fraude exigent opposition définitive et remplacement.

## Plafonds et refus
Plafonds de paiement et de retrait sont indépendants. Le disponible correspond au plafond applicable moins le cumul et certaines préautorisations. Les motifs usuels sont `CARD_BLOCKED`, `CARD_EXPIRED`, `PAYMENT_LIMIT_EXCEEDED`, `INSUFFICIENT_FUNDS`, `INVALID_CVC`, `ONLINE_PAYMENT_DISABLED`, `INTERNATIONAL_USAGE_DISABLED` et `SECURITY_RESTRICTION`. Corriger la cause avant de retenter.

## Sécurité
Ne jamais communiquer PIN, mot de passe, OTP, CVC ou secret complet. Vérifier commerçant, montant et devise avant validation. Après perte ou opération inconnue : bloquer la carte, contrôler l'historique, contester les débits non reconnus et utiliser un canal officiel.

## Exemple de question
« Carte perdue ou volée : quelles règles, quels états et quelle action sont applicables ? »

La réponse explique la règle générale sans inventer de solde, limite, statut ou opération propre à un client.
