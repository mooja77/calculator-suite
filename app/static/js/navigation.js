/**
 * Enhanced Navigation JavaScript
 * Handles mobile menu, dropdowns, and scroll effects
 */

class Navigation {
  constructor() {
    this.header = document.querySelector('.site-header');
    this.navToggle = document.querySelector('.nav-toggle');
    this.navMenu = document.querySelector('.nav-menu');
    this.dropdowns = document.querySelectorAll('.nav-item--dropdown');
    this.isMenuOpen = false;
    this.scrollThreshold = 100;
    
    this.init();
  }
  
  init() {
    // Mobile menu toggle
    if (this.navToggle) {
      this.navToggle.addEventListener('click', () => this.toggleMenu());
    }
    
    // Dropdown menus
    this.initDropdowns();
    
    // Scroll effects
    this.initScrollEffects();
    
    // Close menu on escape
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && this.isMenuOpen) {
        this.closeMenu();
      }
    });
    
    // Close menu on outside click
    document.addEventListener('click', (e) => {
      if (this.isMenuOpen && !e.target.closest('.primary-nav')) {
        this.closeMenu();
      }
    });
    
    // Handle resize
    window.addEventListener('resize', () => {
      if (window.innerWidth >= 768 && this.isMenuOpen) {
        this.closeMenu();
      }
    });
  }
  
  toggleMenu() {
    this.isMenuOpen ? this.closeMenu() : this.openMenu();
  }
  
  openMenu() {
    this.isMenuOpen = true;
    this.navToggle.setAttribute('aria-expanded', 'true');
    this.navMenu.classList.add('nav-menu--open');
    
    // Create backdrop
    this.createBackdrop();
    
    // Prevent body scroll
    document.body.style.overflow = 'hidden';
    
    // Focus first menu item
    setTimeout(() => {
      const firstLink = this.navMenu.querySelector('a, button');
      if (firstLink) firstLink.focus();
    }, 300);
  }
  
  closeMenu() {
    this.isMenuOpen = false;
    this.navToggle.setAttribute('aria-expanded', 'false');
    this.navMenu.classList.remove('nav-menu--open');
    
    // Remove backdrop
    this.removeBackdrop();
    
    // Restore body scroll
    document.body.style.overflow = '';
    
    // Return focus to toggle
    this.navToggle.focus();
  }
  
  createBackdrop() {
    if (!this.backdrop) {
      this.backdrop = document.createElement('div');
      this.backdrop.className = 'nav-backdrop';
      document.body.appendChild(this.backdrop);
      
      this.backdrop.addEventListener('click', () => this.closeMenu());
    }
    
    // Force reflow before adding visible class
    this.backdrop.offsetHeight;
    this.backdrop.classList.add('nav-backdrop--visible');
  }
  
  removeBackdrop() {
    if (this.backdrop) {
      this.backdrop.classList.remove('nav-backdrop--visible');
      setTimeout(() => {
        this.backdrop.remove();
        this.backdrop = null;
      }, 300);
    }
  }
  
  initDropdowns() {
    this.dropdowns.forEach(dropdown => {
      const trigger = dropdown.querySelector('.nav-link--dropdown');
      const menu = dropdown.querySelector('.dropdown-menu');
      
      if (!trigger || !menu) return;
      
      // Click handler for mobile
      trigger.addEventListener('click', (e) => {
        if (window.innerWidth < 768) {
          e.preventDefault();
          this.toggleDropdown(dropdown, trigger);
        }
      });
      
      // Keyboard navigation
      trigger.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          this.toggleDropdown(dropdown, trigger);
        }
        
        if (e.key === 'ArrowDown' && trigger.getAttribute('aria-expanded') === 'true') {
          e.preventDefault();
          const firstLink = menu.querySelector('a');
          if (firstLink) firstLink.focus();
        }
      });
      
      // Close dropdown on escape
      menu.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
          this.closeDropdown(dropdown, trigger);
          trigger.focus();
        }
      });
    });
  }
  
  toggleDropdown(dropdown, trigger) {
    const isOpen = trigger.getAttribute('aria-expanded') === 'true';
    
    // Close all other dropdowns
    this.dropdowns.forEach(d => {
      if (d !== dropdown) {
        this.closeDropdown(d, d.querySelector('.nav-link--dropdown'));
      }
    });
    
    if (isOpen) {
      this.closeDropdown(dropdown, trigger);
    } else {
      this.openDropdown(dropdown, trigger);
    }
  }
  
  openDropdown(dropdown, trigger) {
    trigger.setAttribute('aria-expanded', 'true');
    dropdown.setAttribute('aria-expanded', 'true');
  }
  
  closeDropdown(dropdown, trigger) {
    if (trigger) trigger.setAttribute('aria-expanded', 'false');
    dropdown.setAttribute('aria-expanded', 'false');
  }
  
  initScrollEffects() {
    let lastScroll = 0;
    
    window.addEventListener('scroll', () => {
      const currentScroll = window.pageYOffset;
      
      // Add scrolled class
      if (currentScroll > this.scrollThreshold) {
        this.header.classList.add('site-header--scrolled');
      } else {
        this.header.classList.remove('site-header--scrolled');
      }
      
      // Hide/show on scroll (optional)
      // if (currentScroll > lastScroll && currentScroll > 200) {
      //   this.header.style.transform = 'translateY(-100%)';
      // } else {
      //   this.header.style.transform = 'translateY(0)';
      // }
      
      lastScroll = currentScroll;
    });
  }
}

// Initialize navigation on DOM load
document.addEventListener('DOMContentLoaded', () => {
  new Navigation();
});