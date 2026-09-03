---
document_id: account-opening-identity-verification
document_type: kyc
title: Vérification d’identité
language: fr
version: "3.0"
synthetic: true
domain: account-opening
section: account-opening
locale: fr-FR
effective_from: 2026-01-01
active: true
---

# Vérification d’identité

Documentation synthétique destinée à l'environnement de démonstration Smartly Banking AI.

## Objet et périmètre
La vérification compare les données déclarées, le document officiel et un contrôle de présence. Reflets, recadrage, document expiré ou données divergentes provoquent une nouvelle tentative ou une revue manuelle.



## Parcours d'ouverture
Les états sont `STARTED`, `IDENTITY_PENDING`, `KYC_PENDING`, `DOCUMENTS_PENDING`, `REVIEW_PENDING`, `APPROVAL_PENDING`, `APPROVED`, `ACCOUNT_PROVISIONING`, `COMPLETED`, `REJECTED` et `CANCELLED`. `KYC_PENDING` signifie que les contrôles ne sont pas terminés; ce n'est ni une approbation ni un refus.

## Pièces et cohérence
Le dossier comprend une pièce officielle valide et lisible, adresse, résidence fiscale et justificatifs demandés. Faces, bords, dates et zones de lecture doivent apparaître. Nom, naissance, adresse et pays doivent rester cohérents. Image floue, document expiré, divergence, présence incomplète ou homonyme peut entraîner une revue manuelle.

## Rejet et action
Les motifs comprennent identité invérifiable, faux document, inéligibilité, pièces absentes, incohérence non résolue ou contrôle défavorable. Certains détails ne sont pas communicables. Répondre dans le canal sécurisé; répéter le même dépôt défectueux n'accélère pas l'analyse.

## Exemple de question
« Vérification d’identité : quelles règles, quels états et quelle action sont applicables ? »

La réponse explique la règle générale sans inventer de solde, limite, statut ou opération propre à un client.
