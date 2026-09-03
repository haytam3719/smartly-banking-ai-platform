package com.smartly.banking.mobilebff.auth;
import com.smartly.banking.mobilebff.api.ApiModels.ChatRequest;
import org.springframework.http.HttpHeaders;
import reactor.core.publisher.Mono;
public interface AuthenticationPort{Mono<MobilePrincipal> authenticate(HttpHeaders headers,ChatRequest request);}
