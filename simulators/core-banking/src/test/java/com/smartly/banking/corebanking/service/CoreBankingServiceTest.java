package com.smartly.banking.corebanking.service;

import com.smartly.banking.corebanking.api.ApiModels.CreateAccountRequest;
import com.smartly.banking.corebanking.domain.*;
import com.smartly.banking.corebanking.repository.*;
import io.micrometer.core.instrument.simple.SimpleMeterRegistry;
import org.junit.jupiter.api.*;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import java.util.Optional;
import static org.assertj.core.api.Assertions.*;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class CoreBankingServiceTest {
    @Mock CustomerRepository customers; @Mock AccountRepository accounts; @Mock TransactionRepository transactions;
    @Mock CardRepository cards; @Mock TransferRepository transfers; @Mock AccountOpeningRepository openings;
    CoreBankingService service;
    @BeforeEach void setUp(){service=new CoreBankingService(customers,accounts,transactions,cards,transfers,openings,new SimpleMeterRegistry());}

    @Test void unknownCustomerIsSafeNotFound(){
        when(customers.findById("missing")).thenReturn(Optional.empty());
        assertThatThrownBy(()->service.customer("missing")).isInstanceOf(DomainException.class).extracting("code").isEqualTo("CUSTOMER_NOT_FOUND");
    }
    @Test void crossCustomerTransferLooksUnknown(){
        when(customers.findById("C2048")).thenReturn(Optional.of(new Customer("C2048","A","B",CustomerSegment.STANDARD,KycStatus.VERIFIED,"FR")));
        when(transfers.findByTransferIdAndCustomerId("TR4587","C2048")).thenReturn(Optional.empty());
        assertThatThrownBy(()->service.transfer("C2048","TR4587")).isInstanceOf(DomainException.class).extracting("code").isEqualTo("TRANSFER_NOT_FOUND");
        verify(transfers,never()).findById(anyString());
    }
    @Test void unsupportedCurrencyIsRejectedBeforeWrite(){
        when(customers.findById("C1024")).thenReturn(Optional.of(new Customer("C1024","A","B",CustomerSegment.STANDARD,KycStatus.VERIFIED,"FR")));
        assertThatThrownBy(()->service.createAccount("C1024",new CreateAccountRequest(AccountType.CHECKING,"JPY","O1","K1"))).isInstanceOf(DomainException.class).extracting("code").isEqualTo("UNSUPPORTED_CURRENCY");
        verify(accounts,never()).save(any());
    }
}
