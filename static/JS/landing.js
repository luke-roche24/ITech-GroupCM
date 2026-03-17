// Loader
window.addEventListener('load', function () {
    setTimeout(function () {
        document.getElementById('loader').classList.add('hide');
    }, 1400);
});

// Scroll-triggered step cards
const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            const delay = entry.target.getAttribute('data-delay') || 0;
            setTimeout(() => entry.target.classList.add('visible'), delay);
            observer.unobserve(entry.target);
        }
    });
}, { threshold: 0.2 });
document.querySelectorAll('.step-card').forEach(card => observer.observe(card));

// Back to top button logic
const backTop = document.getElementById('backTop');
window.addEventListener('scroll', function() {
    if (window.scrollY > 400) {
        backTop.classList.add('show');
    } else {
        backTop.classList.remove('show');
    }
});

backTop.addEventListener('click', function() {
    window.scrollTo({ top: 0, behavior: 'smooth' });
});
