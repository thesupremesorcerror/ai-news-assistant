package com.newsassistant.coreapi.service;

import com.newsassistant.coreapi.dto.AiEngineAskRequest;
import com.newsassistant.coreapi.dto.NewsAskRequest;
import com.newsassistant.coreapi.dto.NewsAskResponse;
import com.newsassistant.coreapi.exception.PremiumRequiredException;
import com.newsassistant.coreapi.model.User;
import com.newsassistant.coreapi.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpMethod;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.AccessDeniedException;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

@Slf4j
@Service
@RequiredArgsConstructor
public class NewsService {

    private static final int DEFAULT_TOP_K = 3;

    private final RestTemplate restTemplate;
    private final UserRepository userRepository;

    @Value("${ai-engine.base-url}")
    private String aiEngineBaseUrl;

    /**
     * Routes an authenticated, premium user's question to Service A's
     * RAG pipeline (POST /api/ask) and returns its answer.
     *
     * @param userEmail the authenticated principal's email (from JWT/SecurityContext)
     */
    public NewsAskResponse askNews(String userEmail, NewsAskRequest request) {
        User user = userRepository.findByEmail(userEmail)
                .orElseThrow(() -> new AccessDeniedException("User not found for authenticated principal."));

        if (!user.isPremium()) {
            log.info("Blocked /api/news/ask for non-premium user: {}", userEmail);
            throw new PremiumRequiredException();
        }

        String url = aiEngineBaseUrl + "/api/ask";
        AiEngineAskRequest aiRequest = new AiEngineAskRequest(request.getQuery(), DEFAULT_TOP_K);

        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);
        HttpEntity<AiEngineAskRequest> entity = new HttpEntity<>(aiRequest, headers);

        log.info("Forwarding premium query from '{}' to AI Engine at {}", userEmail, url);

        ResponseEntity<NewsAskResponse> response = restTemplate.exchange(
                url,
                HttpMethod.POST,
                entity,
                NewsAskResponse.class
        );

        return response.getBody();
    }
}
