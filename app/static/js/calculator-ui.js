/**
 * Enhanced Calculator UI Components
 * Modern, accessible, and delightful interactions
 */

// ===============================================
// Number Formatting and Input Handling
// ===============================================

class NumberFormatter {
  constructor(locale = 'en-US', currency = 'USD') {
    this.locale = locale;
    this.currency = currency;
    
    // Formatters
    this.currencyFormatter = new Intl.NumberFormat(locale, {
      style: 'currency',
      currency: currency,
      minimumFractionDigits: 0,
      maximumFractionDigits: 2
    });
    
    this.percentFormatter = new Intl.NumberFormat(locale, {
      style: 'percent',
      minimumFractionDigits: 0,
      maximumFractionDigits: 2
    });
    
    this.numberFormatter = new Intl.NumberFormat(locale, {
      minimumFractionDigits: 0,
      maximumFractionDigits: 2
    });
  }
  
  formatCurrency(value) {
    return this.currencyFormatter.format(value);
  }
  
  formatPercent(value) {
    return this.percentFormatter.format(value / 100);
  }
  
  formatNumber(value, decimals = 2) {
    const formatter = new Intl.NumberFormat(this.locale, {
      minimumFractionDigits: 0,
      maximumFractionDigits: decimals
    });
    return formatter.format(value);
  }
  
  parseNumber(value) {
    // Remove formatting characters
    const cleanValue = value.toString()
      .replace(/[^\d.-]/g, '')
      .replace(/,/g, '');
    return parseFloat(cleanValue) || 0;
  }
}

// ===============================================
// Enhanced Input Components
// ===============================================

class EnhancedInput {
  constructor(element, options = {}) {
    this.element = element;
    this.wrapper = element.closest('.calc-input');
    this.options = {
      type: 'number',
      formatter: null,
      min: null,
      max: null,
      step: 1,
      realtime: true,
      ...options
    };
    
    this.init();
  }
  
  init() {
    // Add formatting on blur
    this.element.addEventListener('blur', () => this.format());
    
    // Add validation on input
    this.element.addEventListener('input', () => {
      this.validate();
      if (this.options.realtime && this.options.onChange) {
        this.options.onChange(this.getValue());
      }
    });
    
    // Handle keyboard shortcuts
    this.element.addEventListener('keydown', (e) => this.handleKeyboard(e));
    
    // Initialize with formatted value if exists
    if (this.element.value) {
      this.format();
    }
  }
  
  getValue() {
    if (this.options.formatter) {
      return this.options.formatter.parseNumber(this.element.value);
    }
    return parseFloat(this.element.value) || 0;
  }
  
  setValue(value) {
    this.element.value = value;
    this.format();
    this.validate();
  }
  
  format() {
    const value = this.getValue();
    
    if (this.options.type === 'currency' && this.options.formatter) {
      // Don't format while typing
      if (document.activeElement !== this.element) {
        this.element.value = this.options.formatter.formatCurrency(value);
      }
    } else if (this.options.type === 'percent' && this.options.formatter) {
      this.element.value = value.toFixed(2);
    }
  }
  
  validate() {
    const value = this.getValue();
    let isValid = true;
    const errors = [];
    
    // Check min/max
    if (this.options.min !== null && value < this.options.min) {
      isValid = false;
      errors.push(`Minimum value is ${this.options.min}`);
    }
    
    if (this.options.max !== null && value > this.options.max) {
      isValid = false;
      errors.push(`Maximum value is ${this.options.max}`);
    }
    
    // Update UI
    this.element.classList.toggle('calc-input__field--error', !isValid);
    
    // Show/hide error message
    const errorElement = this.wrapper?.querySelector('.calc-input__error');
    if (errorElement) {
      errorElement.textContent = errors.join(', ');
      errorElement.style.display = isValid ? 'none' : 'block';
    }
    
    return isValid;
  }
  
  handleKeyboard(e) {
    const step = this.options.step || 1;
    const value = this.getValue();
    
    switch(e.key) {
      case 'ArrowUp':
        e.preventDefault();
        this.setValue(value + step);
        break;
      case 'ArrowDown':
        e.preventDefault();
        this.setValue(value - step);
        break;
    }
  }
}

// ===============================================
// Smart Slider Component
// ===============================================

class SmartSlider {
  constructor(element, options = {}) {
    this.container = element;
    this.options = {
      min: 0,
      max: 100,
      step: 1,
      value: 0,
      unit: '',
      marks: false,
      tooltip: true,
      ...options
    };
    
    this.init();
  }
  
