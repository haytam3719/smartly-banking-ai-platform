package com.smartly.banking.corebanking.repository;
import com.smartly.banking.corebanking.domain.Account;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;
public interface AccountRepository extends JpaRepository<Account,String> { List<Account> findByCustomerIdOrderByAccountId(String customerId); }
