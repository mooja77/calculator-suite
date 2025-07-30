"""
Health check endpoints for global infrastructure monitoring.
"""
from flask import Blueprint, jsonify
import logging
from datetime import datetime

from app.utils.error_handling import health_checker
from app import redis_client

logger = logging.getLogger(__name__)

health_api = Blueprint('health_api', __name__, url_prefix='/api/v1/health')

@health_api.route('/', methods=['GET'])
def overall_health():
    """Overall system health check."""
    try:
        # Check all services
        currency_health = health_checker.check_currency_service()
        localization_health = health_checker.check_localization_service()
        database_health = health_checker.check_database_health()
        
        # Check Redis
        redis_health = {'healthy': False}
        if redis_client:
            try:
                redis_client.ping()
                redis_health = {'healthy': True, 'available': True}
            except Exception as e:
                redis_health = {'healthy': False, 'error': str(e)}
        else:
            redis_health = {'healthy': False, 'error': 'Redis not configured'}
        
        # Determine overall health
        all_healthy = all([
            currency_health['healthy'],
            localization_health['healthy'],
            database_health['healthy'],
            redis_health['healthy']
        ])
        
        response = {
            'healthy': all_healthy,
            'timestamp': datetime.utcnow().isoformat(),
            'services': {
                'currency': currency_health,
                'localization': localization_health,
                'database': database_health,
                'redis': redis_health
            }
        }
        
        status_code = 200 if all_healthy else 503
        return jsonify(response), status_code
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            'healthy': False,
            'error': 'Health check failed',
            'timestamp': datetime.utcnow().isoformat()
        }), 500

@health_api.route('/currency', methods=['GET'])
def currency_health():
    """Currency service health check."""
    try:
        health = health_checker.check_currency_service()
        status_code = 200 if health['healthy'] else 503
        return jsonify(health), status_code
    except Exception as e:
        logger.error(f"Currency health check failed: {e}")
        return jsonify({
            'healthy': False,
            'error': str(e)
        }), 500

@health_api.route('/localization', methods=['GET'])
def localization_health():
    """Localization service health check."""
    try:
        health = health_checker.check_localization_service()
        status_code = 200 if health['healthy'] else 503
        return jsonify(health), status_code
    except Exception as e:
        logger.error(f"Localization health check failed: {e}")
        return jsonify({
            'healthy': False,
            'error': str(e)
        }), 500

@health_api.route('/database', methods=['GET'])
def database_health():
    """Database health check."""
    try:
        health = health_checker.check_database_health()
        status_code = 200 if health['healthy'] else 503
        return jsonify(health), status_code
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return jsonify({
            'healthy': False,
            'error': str(e)
        }), 500

@health_api.route('/redis', methods=['GET'])
def redis_health():
    """Redis cache health check."""
    try:
        if redis_client:
            redis_client.ping()
            return jsonify({
                'healthy': True,
                'available': True,
                'timestamp': datetime.utcnow().isoformat()
            })
        else:
            return jsonify({
                'healthy': False,
                'available': False,
                'error': 'Redis not configured'
            }), 503
    except Exception as e:
        logger.error(f"Redis health check failed: {e}")
        return jsonify({
            'healthy': False,
            'available': False,
            'error': str(e)
        }), 503