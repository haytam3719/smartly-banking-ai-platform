---
document_id: account-opening-required-documents
document_type: account_opening
title: Documents requis pour ouvrir un compte
language: fr
version: "3.0"
synthetic: true
domain: account-opening
section: account-opening
locale: fr-FR
effective_from: 2026-01-01
active: true
---

# Documents requis pour ouvrir un compte

Documentation synthétique destinée à l'environnement de démonstration Smartly Banking AI.

## Objet et périmètre
Sont acceptés dans le scénario : passeport ou carte nationale d’identité en cours de validité, justificatif de domicile de moins de trois mois et, si demandé, justificatif de résidence fiscale. Les copies doivent être lisibles et complètes.

## Documents généralement requis
Passeport ou carte nationale d'identité valide, justificatif de domicile récent lorsque demandé, informations de résidence fiscale et éventuelles pièces complémentaires. Les images doivent être nettes, en couleur, non recadrées et complètes. Un document expiré, illisible, modifié ou divergent entraîne `DOCUMENTS_PENDING`, `IDENTITY_PENDING` ou une revue. Transmettre uniquement dans le parcours sécurisé.

## Parcours d'ouverture
Les états sont `STARTED`, `IDENTITY_PENDING`, `KYC_PENDING`, `DOCUMENTS_PENDING`, `REVIEW_PENDING`, `APPROVAL_PENDING`, `APPROVED`, `ACCOUNT_PROVISIONING`, `COMPLETED`, `REJECTED` et `CANCELLED`. `KYC_PENDING` signifie que les contrôles ne sont pas terminés; ce n'est ni une approbation ni un refus.

## Pièces et cohérence
Le dossier comprend une pièce officielle valide et lisible, adresse, résidence fiscale et justificatifs demandés. Faces, bords, dates et zones de lecture doivent apparaître. Nom, naissance, adresse et pays doivent rester cohérents. Image floue, document expiré, divergence, présence incomplète ou homonyme peut entraîner une revue manuelle.

## Rejet et action
Les motifs comprennent identité invérifiable, faux document, inéligibilité, pièces absentes, incohérence non résolue ou contrôle défavorable. Certains détails ne sont pas communicables. Répondre dans le canal sécurisé; répéter le même dépôt défectueux n'accélère pas l'analyse.

## Exemple de question
« Documents requis pour ouvrir un compte : quelles règles, quels états et quelle action sont applicables ? »

La réponse explique la règle générale sans inventer de solde, limite, statut ou opération propre à un client.
