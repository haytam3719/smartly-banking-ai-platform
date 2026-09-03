---
document_id: transfers-international-transfer-fees
document_type: international_transfer_fees
title: Frais des virements internationaux
language: fr
version: "3.0"
synthetic: true
domain: transfers
section: transfers
locale: fr-FR
effective_from: 2026-01-01
active: true
---

# Frais des virements internationaux

Documentation synthétique destinée à l'environnement de démonstration Smartly Banking AI.

## Objet et périmètre
Dans le scénario, un virement hors zone EUR coûte 7 EUR plus 0,25 % du montant, plafonné à 35 EUR. Le change ajoute une marge synthétique de 0,80 %. Les frais OUR peuvent ajouter 15 EUR; SHA partage les frais et BEN les déduit du montant reçu.

## Composition des frais
Le coût combine potentiellement émission, conversion, marge de change et correspondants. `OUR` met les frais annoncés à charge de l'émetteur, `SHA` partage les frais bancaires, `BEN` les déduit du montant reçu. Le taux peut changer entre programmation et traitement. Le montant reçu peut varier du fait du change ou d'un intermédiaire. Aucun tarif bancaire réel n'est affirmé; le récapitulatif avant confirmation prévaut.

## Cycle et contrôles
Un virement suit `PENDING`, `PROCESSING`, puis `COMPLETED`; il peut finir `REJECTED`, `FAILED` ou `CANCELLED`. `REJECTED` correspond à une règle métier, `FAILED` à un incident technique. Les contrôles portent sur compte source, solde disponible, montant, devise, bénéficiaire, limites, authentification et conformité. Un ordre programmé est revérifié à l'échéance.

## Délais, réessai et annulation
Jours non ouvrés, heure limite, fuseaux, intermédiaires et revue de conformité peuvent retarder le traitement. Ne jamais retenter lorsque l'état est `PENDING` ou inconnu. Après `REJECTED`, corriger le motif; après `FAILED`, vérifier qu'aucune écriture n'existe. Un ordre `PROCESSING` ou `COMPLETED` n'est généralement plus annulable; un rappel reste sans garantie.

## Bénéficiaire et fraude
Confirmer les coordonnées par un canal indépendant. Ne pas recréer un bénéficiaire bloqué, fractionner un ordre pour contourner un contrôle ni communiquer un OTP. Un retour est une nouvelle écriture de crédit et peut subir des frais d'intermédiaires.

## Exemple de question
« Frais des virements internationaux : quelles règles, quels états et quelle action sont applicables ? »

La réponse explique la règle générale sans inventer de solde, limite, statut ou opération propre à un client.
