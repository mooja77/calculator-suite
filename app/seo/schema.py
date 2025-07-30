from flask import request
import json

def generate_calculator_schema(calculator):
    """Generate schema.org markup for calculator pages"""
    
    base_url = request.host_url.rstrip('/')
    calculator_url = f"{base_url}/calculators/{calculator.slug}/"
    
    schema = {
        "@context": "https://schema.org",
        "@type": "WebApplication",
        "name": calculator.get_meta_data().get('title', f"{calculator.slug.title()} Calculator"),
        "description": calculator.get_meta_data().get('description', ''),
        "url": calculator_url,
        "applicationCategory": "UtilityApplication",
        "operatingSystem": "Any",
        "browserRequirements": "Requires JavaScript",
        "offers": {
            "@type": "Offer",
            "price": "0",
            "priceCurrency": "USD"
        },
        "creator": {
            "@type": "Organization",
            "name": "Calculator Suite"
        }
    }
    
    return schema

def generate_website_schema():
    """Generate schema.org markup for the main website"""
    
    base_url = request.host_url.rstrip('/')
    
    schema = {
        "@context": "https://schema.org",
        "@type": "WebSite",
        "name": "Calculator Suite",
        "description": "Free online calculators for percentage, BMI, tips, loans, and more",
        "url": base_url,
        "potentialAction": {
            "@type": "SearchAction",
            "target": f"{base_url}/search?q={{search_term_string}}",
            "query-input": "required name=search_term_string"
        }
    }
    
    return schema

def generate_breadcrumb_schema(breadcrumbs):
    """Generate breadcrumb schema markup"""
    
    base_url = request.host_url.rstrip('/')
    
    items = []
    for i, (name, url) in enumerate(breadcrumbs, 1):
        if not url.startswith('http'):
            url = base_url + url
        
        items.append({
            "@type": "ListItem",
            "position": i,
            "name": name,
            "item": url
        })
    
    schema = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": items
    }
    
    return schema