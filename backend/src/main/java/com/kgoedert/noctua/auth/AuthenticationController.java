package com.kgoedert.noctua.auth;

import java.io.IOException;
import java.security.GeneralSecurityException;

import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/auth")
public class AuthenticationController {

    private final GoogleAuthenticationService googleAuthenticationService;
    private final UserService userService;
    private final JwtService jwtService;

    public AuthenticationController(
            GoogleAuthenticationService googleAuthenticationService,
            UserService userService,
            JwtService jwtService) {
        this.googleAuthenticationService = googleAuthenticationService;
        this.userService = userService;
        this.jwtService = jwtService;
    }

    @PostMapping("/google")
    public AuthenticationResponse googleLogin(
            @RequestBody GoogleLoginRequest request)
            throws GeneralSecurityException, IOException {

        GoogleUser googleUser = googleAuthenticationService.verify(request.credential());

        User user = userService.findOrCreateFromGoogle(googleUser);

        String accessToken = jwtService.generateAccessToken(user);

        return new AuthenticationResponse(accessToken);
    }
}
