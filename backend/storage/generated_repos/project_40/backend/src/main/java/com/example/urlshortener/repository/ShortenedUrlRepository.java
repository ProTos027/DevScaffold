package com.example.urlshortener.repository;

import com.example.urlshortener.model.ShortenedUrl;
import java.util.Optional;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

/**
 * Repository interface for ShortenedUrl entities.
 * Provides data access operations for persisting and retrieving ShortenedUrl objects.
 */
@Repository
public interface ShortenedUrlRepository extends JpaRepository<ShortenedUrl, Long> {

    /**
     * Retrieves a ShortenedUrl entity by its short code.
     *
     * @param shortCode The unique short code of the URL.
     * @return An Optional containing the ShortenedUrl if found, or an empty Optional otherwise.
     */
    Optional<ShortenedUrl> findByShortCode(String shortCode);

    /**
     * Retrieves a ShortenedUrl entity by its original URL.
     *
     * @param originalUrl The original URL.
     * @return An Optional containing the ShortenedUrl if found, or an empty Optional otherwise.
     */
    Optional<ShortenedUrl> findByOriginalUrl(String originalUrl);
}
