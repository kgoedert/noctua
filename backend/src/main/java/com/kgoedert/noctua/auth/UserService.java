package com.kgoedert.noctua.auth;

import java.time.OffsetDateTime;

import org.springframework.stereotype.Service;

@Service
public class UserService {

    private final UserRepository userRepository;

    public UserService(UserRepository userRepository) {
        this.userRepository = userRepository;
    }

    public User findOrCreateFromGoogle(GoogleUser googleUser) {

        return userRepository
                .findByGoogleSubject(googleUser.subject())
                .orElseGet(() -> createFromGoogle(googleUser));
    }

    private User createFromGoogle(GoogleUser googleUser) {

        User user = new User();

        user.setGoogleSubject(googleUser.subject());
        user.setEmail(googleUser.email());
        user.setName(googleUser.name());
        user.setCreatedAt(OffsetDateTime.now());
        user.setUpdatedAt(OffsetDateTime.now());

        return userRepository.save(user);
    }
}