package com.example.urlshortener.repository;

import com.example.urlshortener.model.ShortenedUrl;
import org.springframework.stereotype.Repository;

import java.util.Optional;
import java.util.concurrent.ConcurrentHashMap;

@Repository
public class InMemoryUrlRepository implements UrlRepository {

    // Stores shortCode -> ShortenedUrl object
    private final ConcurrentHashMap<String, ShortenedUrl> shortCodeMap = new ConcurrentHashMap<>();
    // Stores originalUrl -> ShortenedUrl object (for quick lookup by original URL)
    private final ConcurrentHashMap<String, ShortenedUrl> originalUrlMap = new ConcurrentHashMap<>();

    @Override
    public ShortenedUrl save(ShortenedUrl shortenedUrl) {
        shortCodeMap.put(shortenedUrl.getShortCode(), shortenedUrl);
        originalUrlMap.put(shortenedUrl.getOriginalUrl(), shortenedUrl);
        return shortenedUrl;
    }

    @Override
    public Optional<ShortenedUrl> findByShortCode(String shortCode) {
        return Optional.ofNullable(shortCodeMap.get(shortCode));
    }

    @Override
    public Optional<ShortenedUrl> findByOriginalUrl(String originalUrl) {
        return Optional.ofNullable(originalUrlMap.get(originalUrl));
    }
}