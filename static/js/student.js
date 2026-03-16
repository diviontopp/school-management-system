/* =========================================================================
   SCHOLARIS STUDENT PORTAL — Client-Side Logic
   Premium, matching school website UX
========================================================================= */

document.addEventListener('DOMContentLoaded', () => {
    initSidebar();
    initCardFlips();
    initToasts();
});

/* =========================================================================
   SIDEBAR NAVIGATION (desktop fixed + mobile slide-out)
========================================================================= */
function initSidebar() {
    const btn = document.getElementById('hamburgerBtn');
    const sidebar = document.getElementById('navDrawer');
    const overlay = document.getElementById('menuOverlay');

    if (!btn || !sidebar || !overlay) return;

    function openMenu() {
        btn.classList.add('active');
        sidebar.classList.add('active');
        overlay.classList.add('active');
        btn.setAttribute('aria-expanded', 'true');
        document.body.style.overflow = 'hidden';
    }

    function closeMenu() {
        btn.classList.remove('active');
        sidebar.classList.remove('active');
        overlay.classList.remove('active');
        btn.setAttribute('aria-expanded', 'false');
        document.body.style.overflow = '';
    }

    btn.addEventListener('click', () => {
        sidebar.classList.contains('active') ? closeMenu() : openMenu();
    });

    overlay.addEventListener('click', closeMenu);

    // Escape key
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && sidebar.classList.contains('active')) {
            closeMenu();
        }
    });
}

/* =========================================================================
   CARD FLIP INTERACTION
========================================================================= */
function initCardFlips() {
    const cards = document.querySelectorAll('.item-card[data-flippable="true"]');

    cards.forEach(card => {
        const front = card.querySelector('.card-front');
        const flipContent = card.querySelector('.card-flip-content');
        const yesBtn = card.querySelector('.flip-btn--yes');
        const noBtn = card.querySelector('.flip-btn--no');

        if (!front || !flipContent) return;

        // Click front → flip
        front.addEventListener('click', (e) => {
            e.stopPropagation();
            card.classList.add('flipped');
        });

        // "No" → flip back
        if (noBtn) {
            noBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                card.classList.remove('flipped');
            });
        }

        // "Yes" → mark done via AJAX
        if (yesBtn) {
            yesBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                const itemId = card.dataset.itemId;
                const itemType = card.dataset.itemType;

                yesBtn.disabled = true;
                yesBtn.textContent = '...';

                fetch('/student/mark-complete', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        item_id: itemId,
                        item_type: itemType
                    })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        // Green success
                        card.style.background = '#dcfce7';
                        card.style.borderColor = '#16a34a';
                        card.style.transition = 'all 0.4s cubic-bezier(0.16, 1, 0.3, 1)';

                        flipContent.innerHTML = `
                            <div style="display:flex; flex-direction:column; align-items:center; gap:8px;">
                                <i class="fas fa-check-circle" style="font-size:2.5rem; color:#16a34a;"></i>
                                <span style="font-family:'Playfair Display',serif; font-weight:600; font-size:1.15rem; color:#0f4c81;">Done!</span>
                            </div>
                        `;

                        setTimeout(() => {
                            card.style.opacity = '0';
                            card.style.transform = 'translateY(-10px) scale(0.97)';
                            setTimeout(() => card.style.display = 'none', 400);
                        }, 1200);

                        showToast('Marked as completed!', 'success');
                    } else {
                        showToast(data.error || 'Something went wrong.', 'danger');
                        yesBtn.disabled = false;
                        yesBtn.textContent = 'YES';
                    }
                })
                .catch(err => {
                    console.error('Error:', err);
                    showToast('Network error.', 'danger');
                    yesBtn.disabled = false;
                    yesBtn.textContent = 'YES';
                });
            });
        }
    });
}

/* =========================================================================
   TOAST NOTIFICATIONS (glassmorphism style)
========================================================================= */
function initToasts() {
    window.showToast = showToast;
}

function showToast(message, type = 'info') {
    const container = document.getElementById('toastContainer');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = `toast toast--${type}`;

    const icons = {
        success: 'fa-check-circle',
        danger: 'fa-exclamation-circle',
        warning: 'fa-exclamation-triangle',
        info: 'fa-info-circle'
    };

    toast.innerHTML = `
        <i class="fas ${icons[type] || icons.info}"></i>
        <span>${message}</span>
    `;

    container.appendChild(toast);

    // Auto-dismiss after 4s
    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(120%)';
        toast.style.transition = 'all 0.4s cubic-bezier(0.16, 1, 0.3, 1)';
        setTimeout(() => toast.remove(), 400);
    }, 4000);
}
