# API Client Caching

This document describes the API client caching system used in the Z-Beam Generator.

## Overview

The Z-Beam Generator uses a sophisticated caching system for API clients to improve performance and reduce initialization overhead. This caching system:

1. **Persists API clients** between program runs, reducing connection and authentication overhead
2. **Automatically preloads** common API clients during batch operations
3. **Provides detailed statistics** about cache performance
4. **Optimizes resource usage** by reusing existing connections

## Default Behavior

By default, the system uses a persistent cache that saves API client state to disk. This means:

- API clients created during one run will be available in subsequent runs
- No need to reinitialize connections for every run
- Significant performance improvements for batch operations

## Cache Commands

The following commands can be used to manage the API client cache:

```bash
# Preload cache with common API clients
python3 run.py --preload-cache

# View cache statistics
python3 run.py --cache-stats

# View detailed cache information
python3 run.py --cache-info

# Clear the cache (both memory and disk)
python3 run.py --clear-cache

# Disable persistent caching (not recommended)
python3 run.py --no-persistent-cache
```

## Cache Location

The persistent cache is stored in a temporary directory specific to your system:

- macOS/Linux: `/tmp/z-beam-cache` or `/var/folders/.../z-beam-cache`
- Windows: `C:\Users\<username>\AppData\Local\Temp\z-beam-cache`

## Advanced Configuration

The caching system can be configured through environment variables:

```bash
# Disable persistent caching
export Z_BEAM_NO_PERSISTENT_CACHE=true

# Run with in-memory cache only
Z_BEAM_NO_PERSISTENT_CACHE=true python3 run.py
```

## Performance Benefits

Using the persistent cache typically results in:

- 80-90% reduction in API client initialization time
- Elimination of repeated authentication overhead
- More efficient batch processing
- Better error handling and connection stability

## Implementation Details

The caching system is implemented using several components:

1. `cache_adapter.py` - Primary interface that automatically selects the best cache implementation
2. `persistent_cache.py` - Implements disk-based persistent caching
3. `client_cache.py` - Fallback in-memory caching when persistence is disabled

## Cache Statistics

Cache statistics can be viewed using the `--cache-stats` command. Key metrics include:

- **Hit rate**: Percentage of requests served from cache
- **Cache hits**: Number of times a client was retrieved from cache
- **Cache misses**: Number of times a new client had to be created
- **Cached instances**: Number of clients currently in memory
- **Disk cached instances**: Number of clients saved to disk

## Best Practices

For optimal performance:

1. Always preload the cache before batch operations
2. Use the persistent cache (default behavior)
3. Monitor cache statistics to ensure high hit rates
4. Clear the cache only when necessary (e.g., after API changes)

## Troubleshooting

If you encounter issues with the cache:

1. Try clearing the cache with `--clear-cache`
2. Check detailed cache information with `--cache-info`
3. Temporarily disable persistence with `--no-persistent-cache`
4. Ensure your temporary directory has proper permissions
