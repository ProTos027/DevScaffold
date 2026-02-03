CREATE TABLE IF NOT EXISTS shortened_url (
    id BIGSERIAL PRIMARY KEY,
    long_url TEXT NOT NULL UNIQUE,
    short_code VARCHAR(10) NOT NULL UNIQUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP WITH TIME ZONE,
    click_count BIGINT DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_short_code ON shortened_url (short_code);
CREATE INDEX IF NOT EXISTS idx_long_url ON shortened_url (long_url);