---
document_id: account-opening-account-opening-rejections
document_type: account_opening
title: Rejet et refus d'ouverture de compte
language: fr
version: "3.0"
synthetic: true
domain: account-opening
section: account-opening
locale: fr-FR
effective_from: 2026-01-01
active: true
---

# Rejet et refus d'ouverture de compte

Documentation synthétique destinée à l'environnement de démonstration Smartly Banking AI.

## Objet et périmètre
Une demande peut être refusée pour identité invérifiable, document frauduleux ou expiré, non-éligibilité géographique, contrôle de conformité défavorable ou informations non fournies dans les délais. Certains motifs ne peuvent pas être détaillés.

## Codes de refus
`IDENTITY_NOT_VERIFIED`, `DOCUMENT_EXPIRED`, `DOCUMENT_SUSPECTED_FRAUD`, `ELIGIBILITY_NOT_MET`, `INFORMATION_NOT_PROVIDED` et `COMPLIANCE_CHECK_FAILED` décrivent les catégories de rejet. Une nouvelle tentative n'a de sens qu'après correction d'une cause corrigeable. Le support explique les suites communicables, mais pas toujours le détail d'un contrôle.

## Parcours d'ouverture
Les états sont `STARTED`, `IDENTITY_PENDING`, `KYC_PENDING`, `DOCUMENTS_PENDING`, `REVIEW_PENDING`, `APPROVAL_PENDING`, `APPROVED`, `ACCOUNT_PROVISIONING`, `COMPLETED`, `REJECTED` et `CANCELLED`. `KYC_PENDING` signifie que les contrôles ne sont pas terminés; ce n'est ni une approbation ni un refus.

## Pièces et cohérence
Le dossier comprend une pièce officielle valide et lisible, adresse, résidence fiscale et justificatifs demandés. Faces, bords, dates et zones de lecture doivent apparaître. Nom, naissance, adresse et pays doivent rester cohérents. Image floue, document expiré, divergence, présence incomplète ou homonyme peut entraîner une revue manuelle.

## Rejet et action
Les motifs comprennent identité invérifiable, faux document, inéligibilité, pièces absentes, incohérence non résolue ou contrôle défavorable. Certains détails ne sont pas communicables. Répondre dans le canal sécurisé; répéter le même dépôt défectueux n'accélère pas l'analyse.

## Exemple de question
« Refus d’ouverture : quelles règles, quels états et quelle action sont applicables ? »

La réponse explique la règle générale sans inventer de solde, limite, statut ou opération propre à un client.
