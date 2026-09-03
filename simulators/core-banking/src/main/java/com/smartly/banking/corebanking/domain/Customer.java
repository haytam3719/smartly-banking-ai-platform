package com.smartly.banking.corebanking.domain;

import jakarta.persistence.*;

@Entity
@Table(name = "customer")
public class Customer {
    @Id @Column(name = "customer_id", length = 64) private String customerId;
    @Column(name = "first_name", nullable = false, length = 100) private String firstName;
    @Column(name = "last_name", nullable = false, length = 100) private String lastName;
    @Enumerated(EnumType.STRING) @Column(nullable = false, length = 32) private CustomerSegment segment;
    @Enumerated(EnumType.STRING) @Column(name = "kyc_status", nullable = false, length = 32) private KycStatus kycStatus;
    @Column(nullable = false, length = 2) private String country;
    protected Customer() {}
    public Customer(String customerId, String firstName, String lastName, CustomerSegment segment, KycStatus kycStatus, String country) {
        this.customerId=customerId; this.firstName=firstName; this.lastName=lastName; this.segment=segment; this.kycStatus=kycStatus; this.country=country;
    }
    public String getCustomerId(){return customerId;} public String getFirstName(){return firstName;} public String getLastName(){return lastName;}
    public CustomerSegment getSegment(){return segment;} public KycStatus getKycStatus(){return kycStatus;} public String getCountry(){return country;}
}
