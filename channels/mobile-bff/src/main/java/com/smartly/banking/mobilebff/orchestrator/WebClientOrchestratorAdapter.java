package com.smartly.banking.mobilebff.orchestrator;
import com.smartly.banking.mobilebff.api.ApiModels.ChatResponse;
import com.smartly.banking.mobilebff.api.ApiModels.OrchestratorChatRequest;
import com.smartly.banking.mobilebff.auth.MobilePrincipal;
import com.smartly.banking.mobilebff.config.MobileBffProperties;
import io.github.resilience4j.reactor.retry.RetryOperator;
import io.github.resilience4j.retry.Retry;
import java.util.concurrent.TimeoutException;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Component;
import org.springframework.web.reactive.function.client.WebClient;
import org.springframework.web.reactive.function.client.WebClientRequestException;
import reactor.core.publisher.Mono;
@Component
public class WebClientOrchestratorAdapter implements OrchestratorClient{
 private final WebClient client;private final Retry retry;private final MobileBffProperties properties;
 public WebClientOrchestratorAdapter(WebClient orchestratorWebClient,Retry orchestratorRetry,MobileBffProperties properties){this.client=orchestratorWebClient;this.retry=orchestratorRetry;this.properties=properties;}
 public Mono<ChatResponse> chat(OrchestratorChatRequest request,MobilePrincipal principal,MobileRequestContext context){
  return client.post().uri("/api/v1/chat").contentType(MediaType.APPLICATION_JSON).headers(h->{h.set("X-Channel","MOBILE");h.set("X-Authenticated-Subject-Id",principal.subjectId());h.set("X-Authenticated-Customer-Id",principal.customerId());h.set("X-Scopes",principal.scopes());h.set("X-Request-Id",context.requestId());h.set("X-Correlation-Id",context.correlationId());if(context.conversationId()!=null)h.set("X-Conversation-Id",context.conversationId());if(context.traceparent()!=null)h.set("traceparent",context.traceparent());if(context.appVersion()!=null)h.set("X-App-Version",context.appVersion());if(context.deviceClass()!=null)h.set("X-Device-Class",context.deviceClass());}).bodyValue(request).exchangeToMono(r->{if(r.statusCode().is2xxSuccessful())return r.bodyToMono(ChatResponse.class);if(r.statusCode().is5xxServerError())return Mono.error(new RetryableOrchestratorException("ORCHESTRATOR_ERROR"));return Mono.error(new OrchestratorException("ORCHESTRATOR_REQUEST_REJECTED",false));}).timeout(properties.orchestrator().readTimeout()).onErrorMap(WebClientRequestException.class,e->new RetryableOrchestratorException("ORCHESTRATOR_UNAVAILABLE")).transformDeferred(RetryOperator.of(retry)).onErrorMap(TimeoutException.class,e->new RetryableOrchestratorException("ORCHESTRATOR_TIMEOUT"));
 }
}
