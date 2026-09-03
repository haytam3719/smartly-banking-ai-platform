---
document_id: disputes-atm-cash-not-received
document_type: disputes
title: Espèces non reçues au distributeur
language: fr
version: "3.0"
synthetic: true
domain: disputes
section: disputes
locale: fr-FR
effective_from: 2026-01-01
active: true
---

# Espèces non reçues au distributeur

Documentation synthétique destinée à l'environnement de démonstration Smartly Banking AI.

## Objet et périmètre
Si le compte est débité sans remise d’espèces, noter lieu, heure, montant et exploitant, conserver le reçu et attendre la régularisation automatique jusqu’à deux jours ouvrés. Ensuite déposer une contestation; ne jamais forcer le distributeur.

## Débit sans espèces
Ne pas réessayer immédiatement. Noter distributeur, lieu, heure, montant, référence et message; conserver le reçu. Vérifier `PENDING` ou `BOOKED`. Une autorisation peut être libérée automatiquement; si le débit devient comptabilisé ou dépasse le délai annoncé, ouvrir une contestation. Le rapprochement peut nécessiter journal et caisse du distributeur.

## Qualification et preuves
Distinguer opération inconnue, achat reconnu mais incorrect, doublon, remboursement absent et retrait sans espèces. Relever référence, date, montant, devise, libellé, reçu et échanges, sans transmettre PIN, OTP, CVC ou mot de passe.

## Cycle de réclamation
Une réclamation suit `OPEN`, `UNDER_REVIEW`, `INFORMATION_REQUIRED`, puis `RESOLVED`, `REJECTED` ou `CLOSED`. `INFORMATION_REQUIRED` attend les pièces demandées. Pour une opération non autorisée, sécuriser d'abord accès et carte. Pour doublon ou remboursement, vérifier que les écritures sont `BOOKED`. Un virement erroné peut seulement faire l'objet d'un rappel sans garantie.

## Exemple de question
« Espèces non reçues au distributeur : quelles règles, quels états et quelle action sont applicables ? »

La réponse explique la règle générale sans inventer de solde, limite, statut ou opération propre à un client.
