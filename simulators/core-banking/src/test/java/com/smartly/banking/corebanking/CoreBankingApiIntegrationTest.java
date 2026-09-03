package com.smartly.banking.corebanking;

import org.junit.jupiter.api.*;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.test.web.servlet.MockMvc;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@SpringBootTest @AutoConfigureMockMvc @ActiveProfiles("test")
class CoreBankingApiIntegrationTest {
    @Autowired MockMvc mvc;
    @Test void seededRejectedTransferIsAvailableToOwner()throws Exception{
        mvc.perform(get("/internal/v1/customers/C1024/transfers/TR4587"))
            .andExpect(status().isOk()).andExpect(jsonPath("$.status").value("REJECTED")).andExpect(jsonPath("$.rejection_reason").value("PAYMENT_LIMIT_EXCEEDED"));
    }
    @Test void crossCustomerCannotDiscoverTransfer()throws Exception{
        mvc.perform(get("/internal/v1/customers/C2048/transfers/TR4587"))
            .andExpect(status().isNotFound()).andExpect(jsonPath("$.code").value("TRANSFER_NOT_FOUND"));
    }
    @Test void unknownCustomerAndTransferReturnNotFound()throws Exception{
        mvc.perform(get("/internal/v1/customers/UNKNOWN")).andExpect(status().isNotFound()).andExpect(jsonPath("$.code").value("CUSTOMER_NOT_FOUND"));
        mvc.perform(get("/internal/v1/customers/C1024/transfers/UNKNOWN")).andExpect(status().isNotFound()).andExpect(jsonPath("$.code").value("TRANSFER_NOT_FOUND"));
    }
    @Test void filtersTransactionsByInclusiveDates()throws Exception{
        mvc.perform(get("/internal/v1/customers/C1024/transactions").param("start_date","2026-08-01").param("end_date","2026-08-03").param("limit","10"))
            .andExpect(status().isOk()).andExpect(jsonPath("$.transactions.length()").value(2)).andExpect(jsonPath("$.transactions[0].transaction_id").value("TX1004")).andExpect(jsonPath("$.transactions[1].transaction_id").value("TX1002"));
    }
    @Test void provisionsAndSafelyReplaysAccount()throws Exception{
        String body="{\"account_type\":\"CHECKING\",\"currency\":\"EUR\",\"opening_id\":\"OPEN-TEST-1\",\"idempotency_key\":\"IDEM-TEST-1\"}";
        String first=mvc.perform(post("/internal/v1/customers/C1024/accounts").contentType(MediaType.APPLICATION_JSON).content(body)).andExpect(status().isCreated()).andExpect(jsonPath("$.customer_id").value("C1024")).andReturn().getResponse().getContentAsString();
        mvc.perform(post("/internal/v1/customers/C1024/accounts").contentType(MediaType.APPLICATION_JSON).content(body)).andExpect(status().isCreated()).andExpect(content().json(first));
    }
    @Test void conflictingIdempotencyKeyIsRejected()throws Exception{
        String first="{\"account_type\":\"SAVINGS\",\"currency\":\"EUR\",\"opening_id\":\"OPEN-TEST-2\",\"idempotency_key\":\"IDEM-CONFLICT\"}";
        String conflict="{\"account_type\":\"CHECKING\",\"currency\":\"USD\",\"opening_id\":\"OPEN-TEST-3\",\"idempotency_key\":\"IDEM-CONFLICT\"}";
        mvc.perform(post("/internal/v1/customers/C1024/accounts").contentType(MediaType.APPLICATION_JSON).content(first)).andExpect(status().isCreated());
        mvc.perform(post("/internal/v1/customers/C1024/accounts").contentType(MediaType.APPLICATION_JSON).content(conflict)).andExpect(status().isConflict()).andExpect(jsonPath("$.code").value("IDEMPOTENCY_KEY_CONFLICT"));
    }
    @Test void unsupportedTypeAndCurrencyAreRejected()throws Exception{
        mvc.perform(post("/internal/v1/customers/C1024/accounts").contentType(MediaType.APPLICATION_JSON).content("{\"account_type\":\"LOAN\",\"currency\":\"EUR\",\"opening_id\":\"O4\",\"idempotency_key\":\"K4\"}")).andExpect(status().isBadRequest());
        mvc.perform(post("/internal/v1/customers/C1024/accounts").contentType(MediaType.APPLICATION_JSON).content("{\"account_type\":\"CHECKING\",\"currency\":\"JPY\",\"opening_id\":\"O5\",\"idempotency_key\":\"K5\"}")).andExpect(status().isUnprocessableEntity()).andExpect(jsonPath("$.code").value("UNSUPPORTED_CURRENCY"));
    }
}
