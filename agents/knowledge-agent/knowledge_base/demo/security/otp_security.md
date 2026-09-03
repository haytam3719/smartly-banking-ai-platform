---
document_id: security-otp-security
document_type: security
title: Sécurité des codes OTP
language: fr
version: "3.0"
synthetic: true
domain: security
section: security
locale: fr-FR
effective_from: 2026-01-01
active: true
---

# Sécurité des codes OTP

Documentation synthétique destinée à l'environnement de démonstration Smartly Banking AI.

## Objet et périmètre
Un OTP est unique, limité dans le temps et lié à une action. Il ne doit jamais être transmis, même au support. Le client lit le montant et le bénéficiaire dans le message de validation; un code non sollicité peut signaler une attaque.



## Réaction immédiate
Pour une activité suspecte : cesser l'échange, refuser toute validation, ouvrir directement l'application officielle, changer le mot de passe depuis un appareil sûr, fermer les sessions inconnues et bloquer le moyen concerné. Signaler rapidement l'opération avec date, montant et libellé.

## Secrets et appareil
Aucun support ne demande PIN, mot de passe, OTP, CVC ou secret complet. Lire bénéficiaire et montant avant de valider un OTP; refuser une demande non sollicitée. Employer un mot de passe unique, verrouillage automatique et mises à jour. Révoquer un appareil perdu. Éviter applications inconnues, appareils rootés et réseaux affichant une alerte de certificat.

## Hameçonnage
Ne pas suivre un lien reçu sous pression. Vérifier l'information depuis l'application ou un numéro officiel saisi manuellement. Conserver le message comme preuve sans transférer de secrets.

## Exemple de question
« Sécurité des codes OTP : quelles règles, quels états et quelle action sont applicables ? »

La réponse explique la règle générale sans inventer de solde, limite, statut ou opération propre à un client.
