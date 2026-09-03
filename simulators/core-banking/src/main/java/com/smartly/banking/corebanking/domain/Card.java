package com.smartly.banking.corebanking.domain;

import jakarta.persistence.*;
import java.math.BigDecimal;
import java.time.LocalDate;

@Entity
@Table(name="payment_card")
public class Card {
    @Id @Column(name="card_id",length=64) private String cardId;
    @Column(name="customer_id",nullable=false,length=64) private String customerId;
    @Enumerated(EnumType.STRING) @Column(nullable=false,length=32) private CardType type;
    @Enumerated(EnumType.STRING) @Column(nullable=false,length=32) private CardStatus status;
    @Column(name="expiration_date",nullable=false) private LocalDate expirationDate;
    @Column(name="payment_limit",nullable=false,precision=19,scale=2) private BigDecimal paymentLimit;
    @Column(name="amount_used",nullable=false,precision=19,scale=2) private BigDecimal amountUsed;
    @Column(nullable=false,length=3) private String currency;
    protected Card() {}
    public String getCardId(){return cardId;} public String getCustomerId(){return customerId;} public CardType getType(){return type;} public CardStatus getStatus(){return status;} public LocalDate getExpirationDate(){return expirationDate;} public BigDecimal getPaymentLimit(){return paymentLimit;} public BigDecimal getAmountUsed(){return amountUsed;} public String getCurrency(){return currency;}
}
