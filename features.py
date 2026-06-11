import re
from urllib.parse import urlparse

# List of common URL shortening services
SHORTENERS = {
    'bit.ly', 'tinyurl.com', 'goo.gl', 'rebrand.ly', 't.co', 'youtu.be',
    'ow.ly', 'is.gd', 'buff.ly', 'adf.ly', 'bit.do', 'mcaf.ee', 'su.pr'
}

# List of suspicious keywords commonly found in phishing URLs
SUSPICIOUS_KEYWORDS = [
    'login', 'secure', 'verify', 'update', 'bank', 'signin', 'account',
    'webscr', 'cmd', 'security', 'wallet', 'confirm', 'bonus', 'free', 'gift'
]

def clean_url(url: str) -> str:
    """
    Ensures the URL has a scheme (http or https) so that urlparse works properly.
    """
    url = url.strip()
    if not url:
        return ""
    if not re.match(r'^https?://', url, re.IGNORECASE):
        # Default to http:// for parsing purposes if no protocol is given
        url = 'http://' + url
    return url

def extract_features(url: str) -> dict:
    """
    Extracts 12 numeric/binary features from a URL for machine learning model consumption.
    Returns a dictionary of features.
    """
    cleaned = clean_url(url)
    if not cleaned:
        return {
            'url_length': 0,
            'hostname_length': 0,
            'is_ip': 0,
            'has_at_symbol': 0,
            'has_double_slash': 0,
            'has_hyphen_domain': 0,
            'dot_count': 0,
            'subdomain_count': 0,
            'is_shortened': 0,
            'has_https_in_domain': 0,
            'special_char_count': 0,
            'suspicious_keyword_count': 0
        }
    
    parsed = urlparse(cleaned)
    hostname = parsed.netloc
    path = parsed.path
    
    # 1. URL Length
    url_length = len(cleaned)
    
    # 2. Hostname Length
    hostname_length = len(hostname)
    
    # 3. IP Address in Hostname
    # Check for IPv4 (e.g. 192.168.1.1) or hex/octal representations
    ip_pattern = r'^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$'
    is_ip = 1 if re.match(ip_pattern, hostname) else 0
    
    # 4. Presence of "@" symbol in the URL
    has_at_symbol = 1 if '@' in cleaned else 0
    
    # 5. Presence of double slash "//" (redirection) in the path
    # If standard, the only double slash is the protocol identifier (http:// or https://)
    has_double_slash = 1 if '//' in cleaned[8:] else 0
    
    # 6. Presence of hyphen "-" in domain
    has_hyphen_domain = 1 if '-' in hostname else 0
    
    # 7. Number of Dots "." in URL
    dot_count = cleaned.count('.')
    
    # 8. Number of Subdomains
    # Split the hostname by dots and count. Subtract 1 or 2 for primary domain + TLD
    # e.g., 'www.google.com' has parts ['www', 'google', 'com'] -> subdomains: 'www'
    host_parts = hostname.split('.')
    # Filter empty strings (e.g. trailing dot)
    host_parts = [p for p in host_parts if p]
    if len(host_parts) > 2:
        subdomain_count = len(host_parts) - 2
        # Deduct 'www' if present since it's standard and not a typical phishing subdomain
        if 'www' in host_parts:
            subdomain_count = max(0, subdomain_count - 1)
    else:
        subdomain_count = 0
        
    # 9. Use of URL Shortener
    is_shortened = 1 if hostname.lower() in SHORTENERS else 0
    
    # 10. Presence of HTTPS token in the domain part
    has_https_in_domain = 1 if 'https' in hostname.lower() or 'http' in hostname.lower() else 0
    
    # 11. Count of Special Characters in entire URL (?, =, &, _, %, +)
    special_char_count = sum(cleaned.count(char) for char in ['?', '=', '&', '_', '%', '+'])
    
    # 12. Count of Suspicious Keywords in entire URL
    url_lower = cleaned.lower()
    suspicious_keyword_count = sum(1 for word in SUSPICIOUS_KEYWORDS if word in url_lower)
    
    return {
        'url_length': url_length,
        'hostname_length': hostname_length,
        'is_ip': is_ip,
        'has_at_symbol': has_at_symbol,
        'has_double_slash': has_double_slash,
        'has_hyphen_domain': has_hyphen_domain,
        'dot_count': dot_count,
        'subdomain_count': subdomain_count,
        'is_shortened': is_shortened,
        'has_https_in_domain': has_https_in_domain,
        'special_char_count': special_char_count,
        'suspicious_keyword_count': suspicious_keyword_count
    }

def get_feature_names() -> list:
    """
    Returns the ordered list of feature keys as used in extraction.
    """
    return [
        'url_length',
        'hostname_length',
        'is_ip',
        'has_at_symbol',
        'has_double_slash',
        'has_hyphen_domain',
        'dot_count',
        'subdomain_count',
        'is_shortened',
        'has_https_in_domain',
        'special_char_count',
        'suspicious_keyword_count'
    ]

def get_features_list(url: str) -> list:
    """
    Returns features as a flat list in standard order for model prediction.
    """
    feats = extract_features(url)
    return [feats[name] for name in get_feature_names()]
