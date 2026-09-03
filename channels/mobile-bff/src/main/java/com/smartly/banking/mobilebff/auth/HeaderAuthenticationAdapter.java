package com.smartly.banking.mobilebff.auth;
import com.smartly.banking.mobilebff.api.ApiModels.ChatRequest;
import com.smartly.banking.mobilebff.config.MobileBffProperties;
import org.springframework.http.HttpHeaders;
import org.springframework.stereotype.Component;
import reactor.core.publisher.Mono;
@Component
public class HeaderAuthenticationAdapter implements AuthenticationPort{
 private static final String DEFAULT_SCOPES="account:read,card:read,transfer:read,customer:read,knowledge:search,account:open";
 private final MobileBffProperties properties;
 public HeaderAuthenticationAdapter(MobileBffProperties properties){this.properties=properties;}
 public Mono<MobilePrincipal> authenticate(HttpHeaders headers,ChatRequest request){
  String subject=headers.getFirst("X-Demo-Subject-Id"),customer=headers.getFirst("X-Demo-Customer-Id");
  if(properties.authentication().demoMode()){subject=subject==null?"demo-mobile-user":subject;customer=customer==null?request.customerId():customer;}
  if(subject==null||customer==null)return Mono.error(new AuthenticationException("Authenticated mobile session required"));
  if(!customer.equals(request.customerId()))return Mono.error(new CustomerContextException());
  return Mono.just(new MobilePrincipal(subject,customer,headers.getFirst("X-Demo-Scopes")==null?DEFAULT_SCOPES:headers.getFirst("X-Demo-Scopes")));
 }
 public static class CustomerContextException extends RuntimeException{}
}
