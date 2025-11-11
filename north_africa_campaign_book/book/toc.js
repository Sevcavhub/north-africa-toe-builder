// Populate the sidebar
//
// This is a script, and not included directly in the page, to control the total size of the book.
// The TOC contains an entry for each page, so if each page includes a copy of the TOC,
// the total size of the page becomes O(n**2).
class MDBookSidebarScrollbox extends HTMLElement {
    constructor() {
        super();
    }
    connectedCallback() {
        this.innerHTML = '<ol class="chapter"><li class="chapter-item expanded affix "><a href="intro.html">Introduction</a></li><li class="chapter-item expanded affix "><li class="part-title">Strategic Overview</li><li class="chapter-item expanded "><a href="quarter_overviews/1940q2.html"><strong aria-hidden="true">1.</strong> 1940-Q2: Italy Enters War</a></li><li class="chapter-item expanded "><a href="quarter_overviews/1940q3.html"><strong aria-hidden="true">2.</strong> 1940-Q3: Italian Offensive</a></li><li class="chapter-item expanded "><a href="quarter_overviews/1940q4.html"><strong aria-hidden="true">3.</strong> 1940-Q4: Operation Compass</a></li><li class="chapter-item expanded "><a href="quarter_overviews/1941q1.html"><strong aria-hidden="true">4.</strong> 1941-Q1: Rommel Arrives</a></li><li class="chapter-item expanded "><a href="quarter_overviews/1941q2.html"><strong aria-hidden="true">5.</strong> 1941-Q2: Operation Battleaxe</a></li><li class="chapter-item expanded "><a href="quarter_overviews/1941q3.html"><strong aria-hidden="true">6.</strong> 1941-Q3: Desert Stalemate</a></li><li class="chapter-item expanded "><a href="quarter_overviews/1941q4.html"><strong aria-hidden="true">7.</strong> 1941-Q4: Operation Crusader</a></li><li class="chapter-item expanded "><a href="quarter_overviews/1942q1.html"><strong aria-hidden="true">8.</strong> 1942-Q1: Second Offensive</a></li><li class="chapter-item expanded "><a href="quarter_overviews/1942q2.html"><strong aria-hidden="true">9.</strong> 1942-Q2: Gazala and Tobruk</a></li><li class="chapter-item expanded "><a href="quarter_overviews/1942q3.html"><strong aria-hidden="true">10.</strong> 1942-Q3: El Alamein</a></li><li class="chapter-item expanded "><a href="quarter_overviews/1942q4.html"><strong aria-hidden="true">11.</strong> 1942-Q4: Operation Torch</a></li><li class="chapter-item expanded "><a href="quarter_overviews/1943q1.html"><strong aria-hidden="true">12.</strong> 1943-Q1: Tunisia Campaign</a></li><li class="chapter-item expanded "><a href="quarter_overviews/1943q2.html"><strong aria-hidden="true">13.</strong> 1943-Q2: Final Victory</a></li><li class="chapter-item expanded affix "><li class="spacer"></li><li class="chapter-item expanded affix "><a href="appendices/methodology.html">Methodology</a></li><li class="chapter-item expanded affix "><a href="appendices/bibliography.html">Bibliography</a></li><li class="chapter-item expanded affix "><a href="appendices/glossary.html">Glossary</a></li><li class="chapter-item expanded affix "><a href="appendices/abbreviations.html">Abbreviations</a></li></ol>';
        // Set the current, active page, and reveal it if it's hidden
        let current_page = document.location.href.toString().split("#")[0].split("?")[0];
        if (current_page.endsWith("/")) {
            current_page += "index.html";
        }
        var links = Array.prototype.slice.call(this.querySelectorAll("a"));
        var l = links.length;
        for (var i = 0; i < l; ++i) {
            var link = links[i];
            var href = link.getAttribute("href");
            if (href && !href.startsWith("#") && !/^(?:[a-z+]+:)?\/\//.test(href)) {
                link.href = path_to_root + href;
            }
            // The "index" page is supposed to alias the first chapter in the book.
            if (link.href === current_page || (i === 0 && path_to_root === "" && current_page.endsWith("/index.html"))) {
                link.classList.add("active");
                var parent = link.parentElement;
                if (parent && parent.classList.contains("chapter-item")) {
                    parent.classList.add("expanded");
                }
                while (parent) {
                    if (parent.tagName === "LI" && parent.previousElementSibling) {
                        if (parent.previousElementSibling.classList.contains("chapter-item")) {
                            parent.previousElementSibling.classList.add("expanded");
                        }
                    }
                    parent = parent.parentElement;
                }
            }
        }
        // Track and set sidebar scroll position
        this.addEventListener('click', function(e) {
            if (e.target.tagName === 'A') {
                sessionStorage.setItem('sidebar-scroll', this.scrollTop);
            }
        }, { passive: true });
        var sidebarScrollTop = sessionStorage.getItem('sidebar-scroll');
        sessionStorage.removeItem('sidebar-scroll');
        if (sidebarScrollTop) {
            // preserve sidebar scroll position when navigating via links within sidebar
            this.scrollTop = sidebarScrollTop;
        } else {
            // scroll sidebar to current active section when navigating via "next/previous chapter" buttons
            var activeSection = document.querySelector('#sidebar .active');
            if (activeSection) {
                activeSection.scrollIntoView({ block: 'center' });
            }
        }
        // Toggle buttons
        var sidebarAnchorToggles = document.querySelectorAll('#sidebar a.toggle');
        function toggleSection(ev) {
            ev.currentTarget.parentElement.classList.toggle('expanded');
        }
        Array.from(sidebarAnchorToggles).forEach(function (el) {
            el.addEventListener('click', toggleSection);
        });
    }
}
window.customElements.define("mdbook-sidebar-scrollbox", MDBookSidebarScrollbox);
