package com.smartly.banking.mobilebff.api;
import com.smartly.banking.mobilebff.api.ApiModels.ChatRequest;
import com.smartly.banking.mobilebff.api.ApiModels.ChatResponse;
import com.smartly.banking.mobilebff.orchestrator.MobileRequestContext;
import com.smartly.banking.mobilebff.service.MobileChatService;
import jakarta.validation.Valid;
import java.util.Locale;
import java.util.Set;
import java.util.UUID;
import java.util.regex.Pattern;
import org.springframework.http.MediaType;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.server.ServerWebExchange;
import reactor.core.publisher.Mono;
@RestController
public class MobileChatController{
 private static final Pattern SAFE_ID=Pattern.compile("^[A-Za-z0-9._:-]{1,128}$"),APP_VERSION=Pattern.compile("^[A-Za-z0-9._+-]{1,32}$");
 private final MobileChatService service;
 public MobileChatController(MobileChatService service){this.service=service;}
 @PostMapping(value={"/chat","/api/mobile/v1/chat"},consumes=MediaType.APPLICATION_JSON_VALUE,produces=MediaType.APPLICATION_JSON_VALUE)
 public Mono<ChatResponse> chat(@Valid @RequestBody ChatRequest request,ServerWebExchange exchange){
  var h=exchange.getRequest().getHeaders();String requestId=safe(h.getFirst("X-Request-Id"),SAFE_ID,UUID.randomUUID().toString()),correlationId=safe(h.getFirst("X-Correlation-Id"),SAFE_ID,requestId),conversationId=request.conversationId();
  String traceparent=safe(h.getFirst("traceparent"),Pattern.compile("^[0-9a-f]{2}-[0-9a-f]{32}-[0-9a-f]{16}-[0-9a-f]{2}$"),null),appVersion=safe(h.getFirst("X-App-Version"),APP_VERSION,null),device=device(h.getFirst("X-Device-Class"));
  exchange.getAttributes().put("request_id",requestId);exchange.getResponse().getHeaders().set("X-Request-Id",requestId);exchange.getResponse().getHeaders().set("X-Correlation-Id",correlationId);
  return service.chat(request,h,new MobileRequestContext(requestId,correlationId,conversationId,traceparent,appVersion,device));
 }
 private static String safe(String value,Pattern pattern,String fallback){return value!=null&&pattern.matcher(value).matches()?value:fallback;}
 private static String device(String value){if(value==null)return null;String normalized=value.toUpperCase(Locale.ROOT);return Set.of("PHONE","TABLET","UNKNOWN").contains(normalized)?normalized:null;}
}
