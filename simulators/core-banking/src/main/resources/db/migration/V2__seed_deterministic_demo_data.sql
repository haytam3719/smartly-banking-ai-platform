INSERT INTO customer(customer_id,first_name,last_name,segment,kyc_status,country) VALUES
 ('C1024','Camille','Martin','PREMIUM','VERIFIED','FR'),
 ('C2048','Alex','Dubois','STANDARD','VERIFIED','FR'),
 ('C4096','Samira','Benali','PRIVATE','VERIFIED','BE'),
 ('C8192','Noah','Bernard','STANDARD','PENDING','FR');

INSERT INTO account(account_id,customer_id,type,currency,available_balance,status) VALUES
 ('ACC-C1024-EUR','C1024','CHECKING','EUR',2450.75,'ACTIVE'),
 ('ACC-C1024-SAV','C1024','SAVINGS','EUR',12500.00,'ACTIVE'),
 ('ACC-C2048-EUR','C2048','CHECKING','EUR',875.20,'ACTIVE'),
 ('ACC-C4096-EUR','C4096','CHECKING','EUR',42800.00,'ACTIVE'),
 ('ACC-C4096-USD','C4096','SAVINGS','USD',6200.50,'ACTIVE'),
 ('ACC-C8192-EUR','C8192','CHECKING','EUR',0.00,'BLOCKED');

INSERT INTO bank_transaction(transaction_id,account_id,type,amount,currency,merchant,description,occurred_at,status) VALUES
 ('TX1001','ACC-C1024-EUR','CARD_PAYMENT',-42.80,'EUR','Boulangerie République','Card purchase','2026-08-20 08:15:00+00','BOOKED'),
 ('TX1002','ACC-C1024-EUR','TRANSFER_IN',1800.00,'EUR',NULL,'Salary','2026-08-01 06:00:00+00','BOOKED'),
 ('TX1003','ACC-C1024-EUR','DIRECT_DEBIT',-89.99,'EUR','Énergie Démo','Utility bill','2026-07-15 10:30:00+00','BOOKED'),
 ('TX1004','ACC-C1024-SAV','TRANSFER_IN',500.00,'EUR',NULL,'Monthly savings','2026-08-02 09:00:00+00','BOOKED'),
 ('TX2001','ACC-C2048-EUR','CARD_PAYMENT',-16.40,'EUR','Transit Démo','Transport','2026-08-21 17:45:00+00','BOOKED'),
 ('TX2002','ACC-C2048-EUR','CASH_WITHDRAWAL',-100.00,'EUR','ATM-TEST-02','Cash withdrawal','2026-06-10 12:00:00+00','BOOKED'),
 ('TX4001','ACC-C4096-EUR','TRANSFER_OUT',-1200.00,'EUR',NULL,'Synthetic supplier payment','2026-08-18 14:20:00+00','BOOKED'),
 ('TX4002','ACC-C4096-USD','TRANSFER_IN',2500.00,'USD',NULL,'Synthetic incoming transfer','2026-08-25 11:10:00+00','PENDING');

INSERT INTO payment_card(card_id,customer_id,type,status,expiration_date,payment_limit,amount_used,currency) VALUES
 ('CARD-C1024-01','C1024','DEBIT','ACTIVE','2029-12-31',2500.00,1840.00,'EUR'),
 ('CARD-C1024-OLD','C1024','DEBIT','CANCELLED','2026-01-31',1500.00,0.00,'EUR'),
 ('CARD-C2048-01','C2048','DEBIT','ACTIVE','2028-10-31',1200.00,215.30,'EUR'),
 ('CARD-C4096-01','C4096','CREDIT','ACTIVE','2030-06-30',10000.00,2300.00,'EUR');

INSERT INTO bank_transfer(transfer_id,customer_id,beneficiary,amount,currency,created_at,status,rejection_reason) VALUES
 ('TR4587','C1024','Synthetic Beneficiary A',3000.00,'EUR','2026-08-22 09:30:00+00','REJECTED','PAYMENT_LIMIT_EXCEEDED'),
 ('TR4588','C1024','Synthetic Beneficiary B',125.00,'EUR','2026-08-24 13:00:00+00','COMPLETED',NULL),
 ('TR7001','C2048','Synthetic Beneficiary C',75.00,'EUR','2026-08-23 16:15:00+00','PROCESSING',NULL),
 ('TR9001','C4096','Synthetic Beneficiary D',4200.00,'EUR','2026-08-19 08:10:00+00','COMPLETED',NULL);
