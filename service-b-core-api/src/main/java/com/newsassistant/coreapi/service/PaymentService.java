package com.newsassistant.coreapi.service;

import com.newsassistant.coreapi.dto.CreateOrderRequest;
import com.newsassistant.coreapi.dto.CreateOrderResponse;
import com.newsassistant.coreapi.exception.PaymentGatewayException;
import com.razorpay.Order;
import com.razorpay.RazorpayClient;
import com.razorpay.RazorpayException;
import lombok.extern.slf4j.Slf4j;
import org.json.JSONObject;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

/**
 * Stub Razorpay integration: standard client instantiation + order
 * request JSON, per Phase 4 scope. Signature verification of the
 * payment callback/webhook is intentionally out of scope here and
 * would be added alongside a `/api/payment/verify` endpoint.
 */
@Slf4j
@Service
public class PaymentService {

    @Value("${razorpay.key-id}")
    private String keyId;

    @Value("${razorpay.key-secret}")
    private String keySecret;

    public CreateOrderResponse createOrder(CreateOrderRequest request) {
        if (keyId == null || keyId.isBlank() || keySecret == null || keySecret.isBlank()) {
            throw new PaymentGatewayException(
                    "Razorpay credentials are not configured. Set razorpay.key-id / razorpay.key-secret.",
                    null
            );
        }

        try {
            RazorpayClient razorpayClient = new RazorpayClient(keyId, keySecret);

            JSONObject orderRequest = new JSONObject();
            orderRequest.put("amount", request.getAmount()); // smallest currency unit, e.g. paise
            orderRequest.put("currency", request.getCurrency());
            orderRequest.put("receipt", request.getReceiptId());
            orderRequest.put("payment_capture", 1); // auto-capture

            Order order = razorpayClient.orders.create(orderRequest);

            return CreateOrderResponse.builder()
                    .orderId(order.get("id"))
                    .amount(Long.parseLong(order.get("amount").toString()))
                    .currency(order.get("currency"))
                    .status(order.get("status"))
                    .receiptId(request.getReceiptId())
                    .build();

        } catch (RazorpayException e) {
            log.error("Razorpay order creation failed", e);
            throw new PaymentGatewayException(e.getMessage(), e);
        }
    }
}
