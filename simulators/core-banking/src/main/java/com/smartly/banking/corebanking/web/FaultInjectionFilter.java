package com.smartly.banking.corebanking.web;

import jakarta.servlet.*;
import jakarta.servlet.http.*;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.core.Ordered;
import org.springframework.core.annotation.Order;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Component;
import org.springframework.web.filter.OncePerRequestFilter;
import java.io.IOException;

@Component @Order(Ordered.HIGHEST_PRECEDENCE+20)
public class FaultInjectionFilter extends OncePerRequestFilter {
    private final boolean enabled; private final long maxLatencyMs;
    public FaultInjectionFilter(@Value("${simulator.faults.enabled:false}")boolean enabled,@Value("${simulator.faults.max-latency-ms:5000}")long maxLatencyMs){this.enabled=enabled;this.maxLatencyMs=maxLatencyMs;}
    @Override protected boolean shouldNotFilter(HttpServletRequest request){return !enabled||!request.getRequestURI().startsWith("/internal/");}
    @Override protected void doFilterInternal(HttpServletRequest request,HttpServletResponse response,FilterChain chain)throws ServletException,IOException{
        String fault=request.getHeader("X-Simulator-Fault");
        if("latency".equalsIgnoreCase(fault)){long requested=parse(request.getHeader("X-Simulator-Latency-Ms"),1000);try{Thread.sleep(Math.min(Math.max(requested,0),maxLatencyMs));}catch(InterruptedException e){Thread.currentThread().interrupt();throw new ServletException("Fault simulation interrupted",e);}}
        else if("error".equalsIgnoreCase(fault)){response.sendError(500,"Simulated internal error");return;}
        else if("unavailable".equalsIgnoreCase(fault)){response.sendError(503,"Simulated unavailable service");return;}
        else if("malformed".equalsIgnoreCase(fault)){response.setStatus(200);response.setContentType(MediaType.APPLICATION_JSON_VALUE);response.getWriter().write("{malformed-json");return;}
        chain.doFilter(request,response);
    }
    private long parse(String value,long fallback){try{return value==null?fallback:Long.parseLong(value);}catch(NumberFormatException ignored){return fallback;}}
}
