package com.smartly.banking.mobilebff.api;
import com.smartly.banking.mobilebff.api.ApiModels.SafeError;
import com.smartly.banking.mobilebff.auth.AuthenticationException;
import com.smartly.banking.mobilebff.auth.HeaderAuthenticationAdapter.CustomerContextException;
import com.smartly.banking.mobilebff.orchestrator.OrchestratorException;
import java.util.UUID;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.support.WebExchangeBindException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;
import org.springframework.web.server.ServerWebExchange;
@RestControllerAdvice
public class ApiExceptionHandler{
 @ExceptionHandler(WebExchangeBindException.class) ResponseEntity<SafeError> validation(WebExchangeBindException e,ServerWebExchange x){return response(HttpStatus.BAD_REQUEST,"INVALID_REQUEST","Request validation failed",false,x);}
 @ExceptionHandler(AuthenticationException.class) ResponseEntity<SafeError> authentication(AuthenticationException e,ServerWebExchange x){return response(HttpStatus.UNAUTHORIZED,"AUTHENTICATION_REQUIRED","Authentication required",false,x);}
 @ExceptionHandler(CustomerContextException.class) ResponseEntity<SafeError> customer(CustomerContextException e,ServerWebExchange x){return response(HttpStatus.NOT_FOUND,"CUSTOMER_CONTEXT_NOT_FOUND","Customer context not found",false,x);}
 @ExceptionHandler(OrchestratorException.class) ResponseEntity<SafeError> downstream(OrchestratorException e,ServerWebExchange x){var status=e.code().equals("ORCHESTRATOR_TIMEOUT")?HttpStatus.GATEWAY_TIMEOUT:HttpStatus.BAD_GATEWAY;return response(status,e.code(),"The assistant is temporarily unavailable",e.retryable(),x);}
 @ExceptionHandler(Exception.class) ResponseEntity<SafeError> unknown(Exception e,ServerWebExchange x){return response(HttpStatus.INTERNAL_SERVER_ERROR,"INTERNAL_ERROR","The request could not be completed",false,x);}
 private ResponseEntity<SafeError> response(HttpStatus status,String code,String message,boolean retryable,ServerWebExchange exchange){Object value=exchange.getAttribute("request_id");String requestId=value instanceof String s?s:exchange.getRequest().getHeaders().getFirst("X-Request-Id");if(requestId==null||requestId.length()>128)requestId=UUID.randomUUID().toString();return ResponseEntity.status(status).body(new SafeError(code,message,requestId,retryable));}
}
