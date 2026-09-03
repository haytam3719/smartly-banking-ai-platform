---
document_id: account-opening-kyc-process
document_type: kyc
title: KYC_PENDING et processus KYC
language: fr
version: "3.0"
synthetic: true
domain: account-opening
section: account-opening
locale: fr-FR
effective_from: 2026-01-01
active: true
---

# KYC_PENDING et processus KYC

Documentation synthétique destinée à l'environnement de démonstration Smartly Banking AI.

## Objet et périmètre
Le KYC de démonstration recueille l’identité, vérifie le document et la présence réelle, contrôle l’adresse et la résidence fiscale, puis effectue les vérifications de conformité. Il peut aboutir à vérifié, informations supplémentaires requises ou refusé.



## Parcours d'ouverture
Les états sont `STARTED`, `IDENTITY_PENDING`, `KYC_PENDING`, `DOCUMENTS_PENDING`, `REVIEW_PENDING`, `APPROVAL_PENDING`, `APPROVED`, `ACCOUNT_PROVISIONING`, `COMPLETED`, `REJECTED` et `CANCELLED`. `KYC_PENDING` signifie que les contrôles ne sont pas terminés; ce n'est ni une approbation ni un refus.

## Pièces et cohérence
Le dossier comprend une pièce officielle valide et lisible, adresse, résidence fiscale et justificatifs demandés. Faces, bords, dates et zones de lecture doivent apparaître. Nom, naissance, adresse et pays doivent rester cohérents. Image floue, document expiré, divergence, présence incomplète ou homonyme peut entraîner une revue manuelle.

## Rejet et action
Les motifs comprennent identité invérifiable, faux document, inéligibilité, pièces absentes, incohérence non résolue ou contrôle défavorable. Certains détails ne sont pas communicables. Répondre dans le canal sécurisé; répéter le même dépôt défectueux n'accélère pas l'analyse.

## Exemple de question
« Processus KYC : quelles règles, quels états et quelle action sont applicables ? »

La réponse explique la règle générale sans inventer de solde, limite, statut ou opération propre à un client.
