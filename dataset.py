import pandas as pd
import numpy as np
import random
from features import extract_features

# Base safe domains for generating safe URLs
SAFE_DOMAINS = [
    'google.com', 'yahoo.com', 'microsoft.com', 'apple.com', 'wikipedia.org',
    'github.com', 'amazon.com', 'netflix.com', 'linkedin.com', 'twitter.com',
    'instagram.com', 'facebook.com', 'reddit.com', 'medium.com', 'stackoverflow.com',
    'nytimes.com', 'bbc.co.uk', 'cnn.com', 'forbes.com', 'zoom.us',
    'dropbox.com', 'spotify.com', 'adobe.com', 'oracle.com', 'salesforce.com',
    'cloudflare.com', 'imgur.com', 'pinterest.com', 'quora.com', 'tumblr.com',
    'ebay.com', 'walmart.com', 'target.com', 'craigslist.org', 'etsy.com',
    'imdb.com', 'behance.net', 'dribbble.com', 'vimeo.com', 'archive.org'
]

# Safe URL path templates
SAFE_PATHS = [
    '', '/', '/search', '/index.html', '/about', '/contact', '/help', '/faq',
    '/docs', '/wiki/Main_Page', '/posts/12345', '/feed', '/category/tech',
    '/products/item-9876', '/profile/user', '/settings', '/dashboard',
    '/blog/news/2026/05', '/download/app', '/support/ticket/new'
]

# Phishing-related words to simulate malicious patterns
PHISHING_WORDS = [
    'login', 'secure', 'verify', 'update', 'bank', 'signin', 'account',
    'webscr', 'cmd', 'security', 'wallet', 'confirm', 'bonus', 'free', 'gift',
    'paypal', 'netflix-secure', 'amazon-login', 'appleid-support', 'chase-verify'
]

# Shortening service templates
SHORTENED_DOMAINS = [
    'bit.ly', 'tinyurl.com', 'goo.gl', 'rebrand.ly', 't.co'
]

def generate_safe_urls(count=1000):
    urls = []
    for _ in range(count):
        domain = random.choice(SAFE_DOMAINS)
        path = random.choice(SAFE_PATHS)
        
        # Add optional query parameters to some safe URLs
        if path and random.random() > 0.6:
            query = f"?q={random.randint(100, 999)}&category={random.choice(['books', 'music', 'electronics'])}"
            url = f"https://{domain}{path}{query}"
        else:
            # Randomly use http or https (mostly https for safe)
            protocol = 'https://' if random.random() > 0.1 else 'http://'
            # Randomly add www.
            www = 'www.' if random.random() > 0.5 else ''
            url = f"{protocol}{www}{domain}{path}"
            
        urls.append(url)
    return urls

def generate_phishing_urls(count=1000):
    urls = []
    for _ in range(count):
        # Decide the phishing pattern type
        pattern_type = random.choice(['hyphen', 'subdomain', 'ip', 'shortener', 'keyword_stuffing'])
        
        if pattern_type == 'hyphen':
            # e.g., secure-paypal-login-update.com
            brand = random.choice(['paypal', 'amazon', 'netflix', 'chase', 'wells-fargo', 'appleid', 'microsoft'])
            keyword1 = random.choice(['login', 'secure', 'verify', 'update', 'signin', 'account'])
            keyword2 = random.choice(['help', 'support', 'portal', 'verification', 'billing'])
            domain = f"{keyword1}-{brand}-{keyword2}.{random.choice(['com', 'net', 'org', 'info', 'xyz'])}"
            url = f"http://{domain}/{random.choice(['index.php', 'signin.html', 'login'])}"
            
        elif pattern_type == 'subdomain':
            # e.g., login.paypal.com.verification-security.net
            brand = random.choice(['paypal', 'amazon', 'netflix', 'chase', 'google'])
            legit_looking = f"{brand}.com"
            fake_domain = f"verify-{random.choice(['secure', 'account', 'update'])}.{random.choice(['net', 'org', 'xyz', 'info'])}"
            url = f"https://{legit_looking}.{fake_domain}/login.html"
            
        elif pattern_type == 'ip':
            # e.g., http://192.168.1.105/login
            ip = f"{random.randint(1, 254)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 254)}"
            url = f"http://{ip}/{random.choice(['signin', 'secure', 'login', 'webscr'])}"
            
        elif pattern_type == 'shortener':
            # e.g., http://bit.ly/2Ks9Ad
            shortener = random.choice(SHORTENED_DOMAINS)
            code = ''.join(random.choices('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=6))
            url = f"http://{shortener}/{code}"
            
        elif pattern_type == 'keyword_stuffing':
            # e.g., http://login-paypal-security-update-verify-billing-webscr-cmd.com/secure
            words = random.sample(PHISHING_WORDS, k=random.randint(3, 5))
            domain = "-".join(words) + f".{random.choice(['com', 'net', 'xyz', 'info'])}"
            url = f"http://{domain}/{random.choice(['secure', 'verify', 'update'])}"
            
        # Randomly add extra suspicious paths or parameters to make it complex
        if random.random() > 0.5 and pattern_type != 'shortener':
            url += f"?ssl={random.randint(0, 1)}&email={random.choice(['user@gmail.com', 'test@yahoo.com'])}&session={random.randint(10000, 99999)}"
            
        # Randomly add double slash redirection
        if random.random() > 0.8 and pattern_type != 'shortener':
            # e.g., http://login-paypal.com//webscr
            url = url.replace('.com/', '.com//').replace('.net/', '.net//')
            
        urls.append(url)
    return urls

def build_dataset():
    print("Generating safe URLs...")
    safe_urls = generate_safe_urls(1000)
    
    print("Generating phishing URLs...")
    phishing_urls = generate_phishing_urls(1000)
    
    data = []
    
    print("Extracting features from safe URLs...")
    for url in safe_urls:
        features = extract_features(url)
        features['url'] = url
        features['label'] = 0  # 0 for Safe
        data.append(features)
        
    print("Extracting features from phishing URLs...")
    for url in phishing_urls:
        features = extract_features(url)
        features['url'] = url
        features['label'] = 1  # 1 for Phishing
        data.append(features)
        
    # Create DataFrame
    df = pd.DataFrame(data)
    
    # Shuffle dataset
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)
    
    # Save to CSV
    csv_path = 'urldata.csv'
    df.to_csv(csv_path, index=False)
    print(f"Dataset generated successfully! Saved {len(df)} rows to {csv_path}")

if __name__ == '__main__':
    build_dataset()
