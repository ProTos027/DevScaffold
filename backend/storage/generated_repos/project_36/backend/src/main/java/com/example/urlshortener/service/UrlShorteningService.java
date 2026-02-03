package com.example.urlshortener.service;

import com.example.urlshortener.exception.UrlNotFoundException;
import com.example.urlshortener.model.Url;
import com.example.urlshortener.repository.UrlRepository;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.Optional;
import java.util.Random;

@Service
public class UrlShorteningService {

    private final UrlRepository urlRepository;
    private final Random random = new Random();
    private static final String ALPHANUMERIC = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789";
    private static final int SHORT_CODE_LENGTH = 7;

    @Value("${server.port}")
    private String serverPort;

    @Value("${spring.application.name}")
    private String applicationName;

    public UrlShorteningService(UrlRepository urlRepository) {
        this.urlRepository = urlRepository;
    }

    public Url shortenUrl(String originalUrl) {
        // Check if the original URL already has a short code
        Optional<Url> existingUrl = urlRepository.findByOriginalUrl(originalUrl);
        if (existingUrl.isPresent()) {
            return existingUrl.get();
        }

        String shortCode;
        do {
            shortCode = generateShortCode();
        } while (urlRepository.existsByShortCode(shortCode)); // Ensure uniqueness

        LocalDateTime now = LocalDateTime.now();
        // For simplicity, expiration is set to 1 year from creation
        LocalDateTime expirationDate = now.plusYears(1);

        Url newUrl = new Url(null, originalUrl, shortCode, now, expirationDate);
        return urlRepository.save(newUrl);
    }

    public String retrieveOriginalUrl(String shortCode) {
        Url url = urlRepository.findByShortCode(shortCode)
                .orElseThrow(() -> new UrlNotFoundException("Short URL not found: " + shortCode));

        // Handle expiration (simple check, could be more robust with scheduled cleanup)
        if (url.getExpirationDate() != null && url.getExpirationDate().isBefore(LocalDateTime.now())) {
            throw new UrlNotFoundException("Short URL has expired: " + shortCode);
        }

        url.incrementClickCount();
        urlRepository.update(url);
        return url.getOriginalUrl();
    }

    private String generateShortCode() {
        StringBuilder sb = new StringBuilder(SHORT_CODE_LENGTH);
        for (int i = 0; i < SHORT_CODE_LENGTH; i++) {
            sb.append(ALPHANUMERIC.charAt(random.nextInt(ALPHANUMERIC.length())));
        }
        return sb.toString();
    }

    public String getBaseUrl() {
        // In a real application, this should be configurable (e.g., from environment or properties)
        // and consider production domain.
        return "http://localhost:" + serverPort;
    }
}