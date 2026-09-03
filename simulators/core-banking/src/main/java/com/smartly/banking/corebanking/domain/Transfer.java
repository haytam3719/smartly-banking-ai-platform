package com.smartly.banking.corebanking.domain;

import jakarta.persistence.*;
import java.math.BigDecimal;
import java.time.OffsetDateTime;

@Entity
@Table(name="bank_transfer")
public class Transfer {
    @Id @Column(name="transfer_id",length=64) private String transferId;
    @Column(name="customer_id",nullable=false,length=64) private String customerId;
    @Column(nullable=false,length=160) private String beneficiary;
    @Column(nullable=false,precision=19,scale=2) private BigDecimal amount;
    @Column(nullable=false,length=3) private String currency;
    @Column(name="created_at",nullable=false) private OffsetDateTime createdAt;
    @Enumerated(EnumType.STRING) @Column(nullable=false,length=32) private TransferStatus status;
    @Column(name="rejection_reason",length=64) private String rejectionReason;
    protected Transfer() {}
    public String getTransferId(){return transferId;} public String getCustomerId(){return customerId;} public String getBeneficiary(){return beneficiary;} public BigDecimal getAmount(){return amount;} public String getCurrency(){return currency;} public OffsetDateTime getCreatedAt(){return createdAt;} public TransferStatus getStatus(){return status;} public String getRejectionReason(){return rejectionReason;}
}
