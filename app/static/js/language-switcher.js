/**
 * Language Switcher Component
 * Handles dynamic language switching with persistence and RTL support
 */

class LanguageSwitcher {
    constructor() {
        this.currentLanguage = this.getCurrentLanguage();
        this.supportedLanguages = {
            'en': { name: 'English', native: 'English', direction: 'ltr' },
            'fr': { name: 'French', native: 'Français', direction: 'ltr' },
            'de': { name: 'German', native: 'Deutsch', direction: 'ltr' },
            'es': { name: 'Spanish', native: 'Español', direction: 'ltr' },
            'ar': { name: 'Arabic', native: 'العربية', direction: 'rtl' }
        };
        
        this.init();
    }
    
    init() {
        this.createLanguageSwitcher();
        this.bindEvents();
        this.applyLanguageDirection();
        this.loadTranslations();
    }
    
    getCurrentLanguage() {
        // Priority: URL parameter > localStorage > browser language > default
        const urlParams = new URLSearchParams(window.location.search);
        const urlLang = urlParams.get('lang');
        
        if (urlLang && this.isLanguageSupported(urlLang)) {
            return urlLang;
        }
        
        const storedLang = localStorage.getItem('preferred_language');
        if (storedLang && this.isLanguageSupported(storedLang)) {
            return storedLang;
        }
        
        const browserLang = navigator.language.split('-')[0];
        if (this.isLanguageSupported(browserLang)) {
            return browserLang;
        }
        
        return 'en'; // Default fallback
    }
    
    isLanguageSupported(langCode) {
        return langCode in this.supportedLanguages;
    }
    
    createLanguageSwitcher() {
        const existingSwitcher = document.querySelector('.language-switcher');
        if (existingSwitcher) {
            existingSwitcher.remove();
        }
        
        const switcher = document.createElement('div');
        switcher.className = 'language-switcher';
        switcher.innerHTML = `
            <button class="language-toggle" aria-expanded="false" aria-label="Choose language">
                <span class="current-language">
                    <span class="language-flag">${this.getLanguageFlag(this.currentLanguage)}</span>
                    <span class="language-name">${this.supportedLanguages[this.currentLanguage].native}</span>
                    <svg class="dropdown-icon" width="16" height="16" viewBox="0 0 16 16">
                        <path d="M4.5 6L8 9.5L11.5 6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                </span>
            </button>
            <div class="language-dropdown" role="menu">
                ${Object.entries(this.supportedLanguages).map(([code, info]) => `
                    <button class="language-option ${code === this.currentLanguage ? 'active' : ''}" 
                            data-language="${code}" role="menuitem">
                        <span class="language-flag">${this.getLanguageFlag(code)}</span>
                        <span class="language-info">
                            <span class="native-name">${info.native}</span>
                            <span class="english-name">${info.name}</span>
                        </span>
                        ${code === this.currentLanguage ? '<svg class="check-icon" width="16" height="16" viewBox="0 0 16 16"><path d="M6 12L2 8l1.5-1.5L6 9l6.5-6.5L14 4l-8 8z" fill="currentColor"/></svg>' : ''}
                    </button>
                `).join('')}
            </div>
        `;
        
        // Insert into navigation
        const nav = document.querySelector('.primary-nav');
        if (nav) {
            nav.appendChild(switcher);
        }
    }
    
    getLanguageFlag(langCode) {
        const flags = {
            'en': '🇺🇸',
            'fr': '🇫🇷',
            'de': '🇩🇪',
            'es': '🇪🇸',
            'ar': '🇸🇦'
        };
        return flags[langCode] || '🌐';
    }
    
