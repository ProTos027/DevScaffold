package com.example.urlshortener.repository;

import com.example.urlshortener.model.Url;
import org.springframework.stereotype.Repository;

import java.util.Optional;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicLong;

@Repository
public class InMemoryUrlRepository implements UrlRepository {

    private final ConcurrentHashMap<String, Url> shortCodeMap = new ConcurrentHashMap<>();
    private final ConcurrentHashMap<String, Url> originalUrlMap = new ConcurrentHashMap<>();
    private final AtomicLong idCounter = new AtomicLong();

    @Override
    public Optional<Url> findByShortCode(String shortCode) {
        return Optional.ofNullable(shortCodeMap.get(shortCode));
    }

    @Override
    public Optional<Url> findByOriginalUrl(String originalUrl) {
        return Optional.ofNullable(originalUrlMap.get(originalUrl));
    }

    @Override
    public Url save(Url url) {
        if (url.getId() == null) {
            url.setId(String.valueOf(idCounter.incrementAndGet()));
        }
        shortCodeMap.put(url.getShortCode(), url);
        originalUrlMap.put(url.getOriginalUrl(), url);
        return url;
    }

    @Override
    public Url update(Url url) {
        // In this in-memory implementation, simply putting it again updates it.
        // Ensure the ID and shortCode remain the same.
        if (shortCodeMap.containsKey(url.getShortCode())) {
            shortCodeMap.put(url.getShortCode(), url);
            originalUrlMap.put(url.getOriginalUrl(), url);
            return url;
        }
        return null; // Or throw an exception if not found
    }

    @Override
    public boolean existsByShortCode(String shortCode) {
        return shortCodeMap.containsKey(shortCode);
    }
}