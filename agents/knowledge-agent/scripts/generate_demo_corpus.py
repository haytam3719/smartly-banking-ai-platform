"""Upgrade the checked-in synthetic banking corpus to the current format."""
from pathlib import Path
import re

ROOT=Path(__file__).parents[1]/"knowledge_base"/"demo"
DISCLAIMER="Documentation synthétique destinée à l'environnement de démonstration Smartly Banking AI."

TYPES={
"bill_payments":"bill_payments","payment_failures":"payment_failures","payment_limits":"payment_limits","duplicate_payments":"payment_failures","refunds":"payment_failures",
"transfer_rejection_policy":"transfer_policy","international_transfer_fees":"international_transfer_fees","transfer_limits":"transfer_limits","transfer_processing_times":"transfer_processing","scheduled_transfers":"transfer_processing","beneficiary_management":"beneficiary_management","international_transfers":"international_transfers","domestic_transfers":"domestic_transfers","transfer_cancellation":"transfer_processing",
"card_limits":"card_limits","card_payment_limits":"card_limits","cash_withdrawal_limits":"card_limits","failed_card_payments":"card_payment_failures","lost_or_stolen_card":"lost_card_procedure","card_security":"card_security","online_payments":"card_security","international_card_usage":"card_security","card_activation":"card_lifecycle","card_blocking":"card_lifecycle","card_expiration":"card_lifecycle","card_replacement":"card_lifecycle",
"required_documents":"account_opening","account_opening_requirements":"account_opening","account_opening_steps":"account_opening","account_opening_rejections":"account_opening","eligibility_rules":"account_opening","kyc_process":"kyc","identity_verification":"kyc",
"current_accounts":"account_accounts","savings_accounts":"account_accounts","dormant_accounts":"account_accounts","account_closure":"account_accounts","account_statements":"account_statements","account_fees":"account_fees",
"complaint_process":"complaints","mobile_banking":"digital_banking","authentication":"digital_banking","biometric_login":"digital_banking","password_reset":"digital_banking","service_availability":"digital_banking"}

