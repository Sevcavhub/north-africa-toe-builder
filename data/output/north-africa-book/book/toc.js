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
        this.innerHTML = '<ol class="chapter"><li class="chapter-item expanded affix "><a href="introduction.html">Introduction</a></li><li class="chapter-item expanded affix "><li class="spacer"></li><li class="chapter-item expanded affix "><li class="part-title">1941 - Second Quarter (April - June)</li><li class="chapter-item expanded "><a href="1941-q2/overview.html"><strong aria-hidden="true">1.</strong> 1941-Q2 Overview</a></li><li class="chapter-item expanded "><a href="1941-q2/strategic-command-summary.html"><strong aria-hidden="true">2.</strong> Strategic Command Summary</a><a class="toggle"><div>❱</div></a></li><li><ol class="section"><li class="chapter-item "><a href="1941-q2/german-forces.html"><strong aria-hidden="true">2.1.</strong> German Forces</a></li><li class="chapter-item "><a href="1941-q2/italian-forces.html"><strong aria-hidden="true">2.2.</strong> Italian Forces</a></li><li class="chapter-item "><a href="1941-q2/british-forces.html"><strong aria-hidden="true">2.3.</strong> British &amp; Commonwealth Forces</a></li></ol></li><li class="chapter-item expanded "><a href="1941-q2/air-power-analysis.html"><strong aria-hidden="true">3.</strong> Air Power Analysis</a><a class="toggle"><div>❱</div></a></li><li><ol class="section"><li class="chapter-item "><a href="1941-q2/luftwaffe.html"><strong aria-hidden="true">3.1.</strong> Luftwaffe Operations</a></li><li class="chapter-item "><a href="1941-q2/regia-aeronautica.html"><strong aria-hidden="true">3.2.</strong> Regia Aeronautica Operations</a></li><li class="chapter-item "><a href="1941-q2/raf.html"><strong aria-hidden="true">3.3.</strong> RAF &amp; Commonwealth Air Forces</a></li></ol></li><li class="chapter-item expanded "><a href="1941-q2/equipment-database.html"><strong aria-hidden="true">4.</strong> Equipment Database</a></li><li class="chapter-item expanded affix "><li class="spacer"></li><li class="chapter-item expanded affix "><li class="part-title">Methodology &amp; Data Quality</li><li class="chapter-item expanded "><a href="methodology/research-methodology.html"><strong aria-hidden="true">5.</strong> Research Methodology</a></li><li class="chapter-item expanded "><a href="methodology/source-hierarchy.html"><strong aria-hidden="true">6.</strong> Source Hierarchy</a></li><li class="chapter-item expanded "><a href="methodology/data-quality.html"><strong aria-hidden="true">7.</strong> Data Quality Standards</a></li><li class="chapter-item expanded "><a href="methodology/bidirectional-validation.html"><strong aria-hidden="true">8.</strong> Bidirectional Validation</a></li><li class="chapter-item expanded "><a href="methodology/witw-mapping.html"><strong aria-hidden="true">9.</strong> WITW Equipment Mapping</a></li><li class="chapter-item expanded affix "><li class="spacer"></li><li class="chapter-item expanded affix "><li class="part-title">Appendices</li><li class="chapter-item expanded "><a href="appendices/glossary.html"><strong aria-hidden="true">10.</strong> Glossary</a></li><li class="chapter-item expanded "><a href="appendices/bibliography.html"><strong aria-hidden="true">11.</strong> Source Bibliography</a></li><li class="chapter-item expanded "><a href="appendices/witw-ids.html"><strong aria-hidden="true">12.</strong> WITW Equipment IDs</a></li><li class="chapter-item expanded "><a href="appendices/squadron-index.html"><strong aria-hidden="true">13.</strong> Squadron Index</a></li></ol>';
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
