-- RareSource Search Cache Table
-- Stores search results to reduce API costs and improve response time

CREATE TABLE IF NOT EXISTS search_cache (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  part_number TEXT NOT NULL,
  results JSONB NOT NULL,
  source_count INTEGER DEFAULT 0,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
  search_count INTEGER DEFAULT 1,
  last_accessed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index for fast part number lookups
CREATE INDEX IF NOT EXISTS idx_search_cache_part_number ON search_cache(part_number);

-- Index for expiration cleanup
CREATE INDEX IF NOT EXISTS idx_search_cache_expires_at ON search_cache(expires_at);

-- Index for analytics
CREATE INDEX IF NOT EXISTS idx_search_cache_created_at ON search_cache(created_at);

-- Function to delete expired cache entries
CREATE OR REPLACE FUNCTION delete_expired_cache()
RETURNS INTEGER AS $$
DECLARE
  deleted_count INTEGER;
BEGIN
  DELETE FROM search_cache WHERE expires_at < NOW();
  GET DIAGNOSTICS deleted_count = ROW_COUNT;
  RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Optional: Schedule automatic cleanup (requires pg_cron extension)
-- SELECT cron.schedule('cleanup-expired-cache', '0 * * * *', 'SELECT delete_expired_cache()');

COMMENT ON TABLE search_cache IS 'Caches search results to reduce API costs and improve performance';
COMMENT ON COLUMN search_cache.part_number IS 'The searched part number (case-insensitive)';
COMMENT ON COLUMN search_cache.results IS 'JSON array of search results from all sources';
COMMENT ON COLUMN search_cache.source_count IS 'Number of data sources that returned results';
COMMENT ON COLUMN search_cache.expires_at IS 'Cache expiration timestamp (default: 1 hour from creation)';
COMMENT ON COLUMN search_cache.search_count IS 'Number of times this part has been searched';
COMMENT ON COLUMN search_cache.last_accessed_at IS 'Last time this cache entry was accessed';
