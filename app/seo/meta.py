from flask import request, url_for

def generate_meta_tags(meta_data):
    """Generate SEO meta tags from metadata dictionary"""
    
    # Get current URL for canonical
    canonical_url = meta_data.get('canonical', request.path)
    if not canonical_url.startswith('http'):
        canonical_url = request.host_url.rstrip('/') + canonical_url
    
    # Build meta tags HTML
    meta_html = f'''
    <title>{meta_data.get('title', 'Calculator')}</title>
    <meta name="description" content="{meta_data.get('description', '')}" />
    <meta name="keywords" content="{meta_data.get('keywords', '')}" />
    <link rel="canonical" href="{canonical_url}" />
    
    <!-- Open Graph meta tags -->
    <meta property="og:title" content="{meta_data.get('title', 'Calculator')}" />
    <meta property="og:description" content="{meta_data.get('description', '')}" />
    <meta property="og:url" content="{canonical_url}" />
    <meta property="og:type" content="website" />
    <meta property="og:site_name" content="Calculator Suite" />
    
    <!-- Twitter Card meta tags -->
    <meta name="twitter:card" content="summary" />
    <meta name="twitter:title" content="{meta_data.get('title', 'Calculator')}" />
    <meta name="twitter:description" content="{meta_data.get('description', '')}" />
    
    <!-- Additional SEO meta tags -->
    <meta name="robots" content="index, follow" />
    <meta name="googlebot" content="index, follow" />
    <meta name="author" content="Calculator Suite" />
    '''
    
    return meta_html.strip()