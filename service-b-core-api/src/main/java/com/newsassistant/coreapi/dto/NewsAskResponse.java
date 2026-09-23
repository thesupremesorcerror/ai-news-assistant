package com.newsassistant.coreapi.dto;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;

/**
 * Mirrors Service A's (FastAPI) POST /api/ask response body:
 *   { "query": ..., "answer": ..., "sources": [...], "retrieved_chunks": [...] }
 *
 * @JsonIgnoreProperties(ignoreUnknown = true) keeps this DTO resilient
 * to the AI engine adding fields later.
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
@JsonIgnoreProperties(ignoreUnknown = true)
public class NewsAskResponse {

    private String query;
    private String answer;
    private List<String> sources;

    @JsonProperty("retrieved_chunks")
    private List<RetrievedChunkDto> retrievedChunks;

    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    @JsonIgnoreProperties(ignoreUnknown = true)
    public static class RetrievedChunkDto {
        private String title;

        @JsonProperty("content_chunk")
        private String contentChunk;

        @JsonProperty("source_url")
        private String sourceUrl;

        @JsonProperty("published_date")
        private String publishedDate;

        private double score;
    }
}
