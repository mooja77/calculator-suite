// Enhanced Calculator JavaScript with UX improvements

// Utility functions
const utils = {
  // Format number with commas and decimals
  formatNumber(value, decimals = 2) {
    const num = parseFloat(value);
    if (isNaN(num)) return '0';
    
    return new Intl.NumberFormat('en-US', {
      minimumFractionDigits: decimals,
      maximumFractionDigits: decimals
    }).format(num);
  },

  // Format currency
  formatCurrency(value, currency = 'USD') {
    const num = parseFloat(value);
    if (isNaN(num)) return '$0.00';
    
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: currency
    }).format(num);
  },

  // Format percentage
  formatPercent(value, decimals = 2) {
    const num = parseFloat(value);
    if (isNaN(num)) return '0%';
    
    return new Intl.NumberFormat('en-US', {
      style: 'percent',
      minimumFractionDigits: decimals,
      maximumFractionDigits: decimals
    }).format(num / 100);
  },

  // Debounce function for real-time calculations
  debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
      const later = () => {
        clearTimeout(timeout);
        func(...args);
      };
      clearTimeout(timeout);
      timeout = setTimeout(later, wait);
    };
  },

  // Smooth scroll to element
  scrollToElement(element, offset = 100) {
    const y = element.getBoundingClientRect().top + window.pageYOffset - offset;
    window.scrollTo({ top: y, behavior: 'smooth' });
  },

  // Copy to clipboard with feedback
  async copyToClipboard(text, button) {
    try {
      await navigator.clipboard.writeText(text);
      const originalText = button.textContent;
      button.textContent = 'Copied!';
      button.classList.add('btn--success');
      
      setTimeout(() => {
        button.textContent = originalText;
        button.classList.remove('btn--success');
      }, 2000);
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  }
};

// Form validation
class FormValidator {
  constructor(form) {
    this.form = form;
    this.fields = form.querySelectorAll('[required]');
    this.errors = {};
    
    this.initValidation();
  }

  initValidation() {
    this.fields.forEach(field => {
      field.addEventListener('blur', () => this.validateField(field));
      field.addEventListener('input', () => {
        if (this.errors[field.name]) {
          this.validateField(field);
        }
      });
    });
  }

  validateField(field) {
    const value = field.value.trim();
    const name = field.name;
    let error = null;

    // Required validation
    if (!value) {
      error = 'This field is required';
    }
    
    // Type-specific validation
    if (value && field.type === 'number') {
      const num = parseFloat(value);
      const min = parseFloat(field.min);
      const max = parseFloat(field.max);
      
      if (isNaN(num)) {
        error = 'Please enter a valid number';
      } else if (!isNaN(min) && num < min) {
        error = `Value must be at least ${min}`;
      } else if (!isNaN(max) && num > max) {
        error = `Value must be at most ${max}`;
      }
    }

    // Email validation
    if (value && field.type === 'email') {
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!emailRegex.test(value)) {
        error = 'Please enter a valid email address';
      }
    }

    this.setFieldError(field, error);
    return !error;
  }

  setFieldError(field, error) {
    const wrapper = field.closest('.form-group');
    const errorElement = wrapper.querySelector('.form-error');
    
    if (error) {
      this.errors[field.name] = error;
      field.classList.add('form-input--error');
      field.setAttribute('aria-invalid', 'true');
      
      if (errorElement) {
        errorElement.textContent = error;
        errorElement.style.display = 'block';
      }
    } else {
      delete this.errors[field.name];
      field.classList.remove('form-input--error');
      field.setAttribute('aria-invalid', 'false');
      
      if (errorElement) {
        errorElement.textContent = '';
        errorElement.style.display = 'none';
      }
    }
  }

  isValid() {
    let valid = true;
    this.fields.forEach(field => {
      if (!this.validateField(field)) {
        valid = false;
      }
    });
    return valid;
  }
}

// Input formatting
class InputFormatter {
  constructor(input, options = {}) {
    this.input = input;
    this.options = options;
    this.previousValue = '';
    
    this.init();
  }

