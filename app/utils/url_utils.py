from urllib.parse import urlparse

def normalize_url(url: str) -> str:
    """
    Normalize a URL to ensure it's either absolute or starts with a leading slash.
    """
    if not url:
        return url
        
    parsed = urlparse(url)
    
    # If it's an absolute URL (has scheme like http:// or https://)
    if parsed.scheme:
        return url
    
    # If it starts with a leading slash, it's already a valid local URL
    if url.startswith('/'):
        return url
        
    # Convert relative path to absolute path by adding leading slash
    return f'/{url}'
