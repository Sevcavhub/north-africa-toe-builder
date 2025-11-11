# North Africa Campaign Books - Landing Page

## Overview

Professional landing page for the North Africa Campaign Books project, serving as the unified navigation hub for all 12 battle books.

## File Structure

```
books/
├── index.html                 # Landing page (main entry point)
├── compass/book/book/         # Operation Compass (1940q4)
├── sonnenblume/book/book/     # Operation Sonnenblume (1941q1)
├── tobruk/book/book/          # Siege of Tobruk (1941q2-q3)
├── battleaxe/book/book/       # Operation Battleaxe (1941q2)
├── crusader/book/book/        # Operation Crusader (1941q4)
├── gazala/book/book/          # Battle of Gazala (1942q2)
├── first_alamein/book/book/   # First El Alamein (1942q3)
├── alam_halfa/book/book/      # Alam Halfa (1942q3)
├── second_alamein/book/book/  # Second El Alamein (1942q4)
├── torch/book/book/           # Operation Torch (1942q4)
├── tunisia/book/book/         # Tunisia Campaign (1943q1-q2)
└── mareth/book/book/          # Mareth Line (1943q1)
```

## Design Features

### Visual Theme
- **Color Palette**: Desert tan (#C9A77C), olive drab (#6B7F3D), military greens
- **Typography**: Serif fonts (Georgia, Palatino) for historical feel
- **Layout**: Responsive grid system (desktop + mobile)
- **Icons**: Military emoji (🎖️) for favicon and visual accents

### Sections

1. **Header/Hero**
   - Project title with military medal icon
   - Subtitle: "1940-1943: The Desert War"
   - Introduction paragraph explaining the project

2. **About Section**
   - Project overview (database scope, research depth)
   - Features grid (4 cards):
     - Equipment Datacards (V5.5 format)
     - Historical Scenarios (45+ scenarios)
     - Orders of Battle (organizational hierarchies)
     - Research Citations (252 references)

3. **Period Sections** (3 sections)
   - Early War (1940-1941): 5 books
   - Mid War (1942): 4 books
   - Late War (1942-1943): 3 books

4. **Interactive Tools**
   - Placeholder for future Flask tools
   - Scenario builder and equipment database

5. **Footer**
   - Copyright notice
   - Links: GitHub, About, Bibliography

### Book Cards

Each battle book displays:
- **Title**: Operation/battle name
- **Date**: Quarter designation (e.g., "Q4 1940")
- **Description**: 2-3 sentence historical summary
- **Link**: "Read Book →" arrow with hover animation

### Interactive Elements

- **Hover Effects**: Cards lift on hover with shadow
- **Smooth Scrolling**: Anchor links animate smoothly
- **Fade-in Animation**: Period sections fade in on scroll
- **Responsive Design**: Mobile-friendly layout (breakpoint at 768px)

## Technical Details

### Single-File Architecture
- **CSS**: Embedded in `<style>` tag (no external stylesheets)
- **JavaScript**: Minimal inline script for smooth scrolling
- **Favicon**: Data URI SVG (military medal emoji)
- **Size**: 24KB (fast loading)

### GitHub Pages Compatible
- No build process required
- All paths are relative
- Valid HTML5
- No external dependencies

### Browser Support
- Modern browsers (Chrome, Firefox, Safari, Edge)
- Mobile responsive (iOS Safari, Chrome Mobile)
- Graceful degradation for older browsers

## Deployment

### Local Testing
```bash
# Open in browser
start books/index.html

# Or use Python HTTP server
cd books
python -m http.server 8000
# Visit http://localhost:8000
```

### GitHub Pages
1. Commit `books/index.html` to repository
2. Enable GitHub Pages in repository settings
3. Set source to `main` branch, `/books` folder
4. Access at: `https://yourusername.github.io/north-africa-toe-builder/`

### Customization

To update book links or descriptions:
1. Edit `books/index.html`
2. Find the relevant `.book-card` section
3. Update `<h3>`, `<span class="book-date">`, or `<p class="book-description">`
4. Commit and push changes

To change color theme:
1. Edit CSS variables in `:root` selector
2. Modify `--desert-tan`, `--olive-drab`, etc.
3. Preview changes locally before committing

## Future Enhancements

- [ ] Add "Interactive Tools" Flask application
- [ ] Create scenario search/filter functionality
- [ ] Add equipment database browser
- [ ] Generate book cover thumbnails for cards
- [ ] Add progress indicators (completion status per book)
- [ ] Create RSS/Atom feed for updates
- [ ] Add print stylesheet for PDF generation

## Credits

Created for the North Africa Campaign Books project.
Part of Phase 9B: BattleGroup Book Generation.

Last updated: November 11, 2025
