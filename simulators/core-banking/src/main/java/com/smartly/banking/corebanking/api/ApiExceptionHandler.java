package com.smartly.banking.corebanking.api;

import com.smartly.banking.corebanking.api.ApiModels.ErrorResponse;
import com.smartly.banking.corebanking.service.DomainException;
import jakarta.validation.ConstraintViolationException;
import org.slf4j.*;
import org.springframework.http.*;
import org.springframework.http.converter.HttpMessageNotReadableException;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.method.annotation.MethodArgumentTypeMismatchException;

@RestControllerAdvice
public class ApiExceptionHandler {
    private static final Logger log=LoggerFactory.getLogger(ApiExceptionHandler.class);
    @ExceptionHandler(DomainException.class) ResponseEntity<ErrorResponse> domain(DomainException e){return ResponseEntity.status(e.status()).body(error(e.code(),e.getMessage(),false));}
    @ExceptionHandler({MethodArgumentNotValidException.class,ConstraintViolationException.class,MethodArgumentTypeMismatchException.class,HttpMessageNotReadableException.class}) ResponseEntity<ErrorResponse> invalid(Exception e){return ResponseEntity.badRequest().body(error("VALIDATION_ERROR","Request validation failed",false));}
    @ExceptionHandler(Exception.class) ResponseEntity<ErrorResponse> unexpected(Exception e){log.error("Unhandled request failure: {}",e.getClass().getSimpleName());return ResponseEntity.status(500).body(error("INTERNAL_ERROR","An internal error occurred",true));}
    private ErrorResponse error(String code,String message,boolean retryable){return new ErrorResponse(code,message,MDC.get("request_id"),retryable);}
}