GUIDES={
"accounts":'''## Soldes, dates et écritures
Le **solde comptable** additionne les écritures définitives. Le **solde disponible** retranche aussi autorisations, réservations et blocages; il détermine généralement si un débit peut être accepté. Date d'opération, date de comptabilisation et date de valeur peuvent différer. Une écriture `PENDING` réserve parfois des fonds, `BOOKED` est comptabilisée et `REVERSED` a été contrepassée.

## Statuts du compte
`ACTIVE` autorise le fonctionnement normal; `RESTRICTED` interdit certaines opérations; `BLOCKED` suspend les nouveaux débits; `DORMANT` signale une absence prolongée d'activité initiée par le titulaire; `CLOSED` est définitif. Une restriction ne se contourne pas par des essais répétés. Le client consulte les notifications sécurisées et fournit seulement les éléments demandés.

## Cas pratiques
Avant de déclarer un doublon, comparer montant, devise, libellé et statut des lignes. Une clôture exige le traitement du solde résiduel, des opérations en attente, cartes, prélèvements et virements programmés, puis la conservation du relevé final.''',
"cards":'''## Cycle de vie de la carte
`PENDING_ACTIVATION` précède l'utilisation complète; `ACTIVE` permet les opérations sous réserve des contrôles; `BLOCKED` refuse les nouvelles autorisations; `EXPIRED` indique la fin de validité; `CANCELLED` est définitif. Une autorisation accordée avant blocage peut encore être comptabilisée. Le gel temporaire convient à une carte égarée; perte, vol ou fraude exigent opposition définitive et remplacement.

## Plafonds et refus
Plafonds de paiement et de retrait sont indépendants. Le disponible correspond au plafond applicable moins le cumul et certaines préautorisations. Les motifs usuels sont `CARD_BLOCKED`, `CARD_EXPIRED`, `PAYMENT_LIMIT_EXCEEDED`, `INSUFFICIENT_FUNDS`, `INVALID_CVC`, `ONLINE_PAYMENT_DISABLED`, `INTERNATIONAL_USAGE_DISABLED` et `SECURITY_RESTRICTION`. Corriger la cause avant de retenter.

## Sécurité
Ne jamais communiquer PIN, mot de passe, OTP, CVC ou secret complet. Vérifier commerçant, montant et devise avant validation. Après perte ou opération inconnue : bloquer la carte, contrôler l'historique, contester les débits non reconnus et utiliser un canal officiel.''',
"transfers":'''## Cycle et contrôles
Un virement suit `PENDING`, `PROCESSING`, puis `COMPLETED`; il peut finir `REJECTED`, `FAILED` ou `CANCELLED`. `REJECTED` correspond à une règle métier, `FAILED` à un incident technique. Les contrôles portent sur compte source, solde disponible, montant, devise, bénéficiaire, limites, authentification et conformité. Un ordre programmé est revérifié à l'échéance.

## Délais, réessai et annulation
Jours non ouvrés, heure limite, fuseaux, intermédiaires et revue de conformité peuvent retarder le traitement. Ne jamais retenter lorsque l'état est `PENDING` ou inconnu. Après `REJECTED`, corriger le motif; après `FAILED`, vérifier qu'aucune écriture n'existe. Un ordre `PROCESSING` ou `COMPLETED` n'est généralement plus annulable; un rappel reste sans garantie.

## Bénéficiaire et fraude
Confirmer les coordonnées par un canal indépendant. Ne pas recréer un bénéficiaire bloqué, fractionner un ordre pour contourner un contrôle ni communiquer un OTP. Un retour est une nouvelle écriture de crédit et peut subir des frais d'intermédiaires.''',
"payments":'''## Cycle et contrôles
Un paiement peut être `INITIATED`, `AUTHORIZED`, `PROCESSING`, `COMPLETED`, `REJECTED`, `FAILED` ou `REVERSED`. Une autorisation réserve des fonds; la comptabilisation crée le débit définitif. Les contrôles portent sur solde, plafond, instrument, créancier, référence, authentification et sécurité.

## Motifs et nouvelle tentative
Les motifs incluent `INSUFFICIENT_FUNDS`, `PAYMENT_LIMIT_EXCEEDED`, `ACCOUNT_RESTRICTED`, `CARD_BLOCKED`, `CARD_EXPIRED`, `INVALID_BILL_REFERENCE`, `BILL_ALREADY_PAID`, `BILL_EXPIRED`, `SECURITY_RESTRICTION` et `TECHNICAL_ERROR`. Un rejet métier se retente après correction seulement. Après erreur technique, vérifier historique et statut pour éviter un doublon.

## Doublon et remboursement
Deux lignes peuvent être une autorisation et sa comptabilisation. Un paiement `COMPLETED` n'est pas réputé annulable. Un remboursement est une nouvelle écriture de crédit; une `REVERSAL` contre-passe une autorisation ou une écriture. Conserver reçu, référence, montant, date et échanges.''',
"account-opening":'''## Parcours d'ouverture
Les états sont `STARTED`, `IDENTITY_PENDING`, `KYC_PENDING`, `DOCUMENTS_PENDING`, `REVIEW_PENDING`, `APPROVAL_PENDING`, `APPROVED`, `ACCOUNT_PROVISIONING`, `COMPLETED`, `REJECTED` et `CANCELLED`. `KYC_PENDING` signifie que les contrôles ne sont pas terminés; ce n'est ni une approbation ni un refus.

## Pièces et cohérence
Le dossier comprend une pièce officielle valide et lisible, adresse, résidence fiscale et justificatifs demandés. Faces, bords, dates et zones de lecture doivent apparaître. Nom, naissance, adresse et pays doivent rester cohérents. Image floue, document expiré, divergence, présence incomplète ou homonyme peut entraîner une revue manuelle.

## Rejet et action
Les motifs comprennent identité invérifiable, faux document, inéligibilité, pièces absentes, incohérence non résolue ou contrôle défavorable. Certains détails ne sont pas communicables. Répondre dans le canal sécurisé; répéter le même dépôt défectueux n'accélère pas l'analyse.''',
"security":'''## Réaction immédiate
Pour une activité suspecte : cesser l'échange, refuser toute validation, ouvrir directement l'application officielle, changer le mot de passe depuis un appareil sûr, fermer les sessions inconnues et bloquer le moyen concerné. Signaler rapidement l'opération avec date, montant et libellé.

## Secrets et appareil
Aucun support ne demande PIN, mot de passe, OTP, CVC ou secret complet. Lire bénéficiaire et montant avant de valider un OTP; refuser une demande non sollicitée. Employer un mot de passe unique, verrouillage automatique et mises à jour. Révoquer un appareil perdu. Éviter applications inconnues, appareils rootés et réseaux affichant une alerte de certificat.

## Hameçonnage
Ne pas suivre un lien reçu sous pression. Vérifier l'information depuis l'application ou un numéro officiel saisi manuellement. Conserver le message comme preuve sans transférer de secrets.''',
"disputes":'''## Qualification et preuves
Distinguer opération inconnue, achat reconnu mais incorrect, doublon, remboursement absent et retrait sans espèces. Relever référence, date, montant, devise, libellé, reçu et échanges, sans transmettre PIN, OTP, CVC ou mot de passe.

## Cycle de réclamation
Une réclamation suit `OPEN`, `UNDER_REVIEW`, `INFORMATION_REQUIRED`, puis `RESOLVED`, `REJECTED` ou `CLOSED`. `INFORMATION_REQUIRED` attend les pièces demandées. Pour une opération non autorisée, sécuriser d'abord accès et carte. Pour doublon ou remboursement, vérifier que les écritures sont `BOOKED`. Un virement erroné peut seulement faire l'objet d'un rappel sans garantie.''',
"digital-banking":'''## Authentification et appareil
La connexion combine selon le risque mot de passe, appareil enregistré, biométrie et validation renforcée. La biométrie déverrouille une clé locale et ne remplace pas le code de secours. Nouvel appareil, localisation inhabituelle, échecs répétés ou opération sensible peut imposer un contrôle supplémentaire.

## Dépannage sûr
Vérifier réseau, heure automatique, version de l'application et identifiant. Après verrouillage, ne pas multiplier les essais. Réinitialiser depuis l'application ou le site officiel, créer un mot de passe unique et invalider les anciennes sessions. Lors d'une panne, ne pas répéter une opération au statut inconnu; vérifier l'historique après rétablissement. Révoquer immédiatement un appareil perdu.'''}

