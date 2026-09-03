package com.smartly.banking.mobilebff.config;
import io.netty.channel.ChannelOption;
import io.github.resilience4j.retry.Retry;
import io.github.resilience4j.retry.RetryConfig;
import java.util.concurrent.TimeoutException;
import org.springframework.boot.context.properties.EnableConfigurationProperties;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.http.client.reactive.ReactorClientHttpConnector;
import org.springframework.web.reactive.function.client.WebClient;
import reactor.netty.http.client.HttpClient;
@Configuration @EnableConfigurationProperties(MobileBffProperties.class)
class ClientConfiguration{
 @Bean WebClient orchestratorWebClient(WebClient.Builder builder,MobileBffProperties properties){var p=properties.orchestrator();var http=HttpClient.create().option(ChannelOption.CONNECT_TIMEOUT_MILLIS,Math.toIntExact(p.connectTimeout().toMillis())).responseTimeout(p.readTimeout());return builder.baseUrl(p.baseUrl()).clientConnector(new ReactorClientHttpConnector(http)).build();}
 @Bean Retry orchestratorRetry(MobileBffProperties properties){return Retry.of("orchestrator-chat",RetryConfig.custom().maxAttempts(properties.orchestrator().retryAttempts()).waitDuration(java.time.Duration.ofMillis(30)).retryExceptions(com.smartly.banking.mobilebff.orchestrator.RetryableOrchestratorException.class,TimeoutException.class).build());}
}
