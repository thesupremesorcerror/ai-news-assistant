package com.newsassistant.coreapi.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Positive;
import lombok.Data;

@Data
public class CreateOrderRequest {

    @Positive(message = "Amount must be a positive number (in the smallest currency unit, e.g. paise)")
    private long amount;

    @NotBlank(message = "Currency is required, e.g. INR")
    private String currency;

    @NotBlank(message = "Receipt id is required")
    private String receiptId;
}
