package com.smartly.banking.corebanking.repository;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.orm.jpa.DataJpaTest;
import org.springframework.data.domain.PageRequest;
import org.springframework.test.context.ActiveProfiles;
import java.time.*;
import java.util.List;
import static org.assertj.core.api.Assertions.assertThat;

@DataJpaTest
@ActiveProfiles("test")
class RepositoryTests {
    @Autowired CustomerRepository customers;
    @Autowired AccountRepository accounts;
    @Autowired TransactionRepository transactions;
    @Autowired TransferRepository transfers;

    @Test void loadsSeededAggregateAndScopedTransfer(){
        assertThat(customers.findById("C1024")).isPresent();
        assertThat(accounts.findByCustomerIdOrderByAccountId("C1024")).hasSize(2);
        assertThat(transfers.findByTransferIdAndCustomerId("TR4587","C1024")).isPresent();
        assertThat(transfers.findByTransferIdAndCustomerId("TR4587","C2048")).isEmpty();
    }
    @Test void filtersTransactionsByAccountAndDate(){
        var found=transactions.findByAccountIdInAndOccurredAtBetweenOrderByOccurredAtDesc(List.of("ACC-C1024-EUR"),OffsetDateTime.parse("2026-08-01T00:00:00Z"),OffsetDateTime.parse("2026-08-31T23:59:59Z"),PageRequest.of(0,20));
        assertThat(found).extracting("transactionId").containsExactly("TX1001","TX1002");
    }
}
