"""
SEO-friendly URL routing for internationalization
Handles language-specific URL patterns
"""
from flask import Blueprint, render_template, g, request, redirect, url_for
from app.calculators.registry import calculator_registry
from app.services.i18n import i18n_service

# Create blueprint with language code support
i18n_routes = Blueprint(
    'i18n_routes', 
    __name__, 
    url_prefix='/<language_code>'
)

@i18n_routes.url_defaults
def add_language_code(endpoint, values):
    """Add language code to URL generation."""
    if 'language_code' not in values and hasattr(g, 'language_code'):
        values['language_code'] = g.language_code

@i18n_routes.url_value_preprocessor
def pull_lang_code(endpoint, values):
    """Extract and validate language code from URL."""
    if values is not None:
        language_code = values.pop('language_code', 'en')
        
        # Validate language code
        if not i18n_service._is_language_supported(language_code):
            # Redirect to supported language
            return redirect(url_for(endpoint, language_code='en', **values))
        
        g.language_code = language_code

# Language-specific home page
@i18n_routes.route('/')
def home():
    """Localized home page."""
    try:
        # Get featured calculators
        featured_calculators = [
            calculator_registry.get_calculator('percentage'),
            calculator_registry.get_calculator('retirement401k'),
            calculator_registry.get_calculator('studentloan'),
            calculator_registry.get_calculator('paycheck')
        ]
        
        # Filter out None values
        featured_calculators = [calc for calc in featured_calculators if calc is not None]
        
        return render_template(
            'index.html',
            featured_calculators=featured_calculators,
            page_title=g.translations.get('calculators', {}).get('title', 'Calculator Suite'),
            meta_description=g.translations.get('calculators', {}).get('description', 'Professional calculators for all your needs')
        )
        
    except Exception as e:
        logger.error(f"Error rendering localized home page: {e}")
        return render_template('index.html')

# Language-specific calculator pages
@i18n_routes.route('/calculators/<calculator_name>')
def calculator_page(calculator_name):
    """Localized calculator page."""
    try:
        # Get calculator from registry
        calculator = calculator_registry.get_calculator(calculator_name)
        
        if not calculator:
            return redirect(url_for('i18n_routes.calculators_list'))
        
        # Get localized calculator info
        calc_translations = g.translations.get('calculators', {}).get(calculator_name, {})
        
        return render_template(
            f'calculators/{calculator_name}.html',
            calculator=calculator,
            calculator_translations=calc_translations,
            page_title=calc_translations.get('title', calculator.name),
            meta_description=calc_translations.get('description', calculator.description)
        )
        
    except Exception as e:
        logger.error(f"Error rendering calculator page {calculator_name}: {e}")
        return redirect(url_for('i18n_routes.calculators_list'))

# Language-specific calculators list
@i18n_routes.route('/calculators')
def calculators_list():
    """Localized calculators list page."""
    try:
        # Get all calculators
        calculators = calculator_registry.get_all_calculators()
        
        # Group calculators by category
        categorized_calculators = {
            'financial': [],
            'everyday': [],
            'islamic': []
        }
        
        for calc_name, calculator in calculators.items():
            category = getattr(calculator, 'category', 'everyday')
            if calc_name in ['zakat', 'takaful', 'murabaha']:
                category = 'islamic'
            
            calc_translations = g.translations.get('calculators', {}).get(calc_name, {})
            calculator_info = {
                'name': calc_name,
                'calculator': calculator,
                'title': calc_translations.get('title', calculator.name),
                'description': calc_translations.get('description', calculator.description)
            }
            
            categorized_calculators[category].append(calculator_info)
        
        return render_template(
            'calculators_list.html',
            categorized_calculators=categorized_calculators,
            page_title=g.translations.get('navigation', {}).get('all_calculators', 'All Calculators'),
            meta_description=g.translations.get('calculators', {}).get('description', 'Complete list of financial and everyday calculators')
        )
        
    except Exception as e:
        logger.error(f"Error rendering calculators list: {e}")
        return render_template('calculators_list.html')

# Language-specific guides
@i18n_routes.route('/guides')
def guides():
    """Localized guides page."""
    try:
        return render_template(
            'guides.html',
            page_title=g.translations.get('navigation', {}).get('guides', 'Guides'),
            meta_description=g.translations.get('content', {}).get('how_to_use', 'Learn how to use our calculators effectively')
        )
        
    except Exception as e:
        logger.error(f"Error rendering guides page: {e}")
        return render_template('guides.html')