  init() {
    // Get elements
    this.input = this.container.querySelector('.calc-slider__input');
    this.valueInput = this.container.querySelector('.calc-slider__value');
    this.fill = this.container.querySelector('.calc-slider__fill');
    this.thumb = this.container.querySelector('.calc-slider__thumb');
    
    if (!this.input) return;
    
    // Set initial values
    this.input.min = this.options.min;
    this.input.max = this.options.max;
    this.input.step = this.options.step;
    this.input.value = this.options.value;
    
    // Update UI
    this.updateSlider();
    
    // Add event listeners
    this.input.addEventListener('input', () => this.handleInput());
    this.valueInput?.addEventListener('change', () => this.handleValueInput());
    
    // Add keyboard support
    this.input.addEventListener('keydown', (e) => this.handleKeyboard(e));
  }
  
  handleInput() {
    this.updateSlider();
    
    if (this.options.onChange) {
      this.options.onChange(this.getValue());
    }
  }
  
  handleValueInput() {
    const value = parseFloat(this.valueInput.value) || 0;
    const clampedValue = Math.max(this.options.min, Math.min(this.options.max, value));
    
    this.input.value = clampedValue;
    this.valueInput.value = clampedValue;
    this.updateSlider();
    
    if (this.options.onChange) {
      this.options.onChange(clampedValue);
    }
  }
  
  handleKeyboard(e) {
    const step = parseFloat(this.options.step) || 1;
    const bigStep = step * 10;
    
    switch(e.key) {
      case 'ArrowLeft':
      case 'ArrowDown':
        e.preventDefault();
        this.setValue(this.getValue() - (e.shiftKey ? bigStep : step));
        break;
      case 'ArrowRight':
      case 'ArrowUp':
        e.preventDefault();
        this.setValue(this.getValue() + (e.shiftKey ? bigStep : step));
        break;
      case 'Home':
        e.preventDefault();
        this.setValue(this.options.min);
        break;
      case 'End':
        e.preventDefault();
        this.setValue(this.options.max);
        break;
    }
  }
  
  getValue() {
    return parseFloat(this.input.value) || 0;
  }
  
  setValue(value) {
    const clampedValue = Math.max(this.options.min, Math.min(this.options.max, value));
    this.input.value = clampedValue;
    
    if (this.valueInput) {
      this.valueInput.value = clampedValue;
    }
    
    this.updateSlider();
    
    if (this.options.onChange) {
      this.options.onChange(clampedValue);
    }
  }
  
  updateSlider() {
    const value = this.getValue();
    const percentage = ((value - this.options.min) / (this.options.max - this.options.min)) * 100;
    
    // Update fill width
    if (this.fill) {
      this.fill.style.width = `${percentage}%`;
    }
    
    // Update thumb position
    if (this.thumb) {
      this.thumb.style.left = `${percentage}%`;
    }
    
    // Update value input
    if (this.valueInput) {
      this.valueInput.value = value;
    }
    
    // Update ARIA attributes
    this.input.setAttribute('aria-valuenow', value);
    this.input.setAttribute('aria-valuetext', `${value}${this.options.unit}`);
  }
}

// ===============================================
// Real-time Calculator
// ===============================================

class RealtimeCalculator {
  constructor(formElement, options = {}) {
    this.form = formElement;
    this.options = {
      debounceDelay: 300,
      showLoading: true,
      animateResults: true,
      ...options
    };
    
    this.inputs = new Map();
    this.isCalculating = false;
    this.debounceTimer = null;
    
    this.init();
  }
  
  init() {
    // Initialize all inputs
    this.form.querySelectorAll('input[data-calc-input]').forEach(input => {
      const type = input.dataset.calcInput;
      const enhancedInput = new EnhancedInput(input, {
        type: type,
        formatter: this.options.formatter,
        onChange: () => this.scheduleCalculation()
      });
      
      this.inputs.set(input.name, enhancedInput);
    });
    
    // Initialize sliders
    this.form.querySelectorAll('.calc-slider').forEach(slider => {
      new SmartSlider(slider, {
        onChange: () => this.scheduleCalculation()
      });
    });
    
    // Prevent form submission
    this.form.addEventListener('submit', (e) => {
      e.preventDefault();
      this.calculate();
    });
    
    // Initial calculation
    this.calculate();
  }
  
  scheduleCalculation() {
    if (!this.options.realtime) return;
    
    // Clear existing timer
    clearTimeout(this.debounceTimer);
    
    // Schedule new calculation
    this.debounceTimer = setTimeout(() => {
      this.calculate();
    }, this.options.debounceDelay);
  }
  
