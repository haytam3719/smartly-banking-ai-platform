package com.smartly.banking.corebanking.service;

import com.smartly.banking.corebanking.api.ApiModels;
import com.smartly.banking.corebanking.api.ApiModels.*;
import com.smartly.banking.corebanking.domain.*;
import com.smartly.banking.corebanking.repository.*;
import io.micrometer.core.instrument.MeterRegistry;
import org.springframework.data.domain.PageRequest;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import java.math.BigDecimal;
import java.nio.charset.StandardCharsets;
import java.time.*;
import java.util.*;

@Service
@Transactional(readOnly=true)
public class CoreBankingService {
    private static final Set<String> SUPPORTED_CURRENCIES=Set.of("EUR","USD","GBP");
    private final CustomerRepository customers; private final AccountRepository accounts; private final TransactionRepository transactions;
    private final CardRepository cards; private final TransferRepository transfers; private final AccountOpeningRepository openings; private final MeterRegistry meters;
    public CoreBankingService(CustomerRepository customers,AccountRepository accounts,TransactionRepository transactions,CardRepository cards,TransferRepository transfers,AccountOpeningRepository openings,MeterRegistry meters){this.customers=customers;this.accounts=accounts;this.transactions=transactions;this.cards=cards;this.transfers=transfers;this.openings=openings;this.meters=meters;}

    public CustomerResponse customer(String id){return ApiModels.from(requireCustomer(id));}
    public BalanceResponse balances(String id){requireCustomer(id);return new BalanceResponse(id,accounts.findByCustomerIdOrderByAccountId(id).stream().map(ApiModels::from).toList());}
    public TransactionsResponse transactions(String id,LocalDate start,LocalDate end,int limit){
        requireCustomer(id);
        if(start!=null&&end!=null&&start.isAfter(end))throw new DomainException("INVALID_DATE_RANGE","start_date must not be after end_date",HttpStatus.BAD_REQUEST);
        LocalDate effectiveStart=start==null?LocalDate.of(1970,1,1):start; LocalDate effectiveEnd=end==null?LocalDate.of(9999,12,31):end;
        var ids=accounts.findByCustomerIdOrderByAccountId(id).stream().map(Account::getAccountId).toList();
        var result=ids.isEmpty()?List.<BankTransaction>of():transactions.findByAccountIdInAndOccurredAtBetweenOrderByOccurredAtDesc(ids,effectiveStart.atStartOfDay().atOffset(ZoneOffset.UTC),effectiveEnd.plusDays(1).atStartOfDay().atOffset(ZoneOffset.UTC).minusNanos(1),PageRequest.of(0,limit));
        return new TransactionsResponse(id,start,end,limit,result.stream().map(ApiModels::from).toList());
    }
    public CardResponse primaryCard(String id){requireCustomer(id);return cards.findFirstByCustomerIdAndStatusOrderByExpirationDateDesc(id,CardStatus.ACTIVE).map(ApiModels::from).orElseThrow(()->notFound("CARD_NOT_FOUND","Primary card not found"));}
    public TransferResponse transfer(String customerId,String transferId){requireCustomer(customerId);return transfers.findByTransferIdAndCustomerId(transferId,customerId).map(ApiModels::from).orElseThrow(()->notFound("TRANSFER_NOT_FOUND","Transfer not found"));}

    @Transactional
    public AccountResponse createAccount(String customerId,CreateAccountRequest request){
        requireCustomer(customerId);
        if(!SUPPORTED_CURRENCIES.contains(request.currency()))throw new DomainException("UNSUPPORTED_CURRENCY","Unsupported account currency",HttpStatus.UNPROCESSABLE_ENTITY);
        var existingByKey=openings.findByIdempotencyKey(request.idempotencyKey());
        if(existingByKey.isPresent())return replayOrConflict(existingByKey.get(),customerId,request);
        var existingByOpening=openings.findByOpeningId(request.openingId());
        if(existingByOpening.isPresent())return replayOrConflict(existingByOpening.get(),customerId,request);
        String accountId="ACC-"+UUID.nameUUIDFromBytes((request.openingId()+":"+request.idempotencyKey()).getBytes(StandardCharsets.UTF_8)).toString().substring(0,12).toUpperCase(Locale.ROOT);
        Account account=accounts.save(new Account(accountId,customerId,request.accountType(),request.currency(),BigDecimal.ZERO.setScale(2),AccountStatus.ACTIVE));
        openings.save(new AccountOpening(UUID.randomUUID().toString(),request.openingId(),request.idempotencyKey(),customerId,request.accountType(),request.currency(),accountId,OffsetDateTime.now(ZoneOffset.UTC)));
        meters.counter("core_banking.accounts.provisioned","account_type",request.accountType().name(),"currency",request.currency()).increment();
        return ApiModels.from(account);
    }
    private AccountResponse replayOrConflict(AccountOpening x,String customerId,CreateAccountRequest r){
        boolean same=x.getCustomerId().equals(customerId)&&x.getOpeningId().equals(r.openingId())&&x.getIdempotencyKey().equals(r.idempotencyKey())&&x.getAccountType()==r.accountType()&&x.getCurrency().equals(r.currency());
        if(!same)throw new DomainException("IDEMPOTENCY_KEY_CONFLICT","Idempotency key or opening ID was already used for different parameters",HttpStatus.CONFLICT);
        meters.counter("core_banking.accounts.provisioning_replays").increment();
        return accounts.findById(x.getAccountId()).map(ApiModels::from).orElseThrow(()->new IllegalStateException("Provisioned account record is inconsistent"));
    }
    private Customer requireCustomer(String id){return customers.findById(id).orElseThrow(()->notFound("CUSTOMER_NOT_FOUND","Customer not found"));}
    private DomainException notFound(String code,String message){return new DomainException(code,message,HttpStatus.NOT_FOUND);}
}
