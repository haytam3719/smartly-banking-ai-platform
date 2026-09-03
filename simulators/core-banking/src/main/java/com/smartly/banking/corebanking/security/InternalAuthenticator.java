package com.smartly.banking.corebanking.security;
import jakarta.servlet.http.HttpServletRequest;
public interface InternalAuthenticator { boolean authenticate(HttpServletRequest request); }
