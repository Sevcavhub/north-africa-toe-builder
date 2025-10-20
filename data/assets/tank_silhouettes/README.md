# Tank Silhouettes for TO&E Diagrams

This directory contains tank silhouette images for generating organizational diagrams.

## Directory Structure

```
tank_silhouettes/
├── british/       # British & Commonwealth AFVs
├── german/        # German Wehrmacht AFVs
├── italian/       # Italian Regio Esercito AFVs
└── american/      # US Army AFVs
```

## Sourcing Silhouettes

### Option 1: Wikimedia Commons (PUBLIC DOMAIN) ⭐ RECOMMENDED

**Advantages:**
- Public domain, free to use
- Historically accurate
- High quality images

**British Tanks Needed for 7th Armoured Division:**

1. **M3 Stuart (Honey)**
   - URL: https://commons.wikimedia.org/wiki/File:M3_Stuart_light_tank.svg
   - Used by: 3rd RTR, 5th RTR, 8th Hussars (recce troops)

2. **M3 Grant (Lee)**
   - URL: https://commons.wikimedia.org/wiki/File:M3_Lee_tank.svg
   - Used by: 8th Hussars (main tank squadrons)

3. **Crusader Mk III**
   - URL: https://commons.wikimedia.org/wiki/File:Crusader_tank_Mk_III.svg
   - Used by: 3rd RTR, 5th RTR, 22nd Armoured Brigade regiments

**Download Instructions:**
```bash
# Navigate to Wikimedia page, click "Download" button, select PNG or SVG format
# Save to appropriate directory (e.g., tank_silhouettes/british/m3_stuart.png)
```

### Option 2: OnWar.com Technical Drawings

OnWar provides side-view technical drawings for most AFVs. These can be converted to silhouettes:

1. Visit: https://www.onwar.com/tanks/uk/uk_c_crusader.htm
2. Save technical drawing image
3. Convert to silhouette using image editor (increase contrast, remove detail)

### Option 3: Generate Simple SVG Shapes

For rapid prototyping, create basic tank shapes:

```svg
<!-- Simple tank silhouette template -->
<svg width="100" height="40" xmlns="http://www.w3.org/2000/svg">
  <!-- Hull -->
  <rect x="10" y="15" width="70" height="20" fill="black"/>
  <!-- Turret -->
  <rect x="30" y="5" width="30" height="15" fill="black"/>
  <!-- Gun -->
  <rect x="60" y="10" width="30" height="3" fill="black"/>
  <!-- Tracks -->
  <ellipse cx="25" cy="35" rx="15" ry="5" fill="black"/>
  <ellipse cx="65" cy="35" rx="15" ry="5" fill="black"/>
</svg>
```

## Naming Convention

Use lowercase with underscores:
- `m3_stuart.png`
- `m3_grant.png`
- `crusader_mk3.png`
- `pzkw_iii_ausf_j.png`
- `pzkw_iv_ausf_f2.png`

## Image Specifications

**For Graphviz/SVG diagrams:**
- Format: PNG or SVG
- Size: 100-150px width (height auto)
- Background: Transparent
- Color: Black silhouette

**For MDBook embedding:**
- Format: SVG preferred (scalable)
- Fallback: PNG at 150px width

## Already Available

German tanks in `Resource Documents/`:
- ✅ Panzer II Ausf. F.png
- ✅ Panzer III Ausf. J.png
- ✅ Panzer IV Ausf. F2.png
- ✅ Sd.Kfz 222.png

Copy these to `tank_silhouettes/german/` with proper naming:
```bash
cp "Resource Documents/Panzer III Ausf. J.png" tank_silhouettes/german/pzkw_iii_ausf_j.png
cp "Resource Documents/Panzer IV Ausf. F2.png" tank_silhouettes/german/pzkw_iv_ausf_f2.png
```

## British Tanks Priority List (North Africa 1941-43)

**Light Tanks:**
- [ ] M3 Stuart (Honey)
- [ ] Mk VI Light Tank

**Cruiser Tanks:**
- [ ] Crusader Mk I/II/III
- [ ] Covenanter
- [ ] Cavalier
- [ ] Cromwell

**Infantry Tanks:**
- [ ] Matilda II
- [ ] Valentine
- [ ] Churchill

**American Lend-Lease:**
- [ ] M3 Grant (Lee)
- [ ] M4 Sherman

## Usage in Diagrams

### Mermaid (MDBook)
Mermaid doesn't support custom images, so use emoji or text labels:
```
🟦 = Tank
⬜ = Vehicle
```

### Graphviz
Reference silhouette files:
```dot
tank1 [shape=none, image="data/assets/tank_silhouettes/british/crusader_mk3.png", label="Crusader Mk III"]
```

### Custom SVG
Embed directly:
```svg
<image href="data/assets/tank_silhouettes/british/m3_grant.png" width="50"/>
```
