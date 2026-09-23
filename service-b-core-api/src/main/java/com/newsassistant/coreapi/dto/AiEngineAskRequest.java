package com.newsassistant.coreapi.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * Request body sent FROM this service TO Service A (FastAPI /api/ask).
 * Field names must match the FastAPI Pydantic model exactly (snake_case).
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class AiEngineAskRequest {

    private String query;

    @JsonProperty("top_k")
    private int topK;
}
