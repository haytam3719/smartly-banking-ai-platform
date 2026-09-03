package com.smartly.banking.corebanking.security;

import jakarta.servlet.http.HttpServletRequest;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;

@Component
public class ConfiguredInternalAuthenticator implements InternalAuthenticator {
    private final boolean devMode; private final String apiKey;
    public ConfiguredInternalAuthenticator(@Value("${internal-auth.dev-mode:false}") boolean devMode,@Value("${internal-auth.api-key:}") String apiKey){this.devMode=devMode;this.apiKey=apiKey;}
    @Override public boolean authenticate(HttpServletRequest request){
        if(devMode)return true;
        String authorization=request.getHeader("Authorization");
        if(authorization==null||!authorization.startsWith("Bearer ")||apiKey.isBlank())return false;
        return MessageDigest.isEqual(apiKey.getBytes(StandardCharsets.UTF_8),authorization.substring(7).getBytes(StandardCharsets.UTF_8));
    }
}