  async calculate() {
    if (this.isCalculating) return;
    
    // Validate all inputs
    let isValid = true;
    this.inputs.forEach(input => {
      if (!input.validate()) {
        isValid = false;
      }
    });
    
    if (!isValid) return;
    
    this.isCalculating = true;
    
    // Show loading state
    if (this.options.showLoading) {
      this.showLoading();
    }
    
    try {
      // Get form data
      const formData = new FormData(this.form);
      const data = Object.fromEntries(formData);
      
      // Call calculation function
      const results = await this.options.onCalculate(data);
      
      // Display results
      this.displayResults(results);
      
    } catch (error) {
      console.error('Calculation error:', error);
      this.showError(error.message);
    } finally {
      this.isCalculating = false;
      this.hideLoading();
    }
  }
  
  displayResults(results) {
    const container = document.querySelector('.results-container');
    if (!container) return;
    
    // Show container with animation
    container.style.display = 'block';
    
    if (this.options.animateResults) {
      container.classList.add('animate-in');
      
      // Animate individual values
      Object.entries(results).forEach(([key, value], index) => {
        const element = container.querySelector(`[data-result="${key}"]`);
        if (element && typeof value === 'number') {
          this.animateValue(element, value, index * 100);
        }
      });
    } else {
      // Direct update
      Object.entries(results).forEach(([key, value]) => {
        const element = container.querySelector(`[data-result="${key}"]`);
        if (element) {
          element.textContent = this.formatValue(key, value);
        }
      });
    }
  }
  
  animateValue(element, targetValue, delay = 0) {
    const startValue = parseFloat(element.textContent.replace(/[^0-9.-]/g, '')) || 0;
    const duration = 1000;
    const startTime = performance.now() + delay;
    
    const update = (currentTime) => {
      const elapsed = Math.max(0, currentTime - startTime);
      const progress = Math.min(elapsed / duration, 1);
      
      // Easing function
      const easeOutQuad = 1 - (1 - progress) * (1 - progress);
      
      const currentValue = startValue + (targetValue - startValue) * easeOutQuad;
      element.textContent = this.formatValue(element.dataset.result, currentValue);
      
      if (progress < 1) {
        requestAnimationFrame(update);
      }
    };
    
    requestAnimationFrame(update);
  }
  
  formatValue(key, value) {
    if (!this.options.formatter) return value;
    
    // Format based on result type
    if (key.includes('payment') || key.includes('amount') || key.includes('total')) {
      return this.options.formatter.formatCurrency(value);
    } else if (key.includes('rate') || key.includes('percent')) {
      return this.options.formatter.formatPercent(value);
    } else {
      return this.options.formatter.formatNumber(value);
    }
  }
  
  showLoading() {
    const button = this.form.querySelector('button[type="submit"]');
    if (button) {
      button.classList.add('btn--loading');
      button.disabled = true;
    }
  }
  
  hideLoading() {
    const button = this.form.querySelector('button[type="submit"]');
    if (button) {
      button.classList.remove('btn--loading');
      button.disabled = false;
    }
  }
  
  showError(message) {
    // Create or update error element
    let errorElement = this.form.querySelector('.calc-error');
    
    if (!errorElement) {
      errorElement = document.createElement('div');
      errorElement.className = 'calc-error';
      errorElement.innerHTML = `
        <svg class="calc-error__icon" fill="currentColor" viewBox="0 0 20 20">
          <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd"/>
        </svg>
        <div class="calc-error__content">
          <div class="calc-error__title">Calculation Error</div>
          <div class="calc-error__message"></div>
        </div>
      `;
      this.form.prepend(errorElement);
    }
    
    errorElement.querySelector('.calc-error__message').textContent = message;
    errorElement.style.display = 'flex';
    
    // Auto-hide after 5 seconds
    setTimeout(() => {
      errorElement.style.display = 'none';
    }, 5000);
  }
}

// ===============================================
// Chart Components
// ===============================================

class EnhancedChart {
  constructor(canvas, options = {}) {
    this.canvas = canvas;
    this.ctx = canvas.getContext('2d');
    this.options = {
      type: 'doughnut',
      responsive: true,
      maintainAspectRatio: false,
      animation: {
        duration: 1000,
        easing: 'easeOutQuart'
      },
      ...options
    };
    
    this.chart = null;
    this.init();
  }
  
  init() {
    // Ensure Chart.js is loaded
    if (typeof Chart === 'undefined') {
      console.error('Chart.js is not loaded');
      return;
    }
    
    // Configure default options
    Chart.defaults.font.family = getComputedStyle(document.body).getPropertyValue('--font-sans');
    Chart.defaults.color = getComputedStyle(document.body).getPropertyValue('--gray-700');
  }
  