SPECIAL={
"bill_payments":'''## Factures et codes dédiés
Le paiement exige fournisseur, référence, montant, compte de débit et devise compatible. Une facture est `PENDING`, `PAID`, `EXPIRED` ou `CANCELLED`. `BILL_ALREADY_PAID` signifie qu'elle est déjà réglée : vérifier historique, fournisseur, référence et montant, puis ne pas retenter. `BILL_EXPIRED` exige une nouvelle facture. `INVALID_BILL_REFERENCE` impose une correction. `PAYMENT_LIMIT_EXCEEDED`, `INSUFFICIENT_FUNDS` et `ACCOUNT_RESTRICTED` nécessitent respectivement une limite disponible, des fonds ou la levée d'une restriction. Une programmation est intégralement revérifiée à l'échéance.''',
"card_limits":'''## Calcul du plafond disponible
Plafond contractuel, cumul utilisé et disponible sont distincts. Dans la simulation, les paiements utilisent 30 jours glissants et les retraits 7 jours glissants. Une préautorisation réduit parfois le disponible; remboursement et annulation ne le restaurent pas toujours immédiatement. Un disponible de retrait ne compense jamais un plafond de paiement épuisé.''',
"required_documents":'''## Documents généralement requis
Passeport ou carte nationale d'identité valide, justificatif de domicile récent lorsque demandé, informations de résidence fiscale et éventuelles pièces complémentaires. Les images doivent être nettes, en couleur, non recadrées et complètes. Un document expiré, illisible, modifié ou divergent entraîne `DOCUMENTS_PENDING`, `IDENTITY_PENDING` ou une revue. Transmettre uniquement dans le parcours sécurisé.''',
"account_opening_rejections":'''## Codes de refus
`IDENTITY_NOT_VERIFIED`, `DOCUMENT_EXPIRED`, `DOCUMENT_SUSPECTED_FRAUD`, `ELIGIBILITY_NOT_MET`, `INFORMATION_NOT_PROVIDED` et `COMPLIANCE_CHECK_FAILED` décrivent les catégories de rejet. Une nouvelle tentative n'a de sens qu'après correction d'une cause corrigeable. Le support explique les suites communicables, mais pas toujours le détail d'un contrôle.''',
"unauthorized_transactions":'''## Ordre des actions
Bloquer carte ou accès, changer le mot de passe depuis un appareil sûr, révoquer les sessions inconnues, signaler l'opération avec ses références et conserver les preuves. Une autorisation `PENDING` inconnue doit aussi être signalée. Ne pas attendre une réponse d'un commerçant inconnu avant de sécuriser le compte.''',
"atm_cash_not_received":'''## Débit sans espèces
Ne pas réessayer immédiatement. Noter distributeur, lieu, heure, montant, référence et message; conserver le reçu. Vérifier `PENDING` ou `BOOKED`. Une autorisation peut être libérée automatiquement; si le débit devient comptabilisé ou dépasse le délai annoncé, ouvrir une contestation. Le rapprochement peut nécessiter journal et caisse du distributeur.''',
"international_transfer_fees":'''## Composition des frais
Le coût combine potentiellement émission, conversion, marge de change et correspondants. `OUR` met les frais annoncés à charge de l'émetteur, `SHA` partage les frais bancaires, `BEN` les déduit du montant reçu. Le taux peut changer entre programmation et traitement. Le montant reçu peut varier du fait du change ou d'un intermédiaire. Aucun tarif bancaire réel n'est affirmé; le récapitulatif avant confirmation prévaut.''',
"transfer_rejection_policy":'''## Scénario TR4587
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

Le support est approprié pour état ambigu, débit existant, restriction inconnue, incohérence affichée ou demande de conformité sans suivi.'''}