  init() {
    this.input.addEventListener('input', (e) => this.format(e));
    this.input.addEventListener('focus', () => this.onFocus());
    this.input.addEventListener('blur', () => this.onBlur());
  }

  format(e) {
    let value = this.input.value.replace(/[^\d.-]/g, '');
    
    if (this.options.type === 'currency') {
      value = this.formatCurrency(value);
    } else if (this.options.type === 'percentage') {
      value = this.formatPercentage(value);
    } else if (this.options.type === 'number') {
      value = this.formatNumber(value);
    }
    
    this.input.value = value;
    this.previousValue = value;
  }

  formatCurrency(value) {
    const number = parseFloat(value.replace(/,/g, ''));
    if (isNaN(number)) return '';
    
    return utils.formatNumber(number, 2);
  }

  formatPercentage(value) {
    let number = parseFloat(value);
    if (isNaN(number)) return '';
    
    // Limit to 100%
    if (this.options.max && number > this.options.max) {
      number = this.options.max;
    }
    
    return number.toString();
  }

  formatNumber(value) {
    const number = parseFloat(value.replace(/,/g, ''));
    if (isNaN(number)) return '';
    
    return utils.formatNumber(number, this.options.decimals || 0);
  }

  onFocus() {
    // Remove formatting on focus for easier editing
    const value = this.input.value.replace(/[^\d.-]/g, '');
    this.input.value = value;
  }

  onBlur() {
    // Reapply formatting on blur
    this.format();
  }
}

// Real-time calculator
class RealtimeCalculator {
  constructor(form, calculateFn) {
    this.form = form;
    this.calculateFn = calculateFn;
    this.inputs = form.querySelectorAll('input, select');
    this.resultContainer = document.getElementById('result-container');
    
    this.init();
  }

  init() {
    // Debounced calculation
    const calculate = utils.debounce(() => this.calculate(), 300);
    
    this.inputs.forEach(input => {
      input.addEventListener('input', calculate);
      input.addEventListener('change', calculate);
    });
    
    // Initial calculation
    this.calculate();
  }

  async calculate() {
    const data = this.getFormData();
    
    // Show calculating state
    this.showCalculating();
    
    try {
      const result = await this.calculateFn(data);
      this.showResult(result);
    } catch (error) {
      this.showError(error.message);
    }
  }

  getFormData() {
    const data = {};
    const formData = new FormData(this.form);
    
    for (let [key, value] of formData.entries()) {
      // Remove formatting from numbers
      if (value && typeof value === 'string') {
        const cleaned = value.replace(/[^\d.-]/g, '');
        const num = parseFloat(cleaned);
        data[key] = isNaN(num) ? value : num;
      } else {
        data[key] = value;
      }
    }
    
    return data;
  }

  showCalculating() {
    if (this.resultContainer) {
      this.resultContainer.innerHTML = `
        <div class="result-loading">
          <div class="spinner spinner--sm"></div>
          <span>Calculating...</span>
        </div>
      `;
    }
  }

  showResult(result) {
    if (this.resultContainer) {
      this.resultContainer.innerHTML = result;
      this.resultContainer.style.display = 'block';
      
      // Animate result
      this.resultContainer.classList.add('fade-in-up');
      
      // Initialize any charts or interactive elements
      this.initResultFeatures();
    }
  }

  showError(message) {
    if (this.resultContainer) {
      this.resultContainer.innerHTML = `
        <div class="alert alert--error">
          <div class="alert__content">
            <div class="alert__title">Calculation Error</div>
            <p>${message}</p>
          </div>
        </div>
      `;
    }
  }

  initResultFeatures() {
    // Initialize tooltips
    this.initTooltips();
    
    // Initialize copy buttons
    this.initCopyButtons();
    
    // Initialize charts if present
    this.initCharts();
  }

  initTooltips() {
    // Tooltip initialization logic
  }

  initCopyButtons() {
    const copyButtons = this.resultContainer.querySelectorAll('[data-copy]');
    copyButtons.forEach(button => {
      button.addEventListener('click', () => {
        const target = button.dataset.copy;
        const element = document.querySelector(target);
        if (element) {
          utils.copyToClipboard(element.textContent, button);
        }
      });
    });
  }

