---
document_id: transfers-transfer-rejection-policy
document_type: transfer_policy
title: Politique de rejet des virements
language: fr
version: "3.0"
synthetic: true
domain: transfers
section: transfers
locale: fr-FR
effective_from: 2026-01-01
active: true
---

# Politique de rejet des virements

Documentation synthétique destinée à l'environnement de démonstration Smartly Banking AI.

## Objet et périmètre
Cette politique décrit les motifs normalisés de rejet et la conduite sûre à tenir.

## Scénario TR4587
Pour le scénario synthétique, `TR4587` est `REJECTED` avec `PAYMENT_LIMIT_EXCEEDED`. Ce code signifie que le plafond de paiement applicable est dépassé, distinct de la limite globale de virement. Retenter sans réduction, expiration de fenêtre ou relèvement confirmé échouera probablement.

## Motifs de rejet détaillés
Ces motifs complètent notamment le cas synthétique `TR4587`, rejeté avec `PAYMENT_LIMIT_EXCEEDED`.

- `PAYMENT_LIMIT_EXCEEDED` : vérifier le plafond disponible, réduire ou différer; support si le calcul paraît incohérent.
- `INSUFFICIENT_FUNDS` : solde disponible inférieur au montant et aux frais; retenter après comptabilisation des fonds.
- `BENEFICIARY_BLOCKED` : bénéficiaire bloqué; ne pas le recréer, attendre un déblocage explicite et contacter le support si inconnu.
- `INVALID_BENEFICIARY` : coordonnées ou combinaison pays/devise invalide; obtenir et corriger les données avant réessai.
- `ACCOUNT_RESTRICTED` : compte source non autorisé; suivre la notification et attendre la levée confirmée.
- `TRANSFER_LIMIT_EXCEEDED` : limite unitaire ou cumulée de virement dépassée; réduire ou reporter.
- `COMPLIANCE_REVIEW_REQUIRED` : analyse nécessaire; ne pas fractionner ni retenter, répondre dans le canal sécurisé.
- `TECHNICAL_ERROR` : incident technique; vérifier l'historique avant un unique réessai après rétablissement.
- `EXPIRED_AUTHORIZATION` : validation forte expirée; recommencer seulement si le premier ordre est définitivement rejeté.

Le support est approprié pour état ambigu, débit existant, restriction inconnue, incohérence affichée ou demande de conformité sans suivi.

## Cycle et contrôles
Un virement suit `PENDING`, `PROCESSING`, puis `COMPLETED`; il peut finir `REJECTED`, `FAILED` ou `CANCELLED`. `REJECTED` correspond à une règle métier, `FAILED` à un incident technique. Les contrôles portent sur compte source, solde disponible, montant, devise, bénéficiaire, limites, authentification et conformité. Un ordre programmé est revérifié à l'échéance.

## Délais, réessai et annulation
Jours non ouvrés, heure limite, fuseaux, intermédiaires et revue de conformité peuvent retarder le traitement. Ne jamais retenter lorsque l'état est `PENDING` ou inconnu. Après `REJECTED`, corriger le motif; après `FAILED`, vérifier qu'aucune écriture n'existe. Un ordre `PROCESSING` ou `COMPLETED` n'est généralement plus annulable; un rappel reste sans garantie.

## Bénéficiaire et fraude
Confirmer les coordonnées par un canal indépendant. Ne pas recréer un bénéficiaire bloqué, fractionner un ordre pour contourner un contrôle ni communiquer un OTP. Un retour est une nouvelle écriture de crédit et peut subir des frais d'intermédiaires.

## Exemple de question
« Politique de rejet des virements : quelles règles, quels états et quelle action sont applicables ? »

La réponse explique la règle générale sans inventer de solde, limite, statut ou opération propre à un client.
