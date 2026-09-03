---
document_id: accounts-account-closure
document_type: account_accounts
title: Clôture d’un compte
language: fr
version: "3.0"
synthetic: true
domain: accounts
section: accounts
locale: fr-FR
effective_from: 2026-01-01
active: true
---

# Clôture d’un compte

Documentation synthétique destinée à l'environnement de démonstration Smartly Banking AI.

## Objet et périmètre
La clôture exige un solde nul, aucune opération en attente et le traitement des cartes ou paiements rattachés. Le client doit fournir un compte de destination pour un solde positif. La demande est confirmée dans un canal authentifié.



## Soldes, dates et écritures
Le **solde comptable** additionne les écritures définitives. Le **solde disponible** retranche aussi autorisations, réservations et blocages; il détermine généralement si un débit peut être accepté. Date d'opération, date de comptabilisation et date de valeur peuvent différer. Une écriture `PENDING` réserve parfois des fonds, `BOOKED` est comptabilisée et `REVERSED` a été contrepassée.

## Statuts du compte
`ACTIVE` autorise le fonctionnement normal; `RESTRICTED` interdit certaines opérations; `BLOCKED` suspend les nouveaux débits; `DORMANT` signale une absence prolongée d'activité initiée par le titulaire; `CLOSED` est définitif. Une restriction ne se contourne pas par des essais répétés. Le client consulte les notifications sécurisées et fournit seulement les éléments demandés.

## Cas pratiques
Avant de déclarer un doublon, comparer montant, devise, libellé et statut des lignes. Une clôture exige le traitement du solde résiduel, des opérations en attente, cartes, prélèvements et virements programmés, puis la conservation du relevé final.

## Exemple de question
« Clôture d’un compte : quelles règles, quels états et quelle action sont applicables ? »

La réponse explique la règle générale sans inventer de solde, limite, statut ou opération propre à un client.
