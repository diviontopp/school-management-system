// public.js - Frontend logic for the public portal
document.addEventListener('DOMContentLoaded', () => {

    // --- 1. Initialize Lenis (Smooth Scrolling) ---
    const lenis = new Lenis({
        duration: 1.2,
        easing: (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t)), // https://www.desmos.com/calculator/brs54l4xou
        direction: 'vertical',
        gestureDirection: 'vertical',
        smooth: true,
        mouseMultiplier: 1,
        smoothTouch: false,
        touchMultiplier: 2,
        infinite: false,
    });

    // Integrated GSAP ScrollTrigger update
    lenis.on('scroll', ScrollTrigger.update);

    gsap.ticker.add((time) => {
        lenis.raf(time * 1000);
    });

    gsap.ticker.lagSmoothing(0);


    // --- 2. Mobile Navigation Toggle ---
    const mobileMenuToggle = document.querySelector('.mobile-menu-toggle');
    const navContent = document.querySelector('.nav-content');

    if (mobileMenuToggle && navContent) {
        mobileMenuToggle.addEventListener('click', () => {
            mobileMenuToggle.classList.toggle('active');
            navContent.classList.toggle('active');
            
            // Toggle body scroll
            if (navContent.classList.contains('active')) {
                document.body.style.overflow = 'hidden';
            } else {
                document.body.style.overflow = '';
            }
        });

        // Close menu when clicking outside
        document.addEventListener('click', (e) => {
            if (navContent.classList.contains('active') && !navContent.contains(e.target) && !mobileMenuToggle.contains(e.target)) {
                mobileMenuToggle.classList.remove('active');
                navContent.classList.remove('active');
                document.body.style.overflow = '';
            }
        });

        // Close menu on link click
        const navLinks = navContent.querySelectorAll('a');
        navLinks.forEach(link => {
            link.addEventListener('click', () => {
                mobileMenuToggle.classList.remove('active');
                navContent.classList.remove('active');
                document.body.style.overflow = '';
            });
        });
    }

    // --- 3. Navbar Scroll Effect ---
    const navbar = document.querySelector('.navbar');
    if (navbar) {
        window.addEventListener('scroll', () => {
            if (window.scrollY > 50) {
                navbar.classList.add('scrolled');
            } else {
                navbar.classList.remove('scrolled');
            }
        });
    }

    // --- 3. Global GSAP Animations ---
    gsap.registerPlugin(ScrollTrigger);

    // Fade Up Elements (Batched for staggered entrance)
    ScrollTrigger.batch(".fade-up", {
        interval: 0.1, // time window for batching
        batchMax: 6,   // max elements per batch
        onEnter: batch => gsap.to(batch, {
            y: 0,
            opacity: 1,
            duration: 0.8,
            ease: "power3.out", // Smooth cinematic ease
            stagger: 0.15,
            overwrite: true
        }),
        start: 'top 85%',
        once: true // Only animate once to avoid fatigue
    });

    // Subtle Parallax Effects
    const parallaxImages = document.querySelectorAll('.img-parallax');
    parallaxImages.forEach((img) => {
        gsap.fromTo(img, 
            { y: '-10%' },
            { 
                y: '10%',
                ease: 'none',
                scrollTrigger: {
                    trigger: img.parentElement,
                    start: 'top bottom',
                    end: 'bottom top',
                    scrub: true
                }
            }
        );
    });

    // View Timeline Image Box shadow visibility fix
    const hgContainer = document.querySelector('.hg-scroll-container');
    if (hgContainer) {
        const imgBoxes = document.querySelectorAll('.hg-section .img-box');
        gsap.set(imgBoxes, { autoAlpha: 0 }); // hide initially and remove shadow

        // 1. Fade visibility
        ScrollTrigger.create({
            trigger: hgContainer,
            start: 'top bottom-=70%',
            end: 'bottom top',
            onEnter: () => gsap.to(imgBoxes, { autoAlpha: 1, duration: 0.3 }),
            onLeave: () => gsap.to(imgBoxes, { autoAlpha: 0, duration: 0.3 }),
            onEnterBack: () => gsap.to(imgBoxes, { autoAlpha: 1, duration: 0.3 }),
            onLeaveBack: () => gsap.to(imgBoxes, { autoAlpha: 0, duration: 0.3 })
        });

        // 2. Natural scroll-out at the end (Vibrant campus fix)
        ScrollTrigger.create({
            trigger: hgContainer,
            start: 'bottom bottom', // When the bottom of the container reaches the bottom of the screen
            end: 'bottom top',      // When it scrolls fully out
            scrub: true,
            onEnter: () => gsap.set(imgBoxes, { boxShadow: 'none' }),
            onLeaveBack: () => gsap.set(imgBoxes, { clearProps: 'boxShadow' }),
            animation: gsap.fromTo(imgBoxes,
                { y: 0 },
                { y: () => -window.innerHeight, ease: 'none' }
            )
        });
    }

    // --- 4. Form Submission Loading States ---
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', () => {
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                const originalText = submitBtn.innerHTML;
                submitBtn.disabled = true;
                submitBtn.innerHTML = `<i class="fas fa-circle-notch fa-spin"></i> Processing...`;
                
                // Safety timeout if navigation doesn't happen (e.g. invalid form)
                setTimeout(() => {
                    if (submitBtn.disabled) {
                        submitBtn.disabled = false;
                        submitBtn.innerHTML = originalText;
                    }
                }, 10000);
            }
        });
    });

    // --- 5. Service Worker Registration ---
    if ('serviceWorker' in navigator) {
        window.addEventListener('load', () => {
            navigator.serviceWorker.register('/sw.js').then(registration => {
                console.log('SW registered: ', registration);
            }).catch(registrationError => {
                console.log('SW registration failed: ', registrationError);
            });
        });
    }

});

// --- 5. Global Toast Notification System ---
window.showToast = function(message, type = 'info') {
    const container = document.getElementById('toastContainer');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    
    // Icon mapping
    const icons = {
        success: 'fa-check-circle',
        error: 'fa-exclamation-circle',
        danger: 'fa-exclamation-circle',
        warning: 'fa-exclamation-triangle',
        info: 'fa-info-circle'
    };
    const icon = icons[type] || icons.info;

    toast.innerHTML = `
        <div class="toast-icon"><i class="fas ${icon}"></i></div>
        <div class="toast-content">
            <div class="toast-message">${message}</div>
        </div>
        <button class="toast-close" aria-label="Close message"><i class="fas fa-times"></i></button>
    `;

    container.appendChild(toast);

    // Trigger animation
    requestAnimationFrame(() => {
        toast.classList.add('show');
    });

    // Auto dismiss after 5 seconds
    const dismissTimeout = setTimeout(() => {
        hideToast(toast);
    }, 5000);

    // Manual close
    toast.querySelector('.toast-close').addEventListener('click', () => {
        clearTimeout(dismissTimeout);
        hideToast(toast);
    });

    function hideToast(el) {
        el.classList.remove('show');
        el.addEventListener('transitionend', () => {
            el.remove();
        });
    }
};
