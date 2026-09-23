package com.newsassistant.coreapi.dto;

import jakarta.validation.constraints.NotBlank;
import lombok.Data;

@Data
public class NewsAskRequest {

    @NotBlank(message = "Query is required")
    private String query;
}
