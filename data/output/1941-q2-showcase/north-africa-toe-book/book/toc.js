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
        this.innerHTML = '<ol class="chapter"><li class="chapter-item expanded affix "><a href="introduction.html">Introduction</a></li><li class="chapter-item expanded affix "><li class="spacer"></li><li class="chapter-item expanded affix "><li class="part-title">1941 - Second Quarter (April - June)</li><li class="chapter-item expanded "><a href="1941-q2/overview.html"><strong aria-hidden="true">1.</strong> 1941-Q2 Overview</a></li><li class="chapter-item expanded "><a href="1941-q2/british/chapter_7th_armoured_division.html"><strong aria-hidden="true">2.</strong> 7th Armoured Division</a></li><li class="chapter-item expanded "><a href="1941-q2/british/chapter_50th_infantry_division.html"><strong aria-hidden="true">3.</strong> 50th (Northumbrian) Infantry Division</a></li><li class="chapter-item expanded "><a href="1941-q2/british/chapter_2nd_new_zealand_division.html"><strong aria-hidden="true">4.</strong> 2nd New Zealand Division</a></li><li class="chapter-item expanded "><a href="1941-q2/british/chapter_4th_indian_division.html"><strong aria-hidden="true">5.</strong> 4th Indian Infantry Division</a></li><li class="chapter-item expanded "><a href="1941-q2/british/chapter_5th_indian_division.html"><strong aria-hidden="true">6.</strong> 5th Indian Infantry Division</a></li><li class="chapter-item expanded "><a href="1941-q2/british/chapter_9th_australian_division.html"><strong aria-hidden="true">7.</strong> 9th Australian Division</a></li><li class="chapter-item expanded "><a href="1941-q2/british/chapter_1st_south_african_division.html"><strong aria-hidden="true">8.</strong> 1st South African Infantry Division</a></li><li class="chapter-item expanded "><a href="1941-q2/german/chapter_deutsches_afrikakorps.html"><strong aria-hidden="true">9.</strong> Deutsches Afrikakorps</a></li><li class="chapter-item expanded "><a href="1941-q2/german/chapter_15_panzer_division.html"><strong aria-hidden="true">10.</strong> 15. Panzer-Division</a></li><li class="chapter-item expanded "><a href="1941-q2/german/chapter_5_leichte_division.html"><strong aria-hidden="true">11.</strong> 5. leichte Division</a></li><li class="chapter-item expanded "><a href="1941-q2/italian/chapter_132_ariete_division.html"><strong aria-hidden="true">12.</strong> 132ª Divisione corazzata &quot;Ariete&quot;</a></li><li class="chapter-item expanded "><a href="1941-q2/italian/chapter_17_pavia_division.html"><strong aria-hidden="true">13.</strong> 17ª Divisione di fanteria &quot;Pavia&quot;</a></li><li class="chapter-item expanded "><a href="1941-q2/italian/chapter_27_brescia_division.html"><strong aria-hidden="true">14.</strong> 27ª Divisione di fanteria &quot;Brescia&quot;</a></li><li class="chapter-item expanded "><a href="1941-q2/italian/chapter_55_trento_division.html"><strong aria-hidden="true">15.</strong> 55ª Divisione motorizzata &quot;Trento&quot;</a></li><li class="chapter-item expanded "><a href="1941-q2/italian/chapter_sabratha_division.html"><strong aria-hidden="true">16.</strong> 60ª Divisione di fanteria &quot;Sabratha&quot;</a></li><li class="chapter-item expanded "><a href="1941-q2/italian/chapter_101_trieste_division.html"><strong aria-hidden="true">17.</strong> 101ª Divisione motorizzata &quot;Trieste&quot;</a></li><li class="chapter-item expanded "><a href="1941-q2/italian/chapter_25_bologna_division.html"><strong aria-hidden="true">18.</strong> 25ª Divisione di Fanteria &quot;Bologna&quot;</a></li><li class="chapter-item expanded "><a href="1941-q2/italian/chapter_savona_division.html"><strong aria-hidden="true">19.</strong> 55ª Divisione di Fanteria &quot;Savona&quot;</a></li><li class="chapter-item expanded affix "><li class="spacer"></li><li class="chapter-item expanded affix "><li class="part-title">Methodology &amp; Data Quality</li><li class="chapter-item expanded "><a href="methodology/research-methodology.html"><strong aria-hidden="true">20.</strong> Research Methodology</a></li><li class="chapter-item expanded "><a href="methodology/source-hierarchy.html"><strong aria-hidden="true">21.</strong> Source Hierarchy</a></li><li class="chapter-item expanded "><a href="methodology/data-quality.html"><strong aria-hidden="true">22.</strong> Data Quality Standards</a></li><li class="chapter-item expanded "><a href="methodology/validation.html"><strong aria-hidden="true">23.</strong> Validation Process</a></li><li class="chapter-item expanded affix "><li class="spacer"></li><li class="chapter-item expanded affix "><li class="part-title">Appendices</li><li class="chapter-item expanded "><a href="appendices/glossary.html"><strong aria-hidden="true">24.</strong> Glossary of Terms</a></li><li class="chapter-item expanded "><a href="appendices/bibliography.html"><strong aria-hidden="true">25.</strong> Source Bibliography</a></li><li class="chapter-item expanded "><a href="appendices/unit-index.html"><strong aria-hidden="true">26.</strong> Unit Index</a></li></ol>';
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
