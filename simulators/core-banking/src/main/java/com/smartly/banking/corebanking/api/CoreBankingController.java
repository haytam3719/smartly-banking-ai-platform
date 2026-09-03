package com.smartly.banking.corebanking.api;

import com.smartly.banking.corebanking.api.ApiModels.*;
import com.smartly.banking.corebanking.service.CoreBankingService;
import jakarta.validation.Valid;
import jakarta.validation.constraints.Max;
import jakarta.validation.constraints.Min;
import org.springframework.format.annotation.DateTimeFormat;
import org.springframework.http.*;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.*;
import java.time.LocalDate;

@RestController @Validated
@RequestMapping("/internal/v1/customers/{customerId}")
public class CoreBankingController {
    private final CoreBankingService service;
    public CoreBankingController(CoreBankingService service){this.service=service;}
    @GetMapping public CustomerResponse customer(@PathVariable String customerId){return service.customer(customerId);}
    @GetMapping("/accounts/balance") public BalanceResponse balances(@PathVariable String customerId){return service.balances(customerId);}
    @GetMapping("/transactions") public TransactionsResponse transactions(@PathVariable String customerId,
        @RequestParam(name="start_date",required=false) @DateTimeFormat(iso=DateTimeFormat.ISO.DATE) LocalDate start,
        @RequestParam(name="end_date",required=false) @DateTimeFormat(iso=DateTimeFormat.ISO.DATE) LocalDate end,
        @RequestParam(defaultValue="50") @Min(1) @Max(200) int limit){return service.transactions(customerId,start,end,limit);}
    @GetMapping("/cards/primary") public CardResponse primaryCard(@PathVariable String customerId){return service.primaryCard(customerId);}
    @GetMapping("/transfers/{transferId}") public TransferResponse transfer(@PathVariable String customerId,@PathVariable String transferId){return service.transfer(customerId,transferId);}
    @PostMapping("/accounts") public ResponseEntity<AccountResponse> createAccount(@PathVariable String customerId,@Valid @RequestBody CreateAccountRequest request){return ResponseEntity.status(HttpStatus.CREATED).body(service.createAccount(customerId,request));}
}
