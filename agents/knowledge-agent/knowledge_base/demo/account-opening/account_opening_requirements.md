---
document_id: account-opening-account-opening-requirements
document_type: account_opening
title: Conditions d’ouverture
language: fr
version: "3.0"
synthetic: true
domain: account-opening
section: account-opening
locale: fr-FR
effective_from: 2026-01-01
active: true
---

# Conditions d’ouverture

Documentation synthétique destinée à l'environnement de démonstration Smartly Banking AI.

## Objet et périmètre
L’ouverture de démonstration nécessite une identité vérifiable, une adresse dans un pays pris en charge, un âge minimal de 18 ans et des informations de résidence fiscale. L’acceptation reste soumise aux contrôles KYC et de conformité.



## Parcours d'ouverture
Les états sont `STARTED`, `IDENTITY_PENDING`, `KYC_PENDING`, `DOCUMENTS_PENDING`, `REVIEW_PENDING`, `APPROVAL_PENDING`, `APPROVED`, `ACCOUNT_PROVISIONING`, `COMPLETED`, `REJECTED` et `CANCELLED`. `KYC_PENDING` signifie que les contrôles ne sont pas terminés; ce n'est ni une approbation ni un refus.

## Pièces et cohérence
Le dossier comprend une pièce officielle valide et lisible, adresse, résidence fiscale et justificatifs demandés. Faces, bords, dates et zones de lecture doivent apparaître. Nom, naissance, adresse et pays doivent rester cohérents. Image floue, document expiré, divergence, présence incomplète ou homonyme peut entraîner une revue manuelle.

## Rejet et action
Les motifs comprennent identité invérifiable, faux document, inéligibilité, pièces absentes, incohérence non résolue ou contrôle défavorable. Certains détails ne sont pas communicables. Répondre dans le canal sécurisé; répéter le même dépôt défectueux n'accélère pas l'analyse.

## Exemple de question
« Conditions d’ouverture : quelles règles, quels états et quelle action sont applicables ? »

La réponse explique la règle générale sans inventer de solde, limite, statut ou opération propre à un client.
