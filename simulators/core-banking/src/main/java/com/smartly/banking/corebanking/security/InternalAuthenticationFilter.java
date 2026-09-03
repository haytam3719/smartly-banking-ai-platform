package com.smartly.banking.corebanking.security;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.smartly.banking.corebanking.api.ApiModels.ErrorResponse;
import jakarta.servlet.*;
import jakarta.servlet.http.*;
import org.slf4j.MDC;
import org.springframework.core.Ordered;
import org.springframework.core.annotation.Order;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Component;
import org.springframework.web.filter.OncePerRequestFilter;
import java.io.IOException;

@Component @Order(Ordered.HIGHEST_PRECEDENCE+10)
public class InternalAuthenticationFilter extends OncePerRequestFilter {
    private final InternalAuthenticator authenticator; private final ObjectMapper mapper;
    public InternalAuthenticationFilter(InternalAuthenticator authenticator,ObjectMapper mapper){this.authenticator=authenticator;this.mapper=mapper;}
    @Override protected boolean shouldNotFilter(HttpServletRequest request){return request.getRequestURI().startsWith("/actuator/health");}
    @Override protected void doFilterInternal(HttpServletRequest request,HttpServletResponse response,FilterChain chain)throws ServletException,IOException{
        if(authenticator.authenticate(request)){chain.doFilter(request,response);return;}
        response.setStatus(401);response.setContentType(MediaType.APPLICATION_JSON_VALUE);
        mapper.writeValue(response.getOutputStream(),new ErrorResponse("UNAUTHORIZED","Internal authentication required",MDC.get("request_id"),false));
    }
}
