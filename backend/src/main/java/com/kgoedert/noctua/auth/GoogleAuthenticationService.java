package com.kgoedert.noctua.auth;

import java.io.IOException;
import java.security.GeneralSecurityException;
import java.util.List;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import com.google.api.client.googleapis.auth.oauth2.GoogleIdToken;
import com.google.api.client.googleapis.auth.oauth2.GoogleIdTokenVerifier;
import com.google.api.client.http.javanet.NetHttpTransport;
import com.google.api.client.json.gson.GsonFactory;

@Service
public class GoogleAuthenticationService {

    private final GoogleIdTokenVerifier verifier;

    public GoogleAuthenticationService(@Value("${google.client-id}") String clientId) {
        this.verifier = new GoogleIdTokenVerifier.Builder(
                new NetHttpTransport(),
                GsonFactory.getDefaultInstance())
                .setAudience(List.of(clientId))
                .build();
    }

    public GoogleUser verify(String credential) throws GeneralSecurityException, IOException {
        GoogleIdToken idToken = verifier.verify(credential);

        if (idToken == null) {
            throw new UnauthorizedException("Invalid Google credential");
        }

        GoogleIdToken.Payload payload = idToken.getPayload();

        return new GoogleUser(
                payload.getSubject(),
                payload.getEmail(),
                (String) payload.get("name")
        );
    }
}
