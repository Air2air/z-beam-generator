"""API connectivity utilities."""

import os
import socket
import ssl
import time
import logging
import certifi

# Add to generator.py before creating the orchestrator
os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()

logger = logging.getLogger("z-beam")

def check_api_connectivity(provider=None):
    """Check connectivity to API providers."""
    providers = {
        "openai": "api.openai.com",
        "deepseek": "api.deepseek.com", 
        "xai": "api.xai.com",  # Placeholder
        "gemini": "generativelanguage.googleapis.com"
    }
    
    results = {}
    
    # If provider is specified, only check that one
    if provider and provider in providers:
        check_providers = {provider: providers[provider]}
    else:
        check_providers = providers
    
    # Check if we have API keys for each provider
    for provider, host in check_providers.items():
        key_env = f"{provider.upper()}_API_KEY"
        if key_env not in os.environ and provider == "openai":
            key_env = "OPENAI_API_KEY"  # Check common alternative
            
        has_key = key_env in os.environ
        
        if not has_key:
            logger.warning(f"No API key found for {provider} (looking for {key_env})")
        else:
            logger.info(f"Found API key for {provider}")
        
        # Only check connectivity for providers with keys
        if has_key:
            try:
                logger.info(f"Testing connectivity to {host}...")
                # Try to connect on port 443 (HTTPS)
                start_time = time.time()
                sock = socket.create_connection((host, 443), timeout=5)
                sock.close()
                
                # Try SSL handshake
                ssl_context = ssl.create_default_context(cafile=certifi.where())
                conn = ssl_context.wrap_socket(
                    socket.socket(socket.AF_INET),
                    server_hostname=host
                )
                conn.connect((host, 443))
                conn.close()
                
                latency = (time.time() - start_time) * 1000
                logger.info(f"Successfully connected to {host} (latency: {latency:.2f}ms)")
                results[provider] = {"status": "OK", "latency": f"{latency:.2f}ms"}
            except Exception as e:
                logger.error(f"Failed to connect to {provider} API: {str(e)}")
                results[provider] = {"status": "ERROR", "message": str(e)}
    
    return results