  render(data, options = {}) {
    const config = {
      type: this.options.type,
      data: this.formatData(data),
      options: {
        ...this.options,
        ...options,
        plugins: {
          legend: {
            position: 'bottom',
            padding: 20,
            labels: {
              padding: 15,
              usePointStyle: true,
              font: {
                size: 14
              }
            }
          },
          tooltip: {
            backgroundColor: 'rgba(0, 0, 0, 0.8)',
            padding: 12,
            cornerRadius: 8,
            displayColors: true,
            callbacks: {
              label: (context) => {
                const label = context.label || '';
                const value = context.parsed;
                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                const percentage = ((value / total) * 100).toFixed(1);
                
                if (this.options.formatter) {
                  const formattedValue = this.options.formatter.formatCurrency(value);
                  return `${label}: ${formattedValue} (${percentage}%)`;
                }
                
                return `${label}: ${value} (${percentage}%)`;
              }
            }
          }
        }
      }
    };
    
    // Destroy existing chart
    if (this.chart) {
      this.chart.destroy();
    }
    
    // Create new chart
    this.chart = new Chart(this.ctx, config);
  }
  
  formatData(data) {
    // Generate colors
    const colors = [
      '#4F46E5', // Primary blue
      '#7C3AED', // Purple
      '#EC4899', // Pink
      '#F59E0B', // Amber
      '#10B981', // Green
      '#3B82F6', // Blue
      '#EF4444', // Red
      '#6B7280'  // Gray
    ];
    
    return {
      labels: Object.keys(data),
      datasets: [{
        data: Object.values(data),
        backgroundColor: colors.slice(0, Object.keys(data).length),
        borderWidth: 0,
        spacing: 2
      }]
    };
  }
  
  update(data, options = {}) {
    if (!this.chart) {
      this.render(data, options);
      return;
    }
    
    this.chart.data = this.formatData(data);
    this.chart.update();
  }
  
  destroy() {
    if (this.chart) {
      this.chart.destroy();
      this.chart = null;
    }
  }
}

// ===============================================
// Toast Notifications
// ===============================================

class ToastManager {
  constructor() {
    this.container = null;
    this.toasts = new Map();
    this.init();
  }
  
  init() {
    // Create container if it doesn't exist
    if (!document.querySelector('.toast-container')) {
      this.container = document.createElement('div');
      this.container.className = 'toast-container';
      document.body.appendChild(this.container);
    } else {
      this.container = document.querySelector('.toast-container');
    }
  }
  
  show(message, options = {}) {
    const defaults = {
      type: 'info',
      duration: 5000,
      title: null,
      dismissible: true
    };
    
    const settings = { ...defaults, ...options };
    const id = Date.now();
    
    // Create toast element
    const toast = document.createElement('div');
    toast.className = `toast toast--${settings.type}`;
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'polite');
    
    // Build content
    let iconSvg = '';
    switch(settings.type) {
      case 'success':
        iconSvg = '<path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/>';
        break;
      case 'error':
        iconSvg = '<path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd"/>';
        break;
      case 'warning':
        iconSvg = '<path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd"/>';
        break;
      default:
        iconSvg = '<path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd"/>';
    }
    
    toast.innerHTML = `
      <svg class="toast__icon" fill="currentColor" viewBox="0 0 20 20">
        ${iconSvg}
      </svg>
      <div class="toast__content">
        ${settings.title ? `<div class="toast__title">${settings.title}</div>` : ''}
        <div class="toast__message">${message}</div>
      </div>
      ${settings.dismissible ? `
        <button class="toast__close" aria-label="Dismiss">
          <svg fill="currentColor" viewBox="0 0 20 20" width="20" height="20">
            <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd"/>
          </svg>
        </button>
      ` : ''}
    `;
    
    // Add to container
    this.container.appendChild(toast);
    this.toasts.set(id, toast);
    
    // Add close handler
    if (settings.dismissible) {
      const closeBtn = toast.querySelector('.toast__close');
      closeBtn.addEventListener('click', () => this.dismiss(id));
    }
    
    // Auto dismiss
    if (settings.duration > 0) {
      setTimeout(() => this.dismiss(id), settings.duration);
    }
    
    return id;
  }
  
  dismiss(id) {
    const toast = this.toasts.get(id);
    if (!toast) return;
    
    // Add exit animation
    toast.style.animation = 'slideOutRight 0.3s ease-out forwards';
    
    setTimeout(() => {
      toast.remove();
      this.toasts.delete(id);
    }, 300);
  }
  
  success(message, options = {}) {
    return this.show(message, { ...options, type: 'success' });
  }
  
  error(message, options = {}) {
    return this.show(message, { ...options, type: 'error' });
  }
  
  warning(message, options = {}) {
    return this.show(message, { ...options, type: 'warning' });
  }
  
  info(message, options = {}) {
    return this.show(message, { ...options, type: 'info' });
  }
}

// ===============================================
// Export components
// ===============================================

window.CalculatorUI = {
  NumberFormatter,
  EnhancedInput,
  SmartSlider,
  RealtimeCalculator,
  EnhancedChart,
  ToastManager
};