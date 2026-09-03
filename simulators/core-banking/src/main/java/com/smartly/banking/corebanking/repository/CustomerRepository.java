package com.smartly.banking.corebanking.repository;
import com.smartly.banking.corebanking.domain.Customer;
import org.springframework.data.jpa.repository.JpaRepository;
public interface CustomerRepository extends JpaRepository<Customer,String> {}
