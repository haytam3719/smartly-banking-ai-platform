package com.smartly.banking.corebanking.api;

import com.smartly.banking.corebanking.service.*;
import com.smartly.banking.corebanking.security.InternalAuthenticator;
import io.micrometer.core.instrument.MeterRegistry;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.http.HttpStatus;
import org.springframework.test.web.servlet.MockMvc;
import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@WebMvcTest(controllers=CoreBankingController.class)
@AutoConfigureMockMvc(addFilters=false)
class CoreBankingControllerTest {
    @Autowired MockMvc mvc; @MockBean CoreBankingService service; @MockBean InternalAuthenticator authenticator; @MockBean MeterRegistry meterRegistry;
    @Test void mapsUnknownCustomerToCanonicalSafeError()throws Exception{
        when(service.customer("UNKNOWN")).thenThrow(new DomainException("CUSTOMER_NOT_FOUND","Customer not found",HttpStatus.NOT_FOUND));
        mvc.perform(get("/internal/v1/customers/UNKNOWN").header("X-Request-Id","req-test"))
            .andExpect(status().isNotFound()).andExpect(jsonPath("$.code").value("CUSTOMER_NOT_FOUND")).andExpect(jsonPath("$.message").value("Customer not found"));
    }
    @Test void validatesTransactionLimit()throws Exception{
        mvc.perform(get("/internal/v1/customers/C1024/transactions").param("limit","0"))
            .andExpect(status().isBadRequest()).andExpect(jsonPath("$.code").value("VALIDATION_ERROR"));
    }
}
