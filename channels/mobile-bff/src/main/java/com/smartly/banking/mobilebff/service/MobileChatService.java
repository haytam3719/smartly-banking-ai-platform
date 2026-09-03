package com.smartly.banking.mobilebff.service;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ArrayNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.smartly.banking.mobilebff.api.ApiModels.*;
import com.smartly.banking.mobilebff.auth.AuthenticationPort;
import com.smartly.banking.mobilebff.orchestrator.*;
import java.util.ArrayList;
import java.util.List;
import java.util.Set;
import org.springframework.http.HttpHeaders;
import org.springframework.stereotype.Service;
import reactor.core.publisher.Mono;
@Service
public class MobileChatService{
 private static final Set<String> FORBIDDEN=Set.of("base_url","internal_url","stack_trace","stacktrace","traceback","exception");
 private final AuthenticationPort authentication;private final OrchestratorClient orchestrator;
 public MobileChatService(AuthenticationPort authentication,OrchestratorClient orchestrator){this.authentication=authentication;this.orchestrator=orchestrator;}
 public Mono<ChatResponse> chat(ChatRequest request,HttpHeaders headers,MobileRequestContext context){
  String locale=request.locale()==null||request.locale().isBlank()?"fr-FR":request.locale();var downstream=new OrchestratorChatRequest(request.customerId(),request.message(),request.conversationId(),locale);
  return authentication.authenticate(headers,request).flatMap(p->orchestrator.chat(downstream,p,context)).map(this::sanitize);
 }
 private ChatResponse sanitize(ChatResponse response){
  if(response==null||response.answer()==null||response.source()==null||response.conversationId()==null||response.requestId()==null)throw new OrchestratorException("MALFORMED_ORCHESTRATOR_RESPONSE",false);
  var evidence=new ArrayList<Evidence>();if(response.sources()!=null)for(var e:response.sources())evidence.add(new Evidence(e.type(),e.source(),e.content(),safe(e.data()),e.confidence(),safe(e.metadata())));
  return new ChatResponse(response.answer(),response.source(),List.copyOf(evidence),response.conversationId(),response.requestId());
 }
 private JsonNode safe(JsonNode node){
  if(node==null)return null;JsonNode copy=node.deepCopy();scrub(copy);return copy;
 }
 private void scrub(JsonNode node){
  if(node instanceof ObjectNode object){var names=new ArrayList<String>();object.fieldNames().forEachRemaining(names::add);for(var name:names){if(FORBIDDEN.contains(name.toLowerCase()))object.remove(name);else scrub(object.get(name));}}
  else if(node instanceof ArrayNode array)array.forEach(this::scrub);
 }
}
