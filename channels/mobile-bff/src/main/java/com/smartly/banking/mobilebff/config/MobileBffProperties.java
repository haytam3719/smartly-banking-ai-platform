package com.smartly.banking.mobilebff.config;
import java.time.Duration;
import org.springframework.boot.context.properties.ConfigurationProperties;
@ConfigurationProperties("mobile-bff")
public record MobileBffProperties(Authentication authentication,Orchestrator orchestrator){
 public record Authentication(boolean demoMode){}
 public record Orchestrator(String baseUrl,Duration connectTimeout,Duration readTimeout,int retryAttempts){}
}
