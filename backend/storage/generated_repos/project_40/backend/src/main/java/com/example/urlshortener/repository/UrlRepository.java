package com.example.urlshortener.repository;

import com.example.urlshortener.model.ShortenedUrl;
import java.util.Optional;

public interface UrlRepository {
    ShortenedUrl save(ShortenedUrl shortenedUrl);
    Optional<ShortenedUrl> findByShortCode(String shortCode);
    Optional<ShortenedUrl> findByOriginalUrl(String originalUrl);
}