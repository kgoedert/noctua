package com.kgoedert.noctua.auth;

public record UserResponse(
        Long id,
        String email,
        String name) {
}