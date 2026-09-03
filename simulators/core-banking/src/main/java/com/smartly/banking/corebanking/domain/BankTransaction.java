package com.smartly.banking.corebanking.domain;

import jakarta.persistence.*;
import java.math.BigDecimal;
import java.time.OffsetDateTime;

@Entity
@Table(name="bank_transaction")
public class BankTransaction {
    @Id @Column(name="transaction_id",length=64) private String transactionId;
    @Column(name="account_id",nullable=false,length=64) private String accountId;
    @Enumerated(EnumType.STRING) @Column(nullable=false,length=32) private TransactionType type;
    @Column(nullable=false,precision=19,scale=2) private BigDecimal amount;
    @Column(nullable=false,length=3) private String currency;
    @Column(length=160) private String merchant;
    @Column(length=500) private String description;
    @Column(name="occurred_at",nullable=false) private OffsetDateTime occurredAt;
    @Enumerated(EnumType.STRING) @Column(nullable=false,length=32) private TransactionStatus status;
    protected BankTransaction() {}
    public BankTransaction(String transactionId,String accountId,TransactionType type,BigDecimal amount,String currency,String merchant,String description,OffsetDateTime occurredAt,TransactionStatus status){this.transactionId=transactionId;this.accountId=accountId;this.type=type;this.amount=amount;this.currency=currency;this.merchant=merchant;this.description=description;this.occurredAt=occurredAt;this.status=status;}
    public String getTransactionId(){return transactionId;} public String getAccountId(){return accountId;} public TransactionType getType(){return type;} public BigDecimal getAmount(){return amount;} public String getCurrency(){return currency;} public String getMerchant(){return merchant;} public String getDescription(){return description;} public OffsetDateTime getOccurredAt(){return occurredAt;} public TransactionStatus getStatus(){return status;}
}
