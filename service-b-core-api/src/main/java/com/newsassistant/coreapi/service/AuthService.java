package com.newsassistant.coreapi.service;

import com.newsassistant.coreapi.dto.AuthResponse;
import com.newsassistant.coreapi.dto.LoginRequest;
import com.newsassistant.coreapi.dto.RegisterRequest;
import com.newsassistant.coreapi.exception.EmailAlreadyExistsException;
import com.newsassistant.coreapi.exception.InvalidCredentialsException;
import com.newsassistant.coreapi.model.Role;
import com.newsassistant.coreapi.model.User;
import com.newsassistant.coreapi.repository.UserRepository;
import com.newsassistant.coreapi.security.CustomUserDetailsService;
import com.newsassistant.coreapi.security.JwtUtil;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.BadCredentialsException;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

@Slf4j
@Service
@RequiredArgsConstructor
public class AuthService {

    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;
    private final JwtUtil jwtUtil;
    private final AuthenticationManager authenticationManager;
    private final CustomUserDetailsService userDetailsService;

    public AuthResponse register(RegisterRequest request) {
        String normalizedEmail = request.getEmail().trim().toLowerCase();

        if (userRepository.existsByEmail(normalizedEmail)) {
            throw new EmailAlreadyExistsException(normalizedEmail);
        }

        User user = User.builder()
                .email(normalizedEmail)
                .passwordHash(passwordEncoder.encode(request.getPassword()))
                .role(Role.USER)
                .isPremium(false)
                .build();

        userRepository.save(user);
        log.info("Registered new user: {}", normalizedEmail);

        UserDetails userDetails = userDetailsService.loadUserByUsername(normalizedEmail);
        String token = jwtUtil.generateToken(userDetails);

        return AuthResponse.builder()
                .token(token)
                .tokenType("Bearer")
                .email(user.getEmail())
                .role(user.getRole().name())
                .build();
    }

    public AuthResponse login(LoginRequest request) {
        String normalizedEmail = request.getEmail().trim().toLowerCase();

        try {
            authenticationManager.authenticate(
                    new UsernamePasswordAuthenticationToken(normalizedEmail, request.getPassword())
            );
        } catch (BadCredentialsException e) {
            throw new InvalidCredentialsException();
        }

        User user = userRepository.findByEmail(normalizedEmail)
                .orElseThrow(InvalidCredentialsException::new);

        UserDetails userDetails = userDetailsService.loadUserByUsername(normalizedEmail);
        String token = jwtUtil.generateToken(userDetails);

        return AuthResponse.builder()
                .token(token)
                .tokenType("Bearer")
                .email(user.getEmail())
                .role(user.getRole().name())
                .build();
    }
}