def upgrade(path):
    text=path.read_text(encoding="utf-8"); front,body=text.split("---",2)[1:]
    # The script is a migration for legacy templates; curated v3 documents are authoritative.
    if re.search(r'^version:\s*["\']3\.0["\']\s*$',front,re.M): return
    title=re.search(r'^title:\s*["\']?(.*?)["\']?$',front,re.M).group(1).strip('"\'')
    match=re.search(r"## Objet\n(.*?)(?=\n## )",body,re.S)
    intro=(match.group(1).strip() if match else f"Ce document décrit {title.lower()}.")
    intro=re.sub(r"[^.]*\b(?:RAG|Tool|Agent|Knowledge Agent)\b[^.]*\.","",intro).strip()
    domain=path.parent.name; stem=path.stem; dtype=TYPES.get(stem,{"security":"security","disputes":"disputes","general":"banking_reference"}.get(domain,domain.replace("-","_")))
    content=f"# {title}\n\n{DISCLAIMER}\n\n## Objet et périmètre\n{intro}\n\n{SPECIAL.get(stem,'')}\n\n{GUIDES.get(domain,'')}\n\n## Exemple de question\n« {title} : quelles règles, quels états et quelle action sont applicables ? »\n\nLa réponse explique la règle générale sans inventer de solde, limite, statut ou opération propre à un client.\n"
    safe_title=title.replace('"', '\\"')
    meta=f'''---\ndocument_id: {domain}-{stem.replace('_','-')}\ndocument_type: {dtype}\ntitle: "{safe_title}"\nlanguage: fr\nversion: "3.0"\nsynthetic: true\ndomain: {domain}\nsection: {domain}\nlocale: fr-FR\neffective_from: 2026-01-01\nactive: true\n---\n'''
    path.write_text(meta+"\n"+content,encoding="utf-8")

def main():
    for path in sorted(ROOT.rglob("*.md")): upgrade(path)
    print(f"Upgraded {len(list(ROOT.rglob('*.md')))} synthetic Markdown documents")

if __name__=="__main__": main()
