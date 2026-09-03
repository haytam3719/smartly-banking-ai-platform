CREATE TABLE customer (
  customer_id VARCHAR(64) PRIMARY KEY,
  first_name VARCHAR(100) NOT NULL,
  last_name VARCHAR(100) NOT NULL,
  segment VARCHAR(32) NOT NULL,
  kyc_status VARCHAR(32) NOT NULL,
  country VARCHAR(2) NOT NULL
);

CREATE TABLE account (
  account_id VARCHAR(64) PRIMARY KEY,
  customer_id VARCHAR(64) NOT NULL REFERENCES customer(customer_id),
  type VARCHAR(32) NOT NULL,
  currency VARCHAR(3) NOT NULL,
  available_balance DECIMAL(19,2) NOT NULL,
  status VARCHAR(32) NOT NULL
);
CREATE INDEX idx_account_customer ON account(customer_id);

CREATE TABLE bank_transaction (
  transaction_id VARCHAR(64) PRIMARY KEY,
  account_id VARCHAR(64) NOT NULL REFERENCES account(account_id),
  type VARCHAR(32) NOT NULL,
  amount DECIMAL(19,2) NOT NULL,
  currency VARCHAR(3) NOT NULL,
  merchant VARCHAR(160),
  description VARCHAR(500),
  occurred_at TIMESTAMP WITH TIME ZONE NOT NULL,
  status VARCHAR(32) NOT NULL
);
CREATE INDEX idx_transaction_account_date ON bank_transaction(account_id, occurred_at DESC);

CREATE TABLE payment_card (
  card_id VARCHAR(64) PRIMARY KEY,
  customer_id VARCHAR(64) NOT NULL REFERENCES customer(customer_id),
  type VARCHAR(32) NOT NULL,
  status VARCHAR(32) NOT NULL,
  expiration_date DATE NOT NULL,
  payment_limit DECIMAL(19,2) NOT NULL,
  amount_used DECIMAL(19,2) NOT NULL,
  currency VARCHAR(3) NOT NULL
);
CREATE INDEX idx_card_customer ON payment_card(customer_id);

CREATE TABLE bank_transfer (
  transfer_id VARCHAR(64) PRIMARY KEY,
  customer_id VARCHAR(64) NOT NULL REFERENCES customer(customer_id),
  beneficiary VARCHAR(160) NOT NULL,
  amount DECIMAL(19,2) NOT NULL,
  currency VARCHAR(3) NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL,
  status VARCHAR(32) NOT NULL,
  rejection_reason VARCHAR(64)
);
CREATE INDEX idx_transfer_customer ON bank_transfer(customer_id);

CREATE TABLE account_opening (
  opening_record_id VARCHAR(36) PRIMARY KEY,
  opening_id VARCHAR(100) NOT NULL,
  idempotency_key VARCHAR(100) NOT NULL,
  customer_id VARCHAR(64) NOT NULL REFERENCES customer(customer_id),
  account_type VARCHAR(32) NOT NULL,
  currency VARCHAR(3) NOT NULL,
  account_id VARCHAR(64) NOT NULL REFERENCES account(account_id),
  created_at TIMESTAMP WITH TIME ZONE NOT NULL,
  CONSTRAINT uq_account_opening_opening_id UNIQUE(opening_id),
  CONSTRAINT uq_account_opening_idempotency_key UNIQUE(idempotency_key)
);
