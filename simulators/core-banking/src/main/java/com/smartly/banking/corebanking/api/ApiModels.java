package com.smartly.banking.corebanking.api;

import com.smartly.banking.corebanking.domain.*;
import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.annotation.JsonProperty;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Pattern;
import jakarta.validation.constraints.Size;
import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.OffsetDateTime;
import java.util.List;

public final class ApiModels {
    private ApiModels() {}
    public record CustomerResponse(@JsonProperty("customer_id") String customerId,@JsonProperty("first_name") String firstName,@JsonProperty("last_name") String lastName,CustomerSegment segment,@JsonProperty("kyc_status") KycStatus kycStatus,String country) {}
    public record AccountResponse(@JsonProperty("account_id") String accountId,@JsonProperty("customer_id") String customerId,AccountType type,String currency,@JsonProperty("available_balance") BigDecimal availableBalance,AccountStatus status) {}
    public record BalanceResponse(@JsonProperty("customer_id") String customerId,List<AccountResponse> accounts) {}
    public record TransactionResponse(@JsonProperty("transaction_id") String transactionId,@JsonProperty("account_id") String accountId,TransactionType type,BigDecimal amount,String currency,String merchant,String description,@JsonProperty("occurred_at") OffsetDateTime occurredAt,TransactionStatus status) {}
    public record TransactionsResponse(@JsonProperty("customer_id") String customerId,@JsonProperty("start_date") LocalDate startDate,@JsonProperty("end_date") LocalDate endDate,int limit,List<TransactionResponse> transactions) {}
    public record CardResponse(@JsonProperty("card_id") String cardId,@JsonProperty("customer_id") String customerId,CardType type,CardStatus status,@JsonProperty("expiration_date") LocalDate expirationDate,@JsonProperty("payment_limit") BigDecimal paymentLimit,@JsonProperty("amount_used") BigDecimal amountUsed,String currency) {}
    @JsonInclude(JsonInclude.Include.ALWAYS)
    public record TransferResponse(@JsonProperty("transfer_id") String transferId,@JsonProperty("customer_id") String customerId,String beneficiary,BigDecimal amount,String currency,@JsonProperty("created_at") OffsetDateTime createdAt,TransferStatus status,@JsonProperty("rejection_reason") String rejectionReason) {}
    public record CreateAccountRequest(
        @NotNull @JsonProperty("account_type") AccountType accountType,
        @NotBlank @Pattern(regexp="^[A-Z]{3}$") String currency,
        @NotBlank @Size(max=100) @JsonProperty("opening_id") String openingId,
        @NotBlank @Size(max=100) @JsonProperty("idempotency_key") String idempotencyKey) {}
    public record ErrorResponse(String code,String message,@JsonProperty("request_id") String requestId,boolean retryable) {}

    public static CustomerResponse from(Customer x){return new CustomerResponse(x.getCustomerId(),x.getFirstName(),x.getLastName(),x.getSegment(),x.getKycStatus(),x.getCountry());}
    public static AccountResponse from(Account x){return new AccountResponse(x.getAccountId(),x.getCustomerId(),x.getType(),x.getCurrency(),x.getAvailableBalance(),x.getStatus());}
    public static TransactionResponse from(BankTransaction x){return new TransactionResponse(x.getTransactionId(),x.getAccountId(),x.getType(),x.getAmount(),x.getCurrency(),x.getMerchant(),x.getDescription(),x.getOccurredAt(),x.getStatus());}
    public static CardResponse from(Card x){return new CardResponse(x.getCardId(),x.getCustomerId(),x.getType(),x.getStatus(),x.getExpirationDate(),x.getPaymentLimit(),x.getAmountUsed(),x.getCurrency());}
    public static TransferResponse from(Transfer x){return new TransferResponse(x.getTransferId(),x.getCustomerId(),x.getBeneficiary(),x.getAmount(),x.getCurrency(),x.getCreatedAt(),x.getStatus(),x.getRejectionReason());}
}
