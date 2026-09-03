---
document_id: accounts-transactions
document_type: transactions
title: Opérations et mouvements de compte
language: fr
version: "3.0"
synthetic: true
domain: accounts
section: accounts
locale: fr-FR
effective_from: 2026-01-01
active: true
---

# Opérations et mouvements de compte

Documentation synthétique destinée à l'environnement de démonstration Smartly Banking AI.

## Débit, crédit et disponibilité

Un **débit** diminue le solde du compte; un **crédit** l'augmente. Le signe affiché ne suffit pas toujours à identifier l'origine : un remboursement est un crédit distinct, tandis qu'une contrepassation annule une écriture précédente. Le solde comptable repose sur les écritures `BOOKED`; le solde disponible tient aussi compte des autorisations `PENDING`, réservations et restrictions.

## Cycle d'une transaction

- `PENDING` : opération autorisée ou reçue mais pas définitivement comptabilisée;
- `BOOKED` : écriture définitive portée au compte;
- `REVERSED` : autorisation ou écriture contrepassée;
- `REJECTED` : règle métier ayant empêché l'opération;
- `FAILED` : incident technique sans résultat normal confirmé.

Un paiement carte en attente peut disparaître si le commerçant ne le présente pas, ou être remplacé par un débit `BOOKED` dont le montant ou le libellé diffère légèrement. Une opération `PENDING` peut réduire le solde disponible sans figurer encore dans le solde comptable.

## Dates et libellés

La date d'opération correspond à l'initiation, la date de comptabilisation à l'inscription au compte et la date de valeur au calcul financier. Décalage horaire, week-end et traitement par lots peuvent les différencier. Le libellé commerçant peut utiliser une raison sociale, un prestataire de paiement ou une ville plutôt que l'enseigne connue. L'absence de détail enrichi ne signifie pas que l'écriture est invalide.

## Doublons, rapprochement et remboursements

Avant de conclure à un doublon, comparer montant, devise, commerçant, date et statut. Une autorisation et sa comptabilisation ne constituent qu'un seul achat. Deux écritures `BOOKED` distinctes pour le même achat peuvent justifier une contestation après vérification auprès du commerçant. Un remboursement attendu apparaît comme un nouveau crédit et ne supprime pas nécessairement le débit initial.

## Détail indisponible et action recommandée

Actualiser l'historique, vérifier le relevé et attendre la fin d'une opération encore `PENDING` selon le délai annoncé. Pour une écriture inconnue, sécuriser immédiatement le moyen de paiement et signaler l'opération sans attendre son enrichissement. Pour un doublon comptabilisé, conserver reçus et échanges. Pour un statut incohérent ou une opération disparue après débit, contacter le support avec la référence, jamais avec un PIN, OTP, CVC ou mot de passe.

## Exemples

« Pourquoi mon solde disponible est-il inférieur au solde comptable ? » Une autorisation en attente ou une réservation peut déjà réduire les fonds utilisables.

« Deux lignes identiques sont-elles un double débit ? » Pas nécessairement : vérifier si l'une est `PENDING` et l'autre `BOOKED` avant toute contestation.
