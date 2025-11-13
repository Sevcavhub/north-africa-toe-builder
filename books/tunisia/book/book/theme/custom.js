// Add "Back to Main Site" button to the top of each page
(function() {
    // Wait for DOM to be ready
    window.addEventListener('DOMContentLoaded', function() {
        // Find the main content div
        const contentDiv = document.getElementById('content');
        if (!contentDiv) return;

        // Create the navigation header
        const navHeader = document.createElement('div');
        navHeader.style.cssText = `
            background: linear-gradient(135deg, #4A5335 0%, #6B7F3D 100%);
            padding: 0.5rem 1rem;
            margin: -1rem -1rem 1rem -1rem;
            border-bottom: 3px solid #C9A77C;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        `;

        // Create the back button
        const backLink = document.createElement('a');
        backLink.href = 'https://sevcavhub.github.io/north-africa-toe-builder/';
        backLink.style.cssText = `
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            color: white;
            text-decoration: none;
            font-weight: 600;
            font-size: 0.95rem;
            padding: 0.5rem 1rem;
            background: rgba(255,255,255,0.1);
            border-radius: 4px;
            border: 2px solid rgba(255,255,255,0.3);
            transition: all 0.3s ease;
        `;

        // Add arrow SVG
        backLink.innerHTML = `
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M19 12H5M12 19l-7-7 7-7"/>
            </svg>
            <span>Back to Main Site</span>
        `;

        // Add hover effect
        backLink.addEventListener('mouseenter', function() {
            this.style.background = 'rgba(255,255,255,0.2)';
            this.style.borderColor = 'rgba(255,255,255,0.5)';
            this.style.transform = 'translateX(-2px)';
        });

        backLink.addEventListener('mouseleave', function() {
            this.style.background = 'rgba(255,255,255,0.1)';
            this.style.borderColor = 'rgba(255,255,255,0.3)';
            this.style.transform = 'translateX(0)';
        });

        // Assemble and inject
        navHeader.appendChild(backLink);
        contentDiv.insertBefore(navHeader, contentDiv.firstChild);
    });
})();
