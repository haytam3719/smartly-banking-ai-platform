---
document_id: cards-failed-card-payments
document_type: card_payment_failures
title: Refus de paiement par carte
language: fr
version: "3.0"
synthetic: true
domain: cards
section: cards
locale: fr-FR
effective_from: 2026-01-01
active: true
---

# Refus de paiement par carte

Documentation synthétique destinée à l'environnement de démonstration Smartly Banking AI.

## Pourquoi un paiement par carte peut-il être refusé ?

Un refus signifie que l'autorisation n'a pas été accordée; il ne prouve ni une panne ni une fraude. Les contrôles portent sur le statut de la carte, sa validité, le solde disponible, le plafond de paiement, les options internet ou international, l'authentification et le niveau de risque.

## Codes de refus et actions

- `CARD_BLOCKED` : carte bloquée; ne pas retenter avant déblocage confirmé.
- `CARD_EXPIRED` : carte arrivée à expiration; utiliser la carte de renouvellement activée.
- `PAYMENT_LIMIT_EXCEEDED` : plafond disponible insuffisant; réduire ou différer après vérification du cumul.
- `INSUFFICIENT_FUNDS` : solde disponible insuffisant; tenir compte des autorisations en attente.
- `INVALID_CVC` : cryptogramme incorrect; vérifier sans jamais le communiquer au support.
- `ONLINE_PAYMENT_DISABLED` : achats internet désactivés; modifier l'option dans le canal authentifié si l'achat est légitime.
- `INTERNATIONAL_USAGE_DISABLED` : usage hors zone désactivé; vérifier pays, devise et option internationale.
- `SECURITY_RESTRICTION` : contrôle de risque; ne pas multiplier les essais, vérifier les notifications officielles.

## Échec technique, débit en attente et réessai

Après `TECHNICAL_ERROR`, écran figé ou réponse inconnue, consulter l'historique avant de recommencer. Une autorisation `PENDING` peut réserver les fonds même si le commerçant affiche un échec. Attendre sa résolution ou demander au commerçant la référence de l'autorisation. Retenter sans changement après un rejet métier produit généralement le même résultat et peut déclencher une restriction de sécurité.

## Quand contacter le support

Contacter le support si la carte est `ACTIVE`, le solde et le plafond disponible paraissent suffisants, l'option requise est active et le refus persiste; également en cas de débit comptabilisé pour un achat déclaré échoué ou d'autorisation inconnue. Pour une opération non reconnue, bloquer immédiatement la carte. Ne jamais transmettre PIN, OTP, mot de passe ou CVC.

## Exemple

Question : « Pourquoi mon paiement internet est-il refusé ? »

Réponse documentaire : vérifier successivement statut et expiration de la carte, plafond et solde disponibles, option de paiement en ligne, authentification renforcée et éventuelle restriction de sécurité.
