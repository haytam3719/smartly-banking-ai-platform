package com.smartly.banking.corebanking.repository;
import com.smartly.banking.corebanking.domain.AccountOpening;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.Optional;
public interface AccountOpeningRepository extends JpaRepository<AccountOpening,String> {
    Optional<AccountOpening> findByIdempotencyKey(String idempotencyKey);
    Optional<AccountOpening> findByOpeningId(String openingId);
}
