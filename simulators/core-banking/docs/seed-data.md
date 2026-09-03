# Deterministic seed data

Flyway migration `V2__seed_deterministic_demo_data.sql` loads synthetic fixtures. They are stable test inputs, not real people, accounts, merchants, rules, or bank policy.

## Customers and ownership boundaries

| Customer | Segment | KYC | Accounts | Active card | Transfers |
| --- | --- | --- | --- | --- | --- |
| `C1024` | PREMIUM | VERIFIED | EUR checking and savings | `CARD-C1024-01` | `TR4587`, `TR4588` |
| `C2048` | STANDARD | VERIFIED | EUR checking | `CARD-C2048-01` | `TR7001` |
| `C4096` | PRIVATE | VERIFIED | EUR checking and USD savings | `CARD-C4096-01` | `TR9001` |
| `C8192` | STANDARD | PENDING | blocked EUR checking | none | none |

`TR4587` belongs to `C1024`, is `REJECTED`, and has deterministic rejection code `PAYMENT_LIMIT_EXCEEDED`. Requesting it through any other customer path returns `TRANSFER_NOT_FOUND`, preventing existence disclosure.

Eight transactions span multiple customers, accounts, currencies, dates, types, and statuses. In particular, C1024 has transactions in July and August 2026 across both accounts, enabling deterministic inclusive date-filter and limit tests.