# Language-specific guide for specific calculator
@i18n_routes.route('/guides/<calculator_name>')
def calculator_guide(calculator_name):
    """Localized calculator guide page."""
    try:
        # Get calculator from registry
        calculator = calculator_registry.get_calculator(calculator_name)
        
        if not calculator:
            return redirect(url_for('i18n_routes.guides'))
        
        # Get localized calculator info
        calc_translations = g.translations.get('calculators', {}).get(calculator_name, {})
        
        return render_template(
            f'guides/{calculator_name}.html',
            calculator=calculator,
            calculator_translations=calc_translations,
            page_title=f"{calc_translations.get('title', calculator.name)} - {g.translations.get('navigation', {}).get('guides', 'Guide')}",
            meta_description=f"Complete guide for {calc_translations.get('title', calculator.name)}"
        )
        
    except Exception as e:
        logger.error(f"Error rendering calculator guide {calculator_name}: {e}")
        return redirect(url_for('i18n_routes.guides'))

# Islamic finance section (Arabic-optimized)
@i18n_routes.route('/islamic-finance')
def islamic_finance():
    """Islamic finance calculators page with Arabic support."""
    try:
        # Get Islamic finance calculators
        islamic_calculators = ['zakat', 'takaful', 'murabaha']
        calculators_info = []
        
        for calc_name in islamic_calculators:
            calculator = calculator_registry.get_calculator(calc_name)
            if calculator:
                calc_translations = g.translations.get('calculators', {}).get(calc_name, {})
                calculators_info.append({
                    'name': calc_name,
                    'calculator': calculator,
                    'title': calc_translations.get('title', calculator.name),
                    'description': calc_translations.get('description', calculator.description)
                })
        
        # Get Islamic finance terms
        islamic_terms = i18n_service.get_islamic_finance_terms(g.language_code)
        
        return render_template(
            'islamic_finance.html',
            calculators=calculators_info,
            islamic_terms=islamic_terms,
            page_title=g.translations.get('islamic_finance', {}).get('title', 'Islamic Finance'),
            meta_description=g.translations.get('islamic_finance', {}).get('subtitle', 'Sharia-compliant financial calculations')
        )
        
    except Exception as e:
        logger.error(f"Error rendering Islamic finance page: {e}")
        return render_template('islamic_finance.html')

# Sitemap for language-specific URLs
@i18n_routes.route('/sitemap.xml')
def sitemap():
    """Generate sitemap for language-specific URLs."""
    from flask import Response
    import xml.etree.ElementTree as ET
    from datetime import datetime
    
    try:
        # Create sitemap root
        urlset = ET.Element('urlset')
        urlset.set('xmlns', 'http://www.sitemaps.org/schemas/sitemap/0.9')
        urlset.set('xmlns:xhtml', 'http://www.w3.org/1999/xhtml')
        
        base_url = request.url_root.rstrip('/')
        current_date = datetime.now().strftime('%Y-%m-%d')
        
        # Add language-specific URLs
        urls = [
            ('i18n_routes.home', 1.0, 'daily'),
            ('i18n_routes.calculators_list', 0.9, 'daily'),
            ('i18n_routes.guides', 0.7, 'weekly'),
            ('i18n_routes.islamic_finance', 0.8, 'weekly')
        ]
        
        # Add calculator pages
        for calc_name in calculator_registry.get_all_calculators().keys():
            urls.append((f'i18n_routes.calculator_page', 0.8, 'weekly', {'calculator_name': calc_name}))
            urls.append((f'i18n_routes.calculator_guide', 0.6, 'weekly', {'calculator_name': calc_name}))
        
        for endpoint, priority, changefreq, kwargs in urls:
            url_elem = ET.SubElement(urlset, 'url')
            
            # Main URL
            loc = ET.SubElement(url_elem, 'loc')
            if kwargs:
                loc.text = base_url + url_for(endpoint, language_code=g.language_code, **kwargs)
            else:
                loc.text = base_url + url_for(endpoint, language_code=g.language_code)
            
            # Metadata
            lastmod = ET.SubElement(url_elem, 'lastmod')
            lastmod.text = current_date
            
            priority_elem = ET.SubElement(url_elem, 'priority')
            priority_elem.text = str(priority)
            
            changefreq_elem = ET.SubElement(url_elem, 'changefreq')
            changefreq_elem.text = changefreq
            
            # Add alternate language links
            for lang_code in i18n_service.SUPPORTED_LANGUAGES.keys():
                if lang_code != g.language_code:
                    xhtml_link = ET.SubElement(url_elem, '{http://www.w3.org/1999/xhtml}link')
                    xhtml_link.set('rel', 'alternate')
                    xhtml_link.set('hreflang', lang_code)
                    if kwargs:
                        xhtml_link.set('href', base_url + url_for(endpoint, language_code=lang_code, **kwargs))
                    else:
                        xhtml_link.set('href', base_url + url_for(endpoint, language_code=lang_code))
        
        # Generate XML
        xml_str = ET.tostring(urlset, encoding='unicode', method='xml')
        xml_declaration = '<?xml version="1.0" encoding="UTF-8"?>\n'
        
        return Response(
            xml_declaration + xml_str,
            mimetype='application/xml',
            headers={'Cache-Control': 'public, max-age=3600'}
        )
        
    except Exception as e:
        logger.error(f"Error generating sitemap: {e}")
        return Response('Error generating sitemap', status=500)