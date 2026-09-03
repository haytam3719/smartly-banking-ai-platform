package com.smartly.banking.corebanking.repository;
import com.smartly.banking.corebanking.domain.Card;
import com.smartly.banking.corebanking.domain.CardStatus;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.Optional;
public interface CardRepository extends JpaRepository<Card,String> { Optional<Card> findFirstByCustomerIdAndStatusOrderByExpirationDateDesc(String customerId, CardStatus status); }
