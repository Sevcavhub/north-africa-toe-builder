// Add "Back to Main Site" button next to search/print buttons
(function() {
    // Wait for DOM to be ready
    window.addEventListener('DOMContentLoaded', function() {
        // Find the right-buttons div in the menu bar
        const rightButtons = document.querySelector('.right-buttons');
        if (!rightButtons) return;

        // Create the back button link
        const backLink = document.createElement('a');
        backLink.href = 'https://sevcavhub.github.io/north-africa-toe-builder/';
        backLink.title = 'Back to Main Site';
        backLink.setAttribute('aria-label', 'Back to Main Site');
        backLink.style.cssText = `
            display: inline-flex;
            align-items: center;
            gap: 0.3rem;
            color: var(--icons);
            text-decoration: none;
            font-size: 0.875rem;
            padding: 0.25rem 0.5rem;
            margin-right: 0.5rem;
            border-radius: 4px;
            transition: all 0.2s ease;
        `;

        // Add arrow SVG and text
        backLink.innerHTML = `
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M19 12H5M12 19l-7-7 7-7"/>
            </svg>
            <span style="font-weight: 500;">Main Site</span>
        `;

        // Add hover effect
        backLink.addEventListener('mouseenter', function() {
            this.style.background = 'var(--sidebar-bg)';
        });

        backLink.addEventListener('mouseleave', function() {
            this.style.background = 'transparent';
        });

        // Insert before the first child (print button)
        rightButtons.insertBefore(backLink, rightButtons.firstChild);
    });
})();
