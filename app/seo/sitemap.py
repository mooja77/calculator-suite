from flask import url_for, request
from datetime import datetime
import xml.etree.ElementTree as ET

def generate_sitemap(calculators):
    """Generate XML sitemap for the site"""
    
    base_url = request.host_url.rstrip('/')
    
    # Create root element
    urlset = ET.Element('urlset')
    urlset.set('xmlns', 'http://www.sitemaps.org/schemas/sitemap/0.9')
    
    # Homepage
    url_elem = ET.SubElement(urlset, 'url')
    ET.SubElement(url_elem, 'loc').text = base_url + '/'
    ET.SubElement(url_elem, 'changefreq').text = 'weekly'
    ET.SubElement(url_elem, 'priority').text = '1.0'
    ET.SubElement(url_elem, 'lastmod').text = datetime.now().strftime('%Y-%m-%d')
    
    # Calculator pages
    for calc_class in calculators.values():
        calculator = calc_class()
        url_elem = ET.SubElement(urlset, 'url')
        ET.SubElement(url_elem, 'loc').text = f"{base_url}/calculators/{calculator.slug}/"
        ET.SubElement(url_elem, 'changefreq').text = 'monthly'
        ET.SubElement(url_elem, 'priority').text = '0.8'
        ET.SubElement(url_elem, 'lastmod').text = datetime.now().strftime('%Y-%m-%d')
    
    # Convert to string
    return ET.tostring(urlset, encoding='unicode', method='xml')

def generate_robots_txt():
    """Generate robots.txt content"""
    
    base_url = request.host_url.rstrip('/')
    
    robots_content = f"""User-agent: *
Allow: /

# Sitemap
Sitemap: {base_url}/sitemap.xml

# Block admin and API endpoints
Disallow: /admin/
Disallow: /api/
"""
    
    return robots_content.strip()