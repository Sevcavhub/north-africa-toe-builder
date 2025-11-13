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
        this.innerHTML = '<ol class="chapter"><li class="chapter-item expanded affix "><a href="intro.html">Introduction</a></li><li class="chapter-item expanded affix "><li class="part-title">Historical Context</li><li class="chapter-item expanded "><a href="chapter1/strategic_situation.html"><strong aria-hidden="true">1.</strong> Strategic Situation</a></li><li class="chapter-item expanded "><a href="chapter1/historical_overview.html"><strong aria-hidden="true">2.</strong> Historical Overview</a></li><li class="chapter-item expanded "><a href="chapter1/orders_of_battle.html"><strong aria-hidden="true">3.</strong> Orders of Battle</a></li><li class="chapter-item expanded affix "><li class="part-title">Scenarios</li><li class="chapter-item expanded "><a href="scenarios/overview.html"><strong aria-hidden="true">4.</strong> Scenarios Overview</a><a class="toggle"><div>❱</div></a></li><li><ol class="section"><li class="chapter-item "><a href="scenarios/scenario_01.html"><strong aria-hidden="true">4.1.</strong> Scenario 1</a></li><li class="chapter-item "><a href="scenarios/scenario_02.html"><strong aria-hidden="true">4.2.</strong> Scenario 2</a></li><li class="chapter-item "><a href="scenarios/scenario_03.html"><strong aria-hidden="true">4.3.</strong> Scenario 3</a></li><li class="chapter-item "><a href="scenarios/scenario_04.html"><strong aria-hidden="true">4.4.</strong> Scenario 4</a></li><li class="chapter-item "><a href="scenarios/scenario_05.html"><strong aria-hidden="true">4.5.</strong> Scenario 5</a></li><li class="chapter-item "><a href="scenarios/scenario_06.html"><strong aria-hidden="true">4.6.</strong> Scenario 6</a></li><li class="chapter-item "><a href="scenarios/scenario_07.html"><strong aria-hidden="true">4.7.</strong> Scenario 7</a></li><li class="chapter-item "><a href="scenarios/scenario_08.html"><strong aria-hidden="true">4.8.</strong> Scenario 8</a></li></ol></li><li class="chapter-item expanded "><li class="part-title">Forces</li><li class="chapter-item expanded "><a href="army_lists/british.html"><strong aria-hidden="true">5.</strong> British Forces</a></li><li class="chapter-item expanded "><a href="army_lists/german.html"><strong aria-hidden="true">6.</strong> German Forces</a></li><li class="chapter-item expanded "><a href="army_lists/italian.html"><strong aria-hidden="true">7.</strong> Italian Forces</a></li><li class="chapter-item expanded affix "><li class="part-title">Equipment Datacards</li><li class="chapter-item expanded "><a href="chapter2/tanks.html"><strong aria-hidden="true">8.</strong> Tanks</a></li><li class="chapter-item expanded "><a href="chapter2/vehicles.html"><strong aria-hidden="true">9.</strong> Vehicles</a></li><li class="chapter-item expanded "><a href="chapter2/guns_and_artillery.html"><strong aria-hidden="true">10.</strong> Guns &amp; Artillery</a></li><li class="chapter-item expanded "><a href="chapter2/infantry_weapons.html"><strong aria-hidden="true">11.</strong> Infantry Weapons</a></li><li class="chapter-item expanded "><a href="chapter2/other_equipment.html"><strong aria-hidden="true">12.</strong> Other Equipment</a></li><li class="chapter-item expanded affix "><li class="part-title">Special Rules</li><li class="chapter-item expanded "><a href="special_rules/terrain.html"><strong aria-hidden="true">13.</strong> Terrain Rules</a></li><li class="chapter-item expanded "><a href="special_rules/scenarios.html"><strong aria-hidden="true">14.</strong> Scenario Special Rules</a></li><li class="chapter-item expanded "><a href="special_rules/nations.html"><strong aria-hidden="true">15.</strong> National Special Rules</a></li><li class="chapter-item expanded affix "><li class="part-title">Appendices</li><li class="chapter-item expanded "><a href="appendices/appendix_a.html"><strong aria-hidden="true">16.</strong> Appendix A: Quick Reference</a></li><li class="chapter-item expanded "><a href="appendices/appendix_b.html"><strong aria-hidden="true">17.</strong> Appendix B: Designer&#39;s Notes</a></li><li class="chapter-item expanded "><a href="appendices/appendix_c.html"><strong aria-hidden="true">18.</strong> Appendix C: Historical Sources</a></li></ol>';
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
