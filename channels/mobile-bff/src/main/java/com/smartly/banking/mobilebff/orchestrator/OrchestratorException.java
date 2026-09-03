package com.smartly.banking.mobilebff.orchestrator;
public class OrchestratorException extends RuntimeException{private final String code;private final boolean retryable;public OrchestratorException(String code,boolean retryable){super(code);this.code=code;this.retryable=retryable;}public String code(){return code;}public boolean retryable(){return retryable;}}
