package com.smartly.banking.corebanking.repository;
import com.smartly.banking.corebanking.domain.Transfer;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.Optional;
public interface TransferRepository extends JpaRepository<Transfer,String> { Optional<Transfer> findByTransferIdAndCustomerId(String transferId,String customerId); }
