package com.kgoedert.noctua.auth;

import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class TestAuthenticationController {

    @GetMapping("/test/protected")
    public String protectedEndpoint(Authentication authentication) {
        return "Authenticated as user: " + authentication.getName();
    }
}