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


    // --- 2. Navbar Scroll Effect ---
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

    // Fade Up Elements
    const fadeUpElements = document.querySelectorAll('.fade-up');
    fadeUpElements.forEach((el) => {
        gsap.to(el, {
            scrollTrigger: {
                trigger: el,
                start: 'top 85%',
                toggleActions: 'play none none reverse'
            },
            y: 0,
            opacity: 1,
            duration: 1,
            ease: 'power3.out'
        });
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

});
