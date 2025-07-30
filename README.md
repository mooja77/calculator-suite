# Calculator Suite

A SEO-optimized, mobile-first calculator suite built with Flask. Designed to capture organic traffic and monetize through ads/affiliates.

## Features

- **SEO-First Design**: Server-side rendering, optimized meta tags, schema markup
- **Mobile-First**: Responsive design with touch-friendly interfaces  
- **Performance Optimized**: Redis caching, lazy loading, sub-2 second load times
- **Modular Architecture**: Easy to add new calculators
- **Analytics Ready**: Google Analytics integration, calculation logging

## Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL 14+ (optional, defaults to SQLite)
- Redis 6+ (optional, caching disabled if not available)
- Node.js 18+ (for Tailwind CSS, optional)

### Installation

1. **Clone and setup virtual environment:**
```bash
git clone <repo-url>
cd calculator-suite
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Environment setup:**
```bash
cp .env.example .env
# Edit .env with your values
```

4. **Run development server:**
```bash
python run_dev.py
```

The app will be available at http://localhost:5000

## Available Calculators

- **Percentage Calculator** (`/calculators/percentage/`):
  - Basic percentage calculation
  - Percentage increase/decrease
  - Percentage difference
  - Percentage change
  - Find percentage value

## Project Structure

```
calculator-suite/
├── app/
│   ├── calculators/         # Calculator modules
│   │   ├── base.py         # Base calculator class
│   │   ├── percentage.py   # Percentage calculator
│   │   └── registry.py     # Calculator registry
│   ├── seo/                # SEO utilities
│   │   ├── meta.py        # Meta tag generation
│   │   ├── schema.py      # Schema.org markup
│   │   └── sitemap.py     # Dynamic sitemap
│   ├── templates/         # Jinja2 templates
│   ├── static/           # CSS, JS, images
│   ├── content/          # Markdown content files
│   ├── models.py         # Database models
│   ├── cache.py          # Redis caching
│   └── routes.py         # URL routes
├── requirements.txt
└── run_dev.py           # Development server
```

## Adding New Calculators

1. **Create calculator class:**
```python
# app/calculators/mycalc.py
from .base import BaseCalculator
from .registry import register_calculator

@register_calculator
class MyCalculator(BaseCalculator):
    def calculate(self, inputs):
        # Implementation
        pass
    
    def validate_inputs(self, inputs):
        # Validation logic
        pass
    
    def get_meta_data(self):
        return {
            'title': 'My Calculator - Description',
            'description': 'Calculator description...',
            'keywords': 'relevant, keywords',
            'canonical': '/calculators/my/'
        }
    
    def get_schema_markup(self):
        # Schema.org markup
        pass
```

2. **Import in app/__init__.py:**
```python
from app.calculators import mycalc
```

3. **Create content files:**
- `app/content/my_intro.md`
- `app/content/my_guide.md`
- `app/content/my_faq.md`

## Configuration

### Environment Variables

- `FLASK_APP`: Application entry point (default: app.py)
- `FLASK_ENV`: Environment (development/production)
- `SECRET_KEY`: Flask secret key
- `DATABASE_URL`: Database connection string
- `REDIS_URL`: Redis connection string
- `GA_TRACKING_ID`: Google Analytics tracking ID
- `ADSENSE_CLIENT`: Google AdSense client ID

### Database Setup

**SQLite (default):**
No additional setup required.

**PostgreSQL:**
```bash
createdb calculator_suite
# Update DATABASE_URL in .env
```

**Redis (optional):**
```bash
# Install and start Redis
redis-server
```

## Production Deployment

### 1. Install production dependencies:
```bash
pip install gunicorn
```

### 2. Set environment variables:
```bash
export FLASK_ENV=production
export SECRET_KEY=your-production-secret
export DATABASE_URL=postgresql://user:pass@host/db
```

### 3. Run with Gunicorn:
```bash
gunicorn app:app -w 4 -b 0.0.0.0:8000
```

### 4. Nginx configuration:
See `nginx.conf` for production setup with SSL, compression, and caching.

## SEO Features

- **Server-side rendering** for perfect crawlability
- **Dynamic meta tags** with Open Graph and Twitter Cards
- **Schema.org markup** for rich snippets
- **XML sitemap** at `/sitemap.xml`
- **Robots.txt** at `/robots.txt`
- **Mobile-first responsive design**
- **Page speed optimization** (< 2 second load times)

## Performance Features

- **Redis caching** for pages and calculations
- **Database query optimization**
- **Lazy loading** for below-the-fold content
- **Minified assets** and compression
- **CDN-ready** static asset serving

## Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=app
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new calculators
4. Ensure all tests pass
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Support

For issues and questions:
- Open an issue on GitHub
- Check the documentation in `/Docs/`

---

Built with ❤️ for helping people with everyday calculations.