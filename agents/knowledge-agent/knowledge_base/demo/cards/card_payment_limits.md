---
document_id: cards-card-payment-limits
document_type: card_limits
title: Plafond de paiement
language: fr
version: "3.0"
synthetic: true
domain: cards
section: cards
locale: fr-FR
effective_from: 2026-01-01
active: true
---

# Plafond de paiement

Documentation synthétique destinée à l'environnement de démonstration Smartly Banking AI.

## Objet et périmètre
Le plafond de paiement cumule les paiements autorisés sur 30 jours glissants dans la démonstration. Les préautorisations peuvent réserver du disponible. Un remboursement ne restaure pas toujours immédiatement le plafond.



## Cycle de vie de la carte
`PENDING_ACTIVATION` précède l'utilisation complète; `ACTIVE` permet les opérations sous réserve des contrôles; `BLOCKED` refuse les nouvelles autorisations; `EXPIRED` indique la fin de validité; `CANCELLED` est définitif. Une autorisation accordée avant blocage peut encore être comptabilisée. Le gel temporaire convient à une carte égarée; perte, vol ou fraude exigent opposition définitive et remplacement.

## Plafonds et refus
Plafonds de paiement et de retrait sont indépendants. Le disponible correspond au plafond applicable moins le cumul et certaines préautorisations. Les motifs usuels sont `CARD_BLOCKED`, `CARD_EXPIRED`, `PAYMENT_LIMIT_EXCEEDED`, `INSUFFICIENT_FUNDS`, `INVALID_CVC`, `ONLINE_PAYMENT_DISABLED`, `INTERNATIONAL_USAGE_DISABLED` et `SECURITY_RESTRICTION`. Corriger la cause avant de retenter.

## Sécurité
Ne jamais communiquer PIN, mot de passe, OTP, CVC ou secret complet. Vérifier commerçant, montant et devise avant validation. Après perte ou opération inconnue : bloquer la carte, contrôler l'historique, contester les débits non reconnus et utiliser un canal officiel.

## Exemple de question
« Plafond de paiement : quelles règles, quels états et quelle action sont applicables ? »

La réponse explique la règle générale sans inventer de solde, limite, statut ou opération propre à un client.
