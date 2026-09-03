---
document_id: transfers-scheduled-transfers
document_type: transfer_processing
title: Virements programmés
language: fr
version: "3.0"
synthetic: true
domain: transfers
section: transfers
locale: fr-FR
effective_from: 2026-01-01
active: true
---

# Virements programmés

Documentation synthétique destinée à l'environnement de démonstration Smartly Banking AI.

## Objet et périmètre
Un ordre unique ou récurrent s’exécute à la date choisie. Si elle tombe un jour non ouvré, le standard part le jour ouvré suivant. Solde, limites, statut du bénéficiaire et autorisation sont revérifiés à chaque échéance.



## Cycle et contrôles
Un virement suit `PENDING`, `PROCESSING`, puis `COMPLETED`; il peut finir `REJECTED`, `FAILED` ou `CANCELLED`. `REJECTED` correspond à une règle métier, `FAILED` à un incident technique. Les contrôles portent sur compte source, solde disponible, montant, devise, bénéficiaire, limites, authentification et conformité. Un ordre programmé est revérifié à l'échéance.

## Délais, réessai et annulation
Jours non ouvrés, heure limite, fuseaux, intermédiaires et revue de conformité peuvent retarder le traitement. Ne jamais retenter lorsque l'état est `PENDING` ou inconnu. Après `REJECTED`, corriger le motif; après `FAILED`, vérifier qu'aucune écriture n'existe. Un ordre `PROCESSING` ou `COMPLETED` n'est généralement plus annulable; un rappel reste sans garantie.

## Bénéficiaire et fraude
Confirmer les coordonnées par un canal indépendant. Ne pas recréer un bénéficiaire bloqué, fractionner un ordre pour contourner un contrôle ni communiquer un OTP. Un retour est une nouvelle écriture de crédit et peut subir des frais d'intermédiaires.

## Exemple de question
« Virements programmés : quelles règles, quels états et quelle action sont applicables ? »

La réponse explique la règle générale sans inventer de solde, limite, statut ou opération propre à un client.