  initCharts() {
    const chartElements = this.resultContainer.querySelectorAll('[data-chart]');
    chartElements.forEach(element => {
      const type = element.dataset.chartType;
      const data = JSON.parse(element.dataset.chartData);
      
      // Initialize chart based on type
      if (window.Chart) {
        new ChartRenderer(element, type, data);
      }
    });
  }
}

// Chart renderer
class ChartRenderer {
  constructor(canvas, type, data) {
    this.canvas = canvas;
    this.type = type;
    this.data = data;
    
    this.render();
  }

  render() {
    const ctx = this.canvas.getContext('2d');
    const config = this.getConfig();
    
    new Chart(ctx, config);
  }

  getConfig() {
    const configs = {
      pie: this.getPieConfig(),
      bar: this.getBarConfig(),
      line: this.getLineConfig()
    };
    
    return configs[this.type] || configs.pie;
  }

  getPieConfig() {
    return {
      type: 'doughnut',
      data: this.data,
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'bottom',
            labels: {
              padding: 20,
              usePointStyle: true,
              font: {
                size: 14
              }
            }
          },
          tooltip: {
            callbacks: {
              label: (context) => {
                const label = context.label || '';
                const value = utils.formatCurrency(context.parsed);
                const percentage = Math.round(context.parsed / context.dataset.data.reduce((a, b) => a + b, 0) * 100);
                return `${label}: ${value} (${percentage}%)`;
              }
            }
          }
        }
      }
    };
  }

  getBarConfig() {
    return {
      type: 'bar',
      data: this.data,
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          y: {
            beginAtZero: true,
            ticks: {
              callback: (value) => utils.formatCurrency(value)
            }
          }
        },
        plugins: {
          legend: {
            display: false
          },
          tooltip: {
            callbacks: {
              label: (context) => utils.formatCurrency(context.parsed.y)
            }
          }
        }
      }
    };
  }

  getLineConfig() {
    return {
      type: 'line',
      data: this.data,
      options: {
        responsive: true,
        maintainAspectRatio: false,
        interaction: {
          mode: 'index',
          intersect: false
        },
        scales: {
          y: {
            beginAtZero: true,
            ticks: {
              callback: (value) => utils.formatCurrency(value)
            }
          }
        },
        plugins: {
          legend: {
            position: 'bottom',
            labels: {
              padding: 20,
              usePointStyle: true
            }
          },
          tooltip: {
            callbacks: {
              label: (context) => {
                const label = context.dataset.label || '';
                const value = utils.formatCurrency(context.parsed.y);
                return `${label}: ${value}`;
              }
            }
          }
        }
      }
    };
  }
}

// Initialize on DOM load
document.addEventListener('DOMContentLoaded', function() {
  // Initialize form validation
  const forms = document.querySelectorAll('.calculator-form');
  forms.forEach(form => {
    new FormValidator(form);
  });
  
  // Initialize input formatting
  document.querySelectorAll('[data-format="currency"]').forEach(input => {
    new InputFormatter(input, { type: 'currency' });
  });
  
  document.querySelectorAll('[data-format="percentage"]').forEach(input => {
    new InputFormatter(input, { type: 'percentage', max: 100 });
  });
  
  document.querySelectorAll('[data-format="number"]').forEach(input => {
    new InputFormatter(input, { type: 'number', decimals: 0 });
  });
  
  // Initialize tooltips
  const tooltips = document.querySelectorAll('[data-tooltip]');
  tooltips.forEach(element => {
    // Tooltip initialization
  });
  
  // Smooth scroll for anchor links
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
      e.preventDefault();
      const target = document.querySelector(this.getAttribute('href'));
      if (target) {
        utils.scrollToElement(target);
      }
    });
  });
  
  // Print functionality
  const printButtons = document.querySelectorAll('[data-print]');
  printButtons.forEach(button => {
    button.addEventListener('click', () => {
      window.print();
    });
  });
});

// Export for use in calculator pages
window.CalculatorUtils = utils;
window.FormValidator = FormValidator;
window.InputFormatter = InputFormatter;
window.RealtimeCalculator = RealtimeCalculator;
window.ChartRenderer = ChartRenderer;