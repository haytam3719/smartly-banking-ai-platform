package com.smartly.banking.corebanking;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.DynamicPropertyRegistry;
import org.springframework.test.context.DynamicPropertySource;
import org.testcontainers.containers.PostgreSQLContainer;
import org.testcontainers.junit.jupiter.Container;
import org.testcontainers.junit.jupiter.Testcontainers;
import com.smartly.banking.corebanking.repository.*;
import static org.assertj.core.api.Assertions.assertThat;

@Testcontainers(disabledWithoutDocker=true)
@SpringBootTest(properties="internal-auth.dev-mode=true")
class PostgresContainerIntegrationTest {
    @Container static PostgreSQLContainer<?> postgres=new PostgreSQLContainer<>("postgres:16-alpine");
    @DynamicPropertySource static void database(DynamicPropertyRegistry r){r.add("spring.datasource.url",postgres::getJdbcUrl);r.add("spring.datasource.username",postgres::getUsername);r.add("spring.datasource.password",postgres::getPassword);}
    @Autowired CustomerRepository customers; @Autowired TransferRepository transfers;
    @Test void flywaySeedsPostgresAndOwnershipQueryWorks(){assertThat(customers.findById("C1024")).isPresent();assertThat(transfers.findByTransferIdAndCustomerId("TR4587","C1024")).isPresent();assertThat(transfers.findByTransferIdAndCustomerId("TR4587","C2048")).isEmpty();}
}
