package com.kgoedert.noctua.auth;

import java.time.Instant;

import org.springframework.security.oauth2.jwt.JwtClaimsSet;
import org.springframework.security.oauth2.jwt.JwtEncoder;
import org.springframework.security.oauth2.jwt.JwtEncoderParameters;
import org.springframework.stereotype.Service;

@Service
public class JwtService {

    private static final long ACCESS_TOKEN_EXPIRATION_SECONDS = 15 * 60;

    private final JwtEncoder jwtEncoder;

    public JwtService(JwtEncoder jwtEncoder) {
        this.jwtEncoder = jwtEncoder;
    }

    public String generateAccessToken(User user) {
        Instant now = Instant.now();

        JwtClaimsSet claims = JwtClaimsSet.builder()
                .issuer("noctua")
                .subject(user.getId().toString())
                .issuedAt(now)
                .expiresAt(now.plusSeconds(ACCESS_TOKEN_EXPIRATION_SECONDS))
                .claim("email", user.getEmail())
                .claim("name", user.getName())
                .build();

        return jwtEncoder
                .encode(JwtEncoderParameters.from(claims))
                .getTokenValue();
    }
}