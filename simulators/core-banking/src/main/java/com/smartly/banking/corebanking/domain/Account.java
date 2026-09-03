package com.smartly.banking.corebanking.domain;

import jakarta.persistence.*;
import java.math.BigDecimal;

@Entity
@Table(name = "account")
public class Account {
    @Id @Column(name="account_id", length=64) private String accountId;
    @Column(name="customer_id", nullable=false, length=64) private String customerId;
    @Enumerated(EnumType.STRING) @Column(nullable=false, length=32) private AccountType type;
    @Column(nullable=false, length=3) private String currency;
    @Column(name="available_balance", nullable=false, precision=19, scale=2) private BigDecimal availableBalance;
    @Enumerated(EnumType.STRING) @Column(nullable=false, length=32) private AccountStatus status;
    protected Account() {}
    public Account(String accountId,String customerId,AccountType type,String currency,BigDecimal availableBalance,AccountStatus status){this.accountId=accountId;this.customerId=customerId;this.type=type;this.currency=currency;this.availableBalance=availableBalance;this.status=status;}
    public String getAccountId(){return accountId;} public String getCustomerId(){return customerId;} public AccountType getType(){return type;}
    public String getCurrency(){return currency;} public BigDecimal getAvailableBalance(){return availableBalance;} public AccountStatus getStatus(){return status;}
}