    bindEvents() {
        const toggle = document.querySelector('.language-toggle');
        const dropdown = document.querySelector('.language-dropdown');
        const options = document.querySelectorAll('.language-option');
        
        if (!toggle || !dropdown) return;
        
        // Toggle dropdown
        toggle.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            
            const isOpen = toggle.getAttribute('aria-expanded') === 'true';
            toggle.setAttribute('aria-expanded', !isOpen);
            dropdown.classList.toggle('open', !isOpen);
        });
        
        // Handle language selection
        options.forEach(option => {
            option.addEventListener('click', (e) => {
                e.preventDefault();
                const newLanguage = option.dataset.language;
                this.switchLanguage(newLanguage);
            });
        });
        
        // Close dropdown when clicking outside
        document.addEventListener('click', (e) => {
            if (!e.target.closest('.language-switcher')) {
                toggle.setAttribute('aria-expanded', 'false');
                dropdown.classList.remove('open');
            }
        });
        
        // Keyboard navigation
        toggle.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                toggle.click();
            }
        });
        
        dropdown.addEventListener('keydown', (e) => {
            const activeOption = dropdown.querySelector('.language-option:focus');
            const allOptions = Array.from(options);
            const currentIndex = allOptions.indexOf(activeOption);
            
            switch (e.key) {
                case 'ArrowDown':
                    e.preventDefault();
                    const nextIndex = (currentIndex + 1) % allOptions.length;
                    allOptions[nextIndex].focus();
                    break;
                case 'ArrowUp':
                    e.preventDefault();
                    const prevIndex = currentIndex > 0 ? currentIndex - 1 : allOptions.length - 1;
                    allOptions[prevIndex].focus();
                    break;
                case 'Escape':
                    toggle.click();
                    toggle.focus();
                    break;
                case 'Enter':
                case ' ':
                    e.preventDefault();
                    activeOption?.click();
                    break;
            }
        });
    }
    
    async switchLanguage(newLanguage) {
        if (!this.isLanguageSupported(newLanguage) || newLanguage === this.currentLanguage) {
            return;
        }
        
        // Show loading state
        this.showLoadingState();
        
        try {
            // Store preference
            localStorage.setItem('preferred_language', newLanguage);
            
            // Update current language
            this.currentLanguage = newLanguage;
            
            // Load translations
            await this.loadTranslations();
            
            // Apply direction changes
            this.applyLanguageDirection();
            
            // Update URL without reload
            this.updateURL(newLanguage);
            
            // Update UI elements
            this.updateLanguageSwitcher();
            this.translatePageContent();
            
            // Trigger custom event
            window.dispatchEvent(new CustomEvent('languageChanged', {
                detail: { language: newLanguage }
            }));
            
            // Hide loading state
            this.hideLoadingState();
            
        } catch (error) {
            console.error('Error switching language:', error);
            this.showError('Failed to switch language. Please try again.');
            this.hideLoadingState();
        }
    }
    
    async loadTranslations() {
        try {
            if (!this.translations) {
                this.translations = {};
            }
            
            if (!this.translations[this.currentLanguage]) {
                const response = await fetch(`/api/translations/${this.currentLanguage}`);
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}`);
                }
                this.translations[this.currentLanguage] = await response.json();
            }
            
            return this.translations[this.currentLanguage];
        } catch (error) {
            console.error('Error loading translations:', error);
            // Fallback to English if available
            if (this.currentLanguage !== 'en' && this.translations.en) {
                return this.translations.en;
            }
            throw error;
        }
    }
    
    applyLanguageDirection() {
        const langInfo = this.supportedLanguages[this.currentLanguage];
        const html = document.documentElement;
        
        html.setAttribute('lang', this.currentLanguage);
        html.setAttribute('dir', langInfo.direction);
        
        // Add RTL class for styling
        if (langInfo.direction === 'rtl') {
            html.classList.add('rtl');
            document.body.classList.add('rtl');
        } else {
            html.classList.remove('rtl');
            document.body.classList.remove('rtl');
        }
    }
    
    updateURL(language) {
        const url = new URL(window.location);
        url.searchParams.set('lang', language);
        window.history.replaceState({}, '', url);
    }
    
    updateLanguageSwitcher() {
        const currentLangElement = document.querySelector('.current-language');
        if (currentLangElement) {
            currentLangElement.innerHTML = `
                <span class="language-flag">${this.getLanguageFlag(this.currentLanguage)}</span>
                <span class="language-name">${this.supportedLanguages[this.currentLanguage].native}</span>
                <svg class="dropdown-icon" width="16" height="16" viewBox="0 0 16 16">
                    <path d="M4.5 6L8 9.5L11.5 6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
            `;
        }
        
        // Update active state
        document.querySelectorAll('.language-option').forEach(option => {
            const isActive = option.dataset.language === this.currentLanguage;
            option.classList.toggle('active', isActive);
            
            if (isActive) {
                option.innerHTML = option.innerHTML.replace(
                    /<svg class="check-icon".*?<\/svg>/,
                    '<svg class="check-icon" width="16" height="16" viewBox="0 0 16 16"><path d="M6 12L2 8l1.5-1.5L6 9l6.5-6.5L14 4l-8 8z" fill="currentColor"/></svg>'
                );
            } else {
                option.innerHTML = option.innerHTML.replace(/<svg class="check-icon".*?<\/svg>/, '');
            }
        });
    }
    
    translatePageContent() {
        if (!this.translations || !this.translations[this.currentLanguage]) {
            return;
        }
        
        const translations = this.translations[this.currentLanguage];
        
        // Translate elements with data-translate attribute
        document.querySelectorAll('[data-translate]').forEach(element => {
            const key = element.dataset.translate;
            const text = this.getNestedValue(translations, key);
            
            if (text) {
                if (element.tagName === 'INPUT' && (element.type === 'text' || element.type === 'email')) {
                    element.placeholder = text;
                } else {
                    element.textContent = text;
                }
            }
        });
        
        // Update page title
        const titleKey = document.querySelector('meta[name="title-key"]')?.content;
        if (titleKey) {
            const title = this.getNestedValue(translations, titleKey);
            if (title) {
                document.title = title + ' - Calculator Suite';
            }
        }
        
        // Update form labels and placeholders
        this.updateFormElements(translations);
        
        // Update navigation
        this.updateNavigation(translations);
    }
    
    updateFormElements(translations) {
        // Update labels
        document.querySelectorAll('label[data-translate]').forEach(label => {
            const key = label.dataset.translate;
            const text = this.getNestedValue(translations, key);
            if (text) {
                label.textContent = text;
            }
        });
        
        // Update placeholders
        document.querySelectorAll('input[data-translate-placeholder]').forEach(input => {
            const key = input.dataset.translatePlaceholder;
            const text = this.getNestedValue(translations, key);
            if (text) {
                input.placeholder = text;
            }
        });
        
        // Update button text
        document.querySelectorAll('button[data-translate]').forEach(button => {
            const key = button.dataset.translate;
            const text = this.getNestedValue(translations, key);
            if (text) {
                button.textContent = text;
            }
        });
    }
    
    updateNavigation(translations) {
        if (translations.navigation) {
            Object.entries(translations.navigation).forEach(([key, value]) => {
                const element = document.querySelector(`[data-nav-key="${key}"]`);
                if (element) {
                    element.textContent = value;
                }
            });
        }
    }
    
    getNestedValue(obj, key) {
        return key.split('.').reduce((current, prop) => {
            return current && current[prop] !== undefined ? current[prop] : null;
        }, obj);
    }
    
    showLoadingState() {
        const switcher = document.querySelector('.language-switcher');
        if (switcher) {
            switcher.classList.add('loading');
        }
    }
    
    hideLoadingState() {
        const switcher = document.querySelector('.language-switcher');
        if (switcher) {
            switcher.classList.remove('loading');
        }
    }
    
    showError(message) {
        // Simple error notification
        const notification = document.createElement('div');
        notification.className = 'language-error-notification';
        notification.textContent = message;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: #ff4444;
            color: white;
            padding: 12px 16px;
            border-radius: 4px;
            z-index: 10000;
            font-size: 14px;
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.remove();
        }, 5000);
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.languageSwitcher = new LanguageSwitcher();
});

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = LanguageSwitcher;
}