package com.smartly.banking.mobilebff.api;
import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.databind.JsonNode;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Pattern;
import jakarta.validation.constraints.Size;
import java.util.List;
public final class ApiModels{
 private ApiModels(){}
 public record ChatRequest(@NotBlank @Size(max=128) @JsonProperty("customer_id") String customerId,@NotBlank @Size(max=8000) String message,@Size(max=128) @JsonProperty("conversation_id") String conversationId,@Pattern(regexp="^[a-z]{2,3}(?:-[A-Z]{2})?$") String locale){}
 public record OrchestratorChatRequest(@JsonProperty("customer_id") String customerId,String message,@JsonProperty("conversation_id") String conversationId,String locale){}
 public record Evidence(String type,String source,String content,JsonNode data,Double confidence,JsonNode metadata){}
 public record ChatResponse(String answer,String source,List<Evidence> sources,@JsonProperty("conversation_id") String conversationId,@JsonProperty("request_id") String requestId){}
 public record SafeError(String code,String message,@JsonProperty("request_id") String requestId,boolean retryable){}
}
