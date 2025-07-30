from flask import Blueprint, render_template, request, jsonify, abort, current_app, Response
from flask_wtf.csrf import validate_csrf, ValidationError
from app.calculators.registry import calculator_registry
from app.seo.meta import generate_meta_tags
from app.seo.sitemap import generate_sitemap, generate_robots_txt
from app.cache import cache_page
from app.content import get_content_blocks
from app.models import CalculationLog, db
from app.security import sanitize_html, validate_json_input, validate_user_agent
from app import limiter
import time
import json

main = Blueprint('main', __name__)

@main.route('/')
@cache_page(3600)
def index():
    """Homepage with calculator directory"""
    meta_data = {
        'title': 'Free Online Calculators - Fast & Accurate Math Tools',
        'description': 'Access our collection of free online calculators for percentage, BMI, tips, loans, and more. Fast, accurate, and mobile-friendly.',
        'keywords': 'calculator, online calculator, percentage calculator, BMI calculator, tip calculator',
        'canonical': '/'
    }
    
    calculators = calculator_registry.get_all()
    
    return render_template(
        'index.html',
        meta_tags=sanitize_html(generate_meta_tags(meta_data)),
        calculators=calculators
    )

@main.route('/calculators/<calculator_slug>/')
@cache_page(3600)
def calculator_page(calculator_slug):
    """Render calculator page with full SEO optimization"""
    
    # Get calculator instance
    calc_class = calculator_registry.get(calculator_slug)
    if not calc_class:
        abort(404)
    
    calculator = calc_class()
    
    # Performance timing
    start_time = time.time()
    
    # Get all page data
    meta_data = calculator.get_meta_data()
    schema_markup = calculator.get_schema_markup()
    content_blocks = get_content_blocks(calculator.get_content_blocks())
    
    # Render time tracking
    render_time = time.time() - start_time
    
    # Sanitize content blocks
    safe_content_blocks = []
    for block in content_blocks:
        safe_block = {
            'id': block['id'],
            'title': block['title'],
            'content': sanitize_html(block['content'])
        }
        safe_content_blocks.append(safe_block)
    
    return render_template(
        'calculator.html',
        calculator=calculator,
        meta_tags=sanitize_html(generate_meta_tags(meta_data)),
        schema_markup=schema_markup,
        content_blocks=safe_content_blocks,
        render_time=render_time,
        calculator_slug=calculator_slug
    )

@main.route('/api/calculate/<calculator_slug>', methods=['POST'])
@limiter.limit("30/minute")  # Rate limit API calls
def calculate_api(calculator_slug):
    """API endpoint for calculations"""
    
    # Validate user agent
    user_agent = request.headers.get('User-Agent', '')
    if not validate_user_agent(user_agent):
        return jsonify({'error': 'Invalid request'}), 400
    
    # CSRF Protection
    try:
        validate_csrf(request.headers.get('X-CSRFToken'))
    except ValidationError:
        return jsonify({'error': 'CSRF token missing or invalid'}), 403
    
    # Get calculator
    calc_class = calculator_registry.get(calculator_slug)
    if not calc_class:
        return jsonify({'error': 'Calculator not found'}), 404
    
    calculator = calc_class()
    
    # Validate and sanitize JSON input
    raw_inputs = request.get_json()
    if not raw_inputs:
        return jsonify({'error': 'No data provided'}), 400
    
    valid, sanitized_inputs = validate_json_input(raw_inputs)
    if not valid:
        return jsonify({'errors': sanitized_inputs}), 400
    
    # Validate inputs with calculator
    if not calculator.validate_inputs(sanitized_inputs):
        return jsonify({'errors': calculator.errors}), 400
    
    try:
        result = calculator.calculate(sanitized_inputs)
        
        # Log calculation for analytics (with sanitized data)
        log_calculation(calculator_slug, sanitized_inputs, result, request)
        
        return jsonify(result)
    except Exception as e:
        current_app.logger.error(f"Calculation error: {str(e)}")
        return jsonify({'error': 'Calculation failed'}), 500

@main.route('/sitemap.xml')
@cache_page(86400)  # Cache for 24 hours
def sitemap():
    """Generate XML sitemap"""
    calculators = calculator_registry.get_all()
    sitemap_xml = generate_sitemap(calculators)
    
    return Response(sitemap_xml, mimetype='application/xml')

@main.route('/robots.txt')
@cache_page(86400)  # Cache for 24 hours
def robots():
    """Generate robots.txt"""
    robots_content = generate_robots_txt()
    
    return Response(robots_content, mimetype='text/plain')

def log_calculation(calculator_type, inputs, result, request_obj):
    """Log calculation for analytics"""
    try:
        log = CalculationLog(
            calculator_type=calculator_type,
            inputs=json.dumps(inputs),
            result=json.dumps(result),
            user_ip=request_obj.remote_addr,
            user_agent=request_obj.user_agent.string
        )
        db.session.add(log)
        db.session.commit()
    except:
        pass  # Don't let logging errors break the calculation