package com.kgoedert.noctua.auth;

public record GoogleUser(
    String subject,
    String email,
    String name
) {
}