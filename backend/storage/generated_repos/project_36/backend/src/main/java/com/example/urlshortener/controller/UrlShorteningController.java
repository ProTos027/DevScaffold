package com.example.urlshortener.controller;

import com.example.urlshortener.service.UrlShorteningService;
import jakarta.servlet.http.HttpServletResponse;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.io.IOException;
import java.net.URI;
import java.util.Map;

@RestController
public class UrlShorteningController {

    private final UrlShorteningService urlShorteningService;

    public UrlShorteningController(UrlShorteningService urlShorteningService) {
        this.urlShorteningService = urlShorteningService;
    }

    @PostMapping("/api/shorten")
    public ResponseEntity<Map<String, String>> createShortUrl(@RequestBody Map<String, String> request) {
        String originalUrl = request.get("originalUrl");
        if (originalUrl == null || originalUrl.trim().isEmpty()) {
            return ResponseEntity.badRequest().body(Map.of("error", "Original URL cannot be empty."));
        }

        var url = urlShorteningService.shortenUrl(originalUrl);
        String shortUrl = urlShorteningService.getBaseUrl() + "/" + url.getShortCode();
        return ResponseEntity.status(HttpStatus.CREATED).body(Map.of(
                "originalUrl", url.getOriginalUrl(),
                "shortUrl", shortUrl
        ));
    }

    @GetMapping("/{shortCode}")
    public ResponseEntity<Void> redirectToOriginalUrl(@PathVariable String shortCode) {
        String originalUrl = urlShorteningService.retrieveOriginalUrl(shortCode);
        return ResponseEntity.status(HttpStatus.FOUND)
                .location(URI.create(originalUrl))
                .build();
    }
}