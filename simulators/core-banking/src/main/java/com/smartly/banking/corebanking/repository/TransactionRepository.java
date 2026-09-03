package com.smartly.banking.corebanking.repository;
import com.smartly.banking.corebanking.domain.BankTransaction;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import java.time.OffsetDateTime;
import java.util.List;
public interface TransactionRepository extends JpaRepository<BankTransaction,String> {
    List<BankTransaction> findByAccountIdInAndOccurredAtBetweenOrderByOccurredAtDesc(List<String> accountIds, OffsetDateTime start, OffsetDateTime end, Pageable pageable);
}
