package com.smartly.banking.mobilebff.orchestrator;
import com.smartly.banking.mobilebff.api.ApiModels.ChatResponse;
import com.smartly.banking.mobilebff.api.ApiModels.OrchestratorChatRequest;
import com.smartly.banking.mobilebff.auth.MobilePrincipal;
import reactor.core.publisher.Mono;
public interface OrchestratorClient{Mono<ChatResponse> chat(OrchestratorChatRequest request,MobilePrincipal principal,MobileRequestContext context);}
