package com.smartly.banking.corebanking.domain;

import jakarta.persistence.*;
import java.time.OffsetDateTime;

@Entity
@Table(name="account_opening", uniqueConstraints={@UniqueConstraint(name="uq_account_opening_opening_id",columnNames="opening_id"),@UniqueConstraint(name="uq_account_opening_idempotency_key",columnNames="idempotency_key")})
public class AccountOpening {
    @Id @Column(name="opening_record_id",length=36) private String openingRecordId;
    @Column(name="opening_id",nullable=false,length=100) private String openingId;
    @Column(name="idempotency_key",nullable=false,length=100) private String idempotencyKey;
    @Column(name="customer_id",nullable=false,length=64) private String customerId;
    @Enumerated(EnumType.STRING) @Column(name="account_type",nullable=false,length=32) private AccountType accountType;
    @Column(nullable=false,length=3) private String currency;
    @Column(name="account_id",nullable=false,length=64) private String accountId;
    @Column(name="created_at",nullable=false) private OffsetDateTime createdAt;
    protected AccountOpening() {}
    public AccountOpening(String openingRecordId,String openingId,String idempotencyKey,String customerId,AccountType accountType,String currency,String accountId,OffsetDateTime createdAt){this.openingRecordId=openingRecordId;this.openingId=openingId;this.idempotencyKey=idempotencyKey;this.customerId=customerId;this.accountType=accountType;this.currency=currency;this.accountId=accountId;this.createdAt=createdAt;}
    public String getOpeningId(){return openingId;} public String getIdempotencyKey(){return idempotencyKey;} public String getCustomerId(){return customerId;} public AccountType getAccountType(){return accountType;} public String getCurrency(){return currency;} public String getAccountId(){return accountId;}
}
