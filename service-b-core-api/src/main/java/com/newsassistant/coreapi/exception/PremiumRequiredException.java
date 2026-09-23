package com.newsassistant.coreapi.exception;

public class PremiumRequiredException extends RuntimeException {
    public PremiumRequiredException() {
        super("This feature requires an active Premium subscription.");
    }
}
