package com.smartly.banking.mobilebff.orchestrator;
public record MobileRequestContext(String requestId,String correlationId,String conversationId,String traceparent,String appVersion,String deviceClass){}
