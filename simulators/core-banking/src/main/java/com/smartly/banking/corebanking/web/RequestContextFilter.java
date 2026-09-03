package com.smartly.banking.corebanking.web;

import io.micrometer.core.instrument.MeterRegistry;
import io.micrometer.core.instrument.Timer;
import jakarta.servlet.*;
import jakarta.servlet.http.*;
import org.slf4j.MDC;
import org.springframework.core.Ordered;
import org.springframework.core.annotation.Order;
import org.springframework.stereotype.Component;
import org.springframework.web.filter.OncePerRequestFilter;
import java.io.IOException;
import java.util.UUID;

@Component("coreBankingRequestContextFilter") @Order(Ordered.HIGHEST_PRECEDENCE)
public class RequestContextFilter extends OncePerRequestFilter {
    private final MeterRegistry registry;
    public RequestContextFilter(MeterRegistry registry){this.registry=registry;}
    @Override protected void doFilterInternal(HttpServletRequest request,HttpServletResponse response,FilterChain chain)throws ServletException,IOException{
        String requestId=safeId(request.getHeader("X-Request-Id"),UUID.randomUUID().toString());
        String correlationId=safeId(request.getHeader("X-Correlation-Id"),requestId);
        Timer.Sample sample=Timer.start(registry);
        try(MDC.MDCCloseable ignored1=MDC.putCloseable("request_id",requestId);MDC.MDCCloseable ignored2=MDC.putCloseable("correlation_id",correlationId)){
            response.setHeader("X-Request-Id",requestId); response.setHeader("X-Correlation-Id",correlationId);
            chain.doFilter(request,response);
        } finally {
            sample.stop(registry.timer("core_banking.http.server.requests","method",request.getMethod(),"status",Integer.toString(response.getStatus())));
        }
    }
    private String safeId(String value,String fallback){return value!=null&&!value.isBlank()&&value.length()<=128&&value.matches("[A-Za-z0-9._:-]+")?value:fallback;}
}
