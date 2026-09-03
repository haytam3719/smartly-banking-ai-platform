---
document_id: digital-banking-authentication
document_type: digital_banking
title: Authentification
language: fr
version: "3.0"
synthetic: true
domain: digital-banking
section: digital-banking
locale: fr-FR
effective_from: 2026-01-01
active: true
---

# Authentification

Documentation synthétique destinée à l'environnement de démonstration Smartly Banking AI.

## Objet et périmètre
La connexion combine identifiant, secret et, selon le risque, second facteur. Une nouvelle localisation, un appareil inconnu ou une opération sensible déclenche une vérification renforcée. Plusieurs échecs provoquent un verrouillage temporaire.



## Authentification et appareil
La connexion combine selon le risque mot de passe, appareil enregistré, biométrie et validation renforcée. La biométrie déverrouille une clé locale et ne remplace pas le code de secours. Nouvel appareil, localisation inhabituelle, échecs répétés ou opération sensible peut imposer un contrôle supplémentaire.

## Dépannage sûr
Vérifier réseau, heure automatique, version de l'application et identifiant. Après verrouillage, ne pas multiplier les essais. Réinitialiser depuis l'application ou le site officiel, créer un mot de passe unique et invalider les anciennes sessions. Lors d'une panne, ne pas répéter une opération au statut inconnu; vérifier l'historique après rétablissement. Révoquer immédiatement un appareil perdu.

## Exemple de question
« Authentification : quelles règles, quels états et quelle action sont applicables ? »

La réponse explique la règle générale sans inventer de solde, limite, statut ou opération propre à un client.
