// Calculator Suite JavaScript
// Lightweight vanilla JS for calculator interactions

document.addEventListener('DOMContentLoaded', function() {
    // Add loading state to buttons
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        form.addEventListener('submit', function() {
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                const originalText = submitBtn.textContent;
                submitBtn.textContent = 'Calculating...';
                submitBtn.disabled = true;
                
                // Re-enable button after response (handled by calculator.html script)
                setTimeout(() => {
                    submitBtn.textContent = originalText;
                    submitBtn.disabled = false;
                }, 2000);
            }
        });
    });
    
    // Add smooth scrolling for anchor links
    const anchorLinks = document.querySelectorAll('a[href^="#"]');
    
    anchorLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
    
    // Analytics tracking for calculator usage
    if (typeof gtag !== 'undefined') {
        const calculatorForms = document.querySelectorAll('#calculator-form');
        
        calculatorForms.forEach(form => {
            form.addEventListener('submit', function() {
                const calculatorType = window.location.pathname.split('/')[2];
                gtag('event', 'calculator_use', {
                    'event_category': 'Calculator',
                    'event_label': calculatorType,
                    'value': 1
                });
            });
        });
    }
});

// Utility functions
function formatNumber(num, decimals = 2) {
    return Number(num).toLocaleString(undefined, {
        minimumFractionDigits: decimals,
        maximumFractionDigits: decimals
    });
}

function copyToClipboard(text) {
    if (navigator.clipboard && window.isSecureContext) {
        return navigator.clipboard.writeText(text);
    } else {
        // Fallback for older browsers
        const textArea = document.createElement('textarea');
        textArea.value = text;
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();
        try {
            document.execCommand('copy');
        } catch (err) {
            console.error('Failed to copy text: ', err);
        }
        document.body.removeChild(textArea);
    }
}