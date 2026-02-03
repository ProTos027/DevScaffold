package com.example.urlshortener.repository;

import com.example.urlshortener.model.Url;
import java.util.Optional;

public interface UrlRepository {
    Optional<Url> findByShortCode(String shortCode);
    Optional<Url> findByOriginalUrl(String originalUrl);
    Url save(Url url);
    Url update(Url url);
    boolean existsByShortCode(String shortCode);
}