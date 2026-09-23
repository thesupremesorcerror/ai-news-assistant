package com.newsassistant.coreapi.controller;

import com.newsassistant.coreapi.dto.NewsAskRequest;
import com.newsassistant.coreapi.dto.NewsAskResponse;
import com.newsassistant.coreapi.service.NewsService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

/**
 * Secured by SecurityConfig (anyRequest().authenticated()) — every
 * request here must carry a valid Bearer JWT. Premium-tier gating
 * happens inside NewsService.
 */
@RestController
@RequestMapping("/api/news")
@RequiredArgsConstructor
public class NewsController {

    private final NewsService newsService;

    @PostMapping("/ask")
    public ResponseEntity<NewsAskResponse> ask(
            @Valid @RequestBody NewsAskRequest request,
            Authentication authentication
    ) {
        String userEmail = authentication.getName();
        NewsAskResponse response = newsService.askNews(userEmail, request);
        return ResponseEntity.ok(response);
    }
}
