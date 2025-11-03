# Tank Datacards - Sample Format (3x2 Layout) - FINAL

<style>
@media print {
    @page {
        size: A4 landscape;
        margin: 10mm;
    }

    .datacard-grid {
        page-break-after: always;
    }

    .datacard {
        page-break-inside: avoid;
    }
}

.datacard-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 15px;
    margin: 20px 0;
}

.datacard {
    border: 3px solid #2c2416;
    padding: 8px;
    background-color: #d4c5a0;
    box-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    font-family: Arial, sans-serif;
}

.datacard-header {
    display: flex;
    gap: 10px;
    margin-bottom: 8px;
    align-items: center;
}

.datacard-silhouette {
    width: 80px;
    height: 60px;
    background-color: #1a1a1a;
    border: 1px solid #333;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
}

.datacard-silhouette img {
    width: 100%;
    height: 100%;
    object-fit: contain;
    filter: brightness(0) invert(1);
}

.datacard-title-block {
    flex: 1;
    text-align: right;
}

.datacard-title {
    font-weight: bold;
    font-size: 14px;
    margin: 0;
    line-height: 1.2;
}

.datacard-subtitle {
    font-size: 9px;
    font-style: italic;
    margin: 2px 0 0 0;
    line-height: 1.2;
}

.datacard table {
    width: 100%;
    border-collapse: collapse;
    margin: 4px 0;
    font-size: 8px;
}

.datacard th {
    background-color: #8b7355;
    color: white;
    font-weight: bold;
    padding: 2px 3px;
    border: 1px solid #2c2416;
    text-align: center;
    font-size: 7px;
    line-height: 1.1;
}

.datacard td {
    background-color: #f5f5dc;
    border: 1px solid #2c2416;
    padding: 2px 3px;
    text-align: center;
    font-size: 8px;
    line-height: 1.1;
}

.datacard .main-header {
    font-size: 8px;
    font-weight: bold;
}
</style>

---

<div class="datacard-grid">

<!-- Card 1: Matilda II -->
<div class="datacard">
<div class="datacard-header">
<div class="datacard-silhouette">
<span style="color: white; font-size: 10px;">🔲</span>
</div>
<div class="datacard-title-block">
<p class="datacard-title">MATILDA II</p>
<p class="datacard-subtitle">1940-1945 | Infantry tank</p>
</div>
</div>

<table>
<tr>
<th class="main-header">VEHICLE</th>
<th class="main-header" colspan="3">MOVEMENT</th>
<th class="main-header" colspan="3">ARMOUR</th>
<th class="main-header" colspan="3">ARMAMENT</th>
</tr>
<tr>
<th></th>
<th>Off-Road</th>
<th>Road</th>
<th>Special</th>
<th>F</th>
<th>S</th>
<th>R</th>
<th>Weapon</th>
<th>Mount</th>
<th>Ammo</th>
</tr>
<tr>
<td>Tank</td>
<td>5"</td>
<td>8"</td>
<td>-</td>
<td>K</td>
<td>K</td>
<td>L</td>
<td>2pdr</td>
<td>Turret</td>
<td>9</td>
</tr>
<tr>
<td></td>
<td></td>
<td></td>
<td></td>
<td></td>
<td></td>
<td></td>
<td>MG</td>
<td>Co-ax</td>
<td>-</td>
</tr>
</table>

<table>
<tr>
<th class="main-header" colspan="2">WEAPON</th>
<th class="main-header">AMMO</th>
<th class="main-header">HE</th>
<th class="main-header" colspan="6">RANGE</th>
</tr>
<tr>
<th></th>
<th></th>
<th></th>
<th>weight</th>
<th>0-10"</th>
<th>10-20"</th>
<th>20-30"</th>
<th>30-40"</th>
<th>40-50"</th>
<th>50-70"</th>
</tr>
<tr>
<td>2pdr</td>
<td></td>
<td>HE</td>
<td>Light</td>
<td>-</td>
<td>-</td>
<td>-</td>
<td>-</td>
<td>-</td>
<td>-</td>
</tr>
<tr>
<td>2pdr</td>
<td></td>
<td>AP</td>
<td>-</td>
<td>5</td>
<td>5</td>
<td>4</td>
<td>3</td>
<td>2</td>
<td>-</td>
</tr>
</table>
</div>

<!-- Card 2: Stuart I -->
<div class="datacard">
<div class="datacard-header">
<div class="datacard-silhouette">
<span style="color: white; font-size: 10px;">🔲</span>
</div>
<div class="datacard-title-block">
<p class="datacard-title">STUART I (M3 LIGHT)</p>
<p class="datacard-subtitle">1941-1943 | Light tank</p>
</div>
</div>

<table>
<tr>
<th class="main-header">VEHICLE</th>
<th class="main-header" colspan="3">MOVEMENT</th>
<th class="main-header" colspan="3">ARMOUR</th>
<th class="main-header" colspan="3">ARMAMENT</th>
</tr>
<tr>
<th></th>
<th>Off-Road</th>
<th>Road</th>
<th>Special</th>
<th>F</th>
<th>S</th>
<th>R</th>
<th>Weapon</th>
<th>Mount</th>
<th>Ammo</th>
</tr>
<tr>
<td>Tank</td>
<td>8"</td>
<td>12"</td>
<td>-</td>
<td>N</td>
<td>O</td>
<td>O</td>
<td>37mm</td>
<td>Turret</td>
<td>-</td>
</tr>
<tr>
<td></td>
<td></td>
<td></td>
<td></td>
<td></td>
<td></td>
<td></td>
<td>MG</td>
<td>Co-ax</td>
<td>-</td>
</tr>
</table>

<table>
<tr>
<th class="main-header" colspan="2">WEAPON</th>
<th class="main-header">AMMO</th>
<th class="main-header">HE</th>
<th class="main-header" colspan="6">RANGE</th>
</tr>
<tr>
<th></th>
<th></th>
<th></th>
<th>weight</th>
<th>0-10"</th>
<th>10-20"</th>
<th>20-30"</th>
<th>30-40"</th>
<th>40-50"</th>
<th>50-70"</th>
</tr>
<tr>
<td>37mm</td>
<td></td>
<td>HE</td>
<td>Light</td>
<td>-</td>
<td>-</td>
<td>-</td>
<td>-</td>
<td>-</td>
<td>-</td>
</tr>
<tr>
<td>37mm</td>
<td></td>
<td>AP</td>
<td>-</td>
<td>3</td>
<td>3</td>
<td>2</td>
<td>1</td>
<td>0</td>
<td>-</td>
</tr>
</table>
</div>

<!-- Card 3: Light Tank Mk VI (no weapon table) -->
<div class="datacard">
<div class="datacard-header">
<div class="datacard-silhouette">
<span style="color: white; font-size: 10px;">🔲</span>
</div>
<div class="datacard-title-block">
<p class="datacard-title">LIGHT TANK MK VI</p>
<p class="datacard-subtitle">1936-1940 | Reconnaissance tank</p>
</div>
</div>

<table>
<tr>
<th class="main-header">VEHICLE</th>
<th class="main-header" colspan="3">MOVEMENT</th>
<th class="main-header" colspan="3">ARMOUR</th>
<th class="main-header" colspan="3">ARMAMENT</th>
</tr>
<tr>
<th></th>
<th>Off-Road</th>
<th>Road</th>
<th>Special</th>
<th>F</th>
<th>S</th>
<th>R</th>
<th>Weapon</th>
<th>Mount</th>
<th>Ammo</th>
</tr>
<tr>
<td>Tank</td>
<td>8"</td>
<td>12"</td>
<td>-</td>
<td>N</td>
<td>O</td>
<td>O</td>
<td>MG</td>
<td>Turret</td>
<td>-</td>
</tr>
</table>
</div>

<!-- Card 4: Valentine III -->
<div class="datacard">
<div class="datacard-header">
<div class="datacard-silhouette">
<span style="color: white; font-size: 10px;">🔲</span>
</div>
<div class="datacard-title-block">
<p class="datacard-title">VALENTINE III</p>
<p class="datacard-subtitle">1941-1944 | Infantry tank</p>
</div>
</div>

<table>
<tr>
<th class="main-header">VEHICLE</th>
<th class="main-header" colspan="3">MOVEMENT</th>
<th class="main-header" colspan="3">ARMOUR</th>
<th class="main-header" colspan="3">ARMAMENT</th>
</tr>
<tr>
<th></th>
<th>Off-Road</th>
<th>Road</th>
<th>Special</th>
<th>F</th>
<th>S</th>
<th>R</th>
<th>Weapon</th>
<th>Mount</th>
<th>Ammo</th>
</tr>
<tr>
<td>Tank</td>
<td>5"</td>
<td>8"</td>
<td>-</td>
<td>K</td>
<td>K</td>
<td>L</td>
<td>2pdr</td>
<td>Turret</td>
<td>-</td>
</tr>
<tr>
<td></td>
<td></td>
<td></td>
<td></td>
<td></td>
<td></td>
<td></td>
<td>MG</td>
<td>Co-ax</td>
<td>-</td>
</tr>
</table>

<table>
<tr>
<th class="main-header" colspan="2">WEAPON</th>
<th class="main-header">AMMO</th>
<th class="main-header">HE</th>
<th class="main-header" colspan="6">RANGE</th>
</tr>
<tr>
<th></th>
<th></th>
<th></th>
<th>weight</th>
<th>0-10"</th>
<th>10-20"</th>
<th>20-30"</th>
<th>30-40"</th>
<th>40-50"</th>
<th>50-70"</th>
</tr>
<tr>
<td>2pdr</td>
<td></td>
<td>HE</td>
<td>Light</td>
<td>-</td>
<td>-</td>
<td>-</td>
<td>-</td>
<td>-</td>
<td>-</td>
</tr>
<tr>
<td>2pdr</td>
<td></td>
<td>AP</td>
<td>-</td>
<td>5</td>
<td>5</td>
<td>4</td>
<td>3</td>
<td>2</td>
<td>-</td>
</tr>
</table>
</div>

<!-- Card 5: M4 Sherman (Medium tank with HE capability) -->
<div class="datacard">
<div class="datacard-header">
<div class="datacard-silhouette">
<span style="color: white; font-size: 10px;">🔲</span>
</div>
<div class="datacard-title-block">
<p class="datacard-title">M4 SHERMAN</p>
<p class="datacard-subtitle">1942-1945 | Medium tank</p>
</div>
</div>

<table>
<tr>
<th class="main-header">VEHICLE</th>
<th class="main-header" colspan="3">MOVEMENT</th>
<th class="main-header" colspan="3">ARMOUR</th>
<th class="main-header" colspan="3">ARMAMENT</th>
</tr>
<tr>
<th></th>
<th>Off-Road</th>
<th>Road</th>
<th>Special</th>
<th>F</th>
<th>S</th>
<th>R</th>
<th>Weapon</th>
<th>Mount</th>
<th>Ammo</th>
</tr>
<tr>
<td>Tank</td>
<td>9"</td>
<td>14"</td>
<td>-</td>
<td>K</td>
<td>L</td>
<td>N</td>
<td>75mm</td>
<td>Turret</td>
<td>9</td>
</tr>
<tr>
<td></td>
<td></td>
<td></td>
<td></td>
<td></td>
<td></td>
<td></td>
<td>MG</td>
<td>Co-ax</td>
<td>-</td>
</tr>
<tr>
<td></td>
<td></td>
<td></td>
<td></td>
<td></td>
<td></td>
<td></td>
<td>MG</td>
<td>Hull</td>
<td>-</td>
</tr>
</table>

<table>
<tr>
<th class="main-header" colspan="2">WEAPON</th>
<th class="main-header">AMMO</th>
<th class="main-header">HE</th>
<th class="main-header" colspan="6">RANGE</th>
</tr>
<tr>
<th></th>
<th></th>
<th></th>
<th>weight</th>
<th>0-10"</th>
<th>10-20"</th>
<th>20-30"</th>
<th>30-40"</th>
<th>40-50"</th>
<th>50-70"</th>
</tr>
<tr>
<td>75mm</td>
<td></td>
<td>HE</td>
<td>Medium</td>
<td>3</td>
<td>3</td>
<td>3</td>
<td>3</td>
<td>3</td>
<td>3</td>
</tr>
<tr>
<td>75mm</td>
<td></td>
<td>AP</td>
<td>-</td>
<td>6</td>
<td>6</td>
<td>5</td>
<td>4</td>
<td>3</td>
<td>-</td>
</tr>
</table>
</div>

<!-- Card 6: Panzer IV F2 (German Medium tank) -->
<div class="datacard">
<div class="datacard-header">
<div class="datacard-silhouette">
<span style="color: white; font-size: 10px;">🔲</span>
</div>
<div class="datacard-title-block">
<p class="datacard-title">PANZER IV AUSF. F2</p>
<p class="datacard-subtitle">1942-1943 | Medium tank</p>
</div>
</div>

<table>
<tr>
<th class="main-header">VEHICLE</th>
<th class="main-header" colspan="3">MOVEMENT</th>
<th class="main-header" colspan="3">ARMOUR</th>
<th class="main-header" colspan="3">ARMAMENT</th>
</tr>
<tr>
<th></th>
<th>Off-Road</th>
<th>Road</th>
<th>Special</th>
<th>F</th>
<th>S</th>
<th>R</th>
<th>Weapon</th>
<th>Mount</th>
<th>Ammo</th>
</tr>
<tr>
<td>Tank</td>
<td>10"</td>
<td>14"</td>
<td>-</td>
<td>L</td>
<td>N</td>
<td>N</td>
<td>75mm L/43</td>
<td>Turret</td>
<td>-</td>
</tr>
<tr>
<td></td>
<td></td>
<td></td>
<td></td>
<td></td>
<td></td>
<td></td>
<td>MG</td>
<td>Co-ax</td>
<td>-</td>
</tr>
<tr>
<td></td>
<td></td>
<td></td>
<td></td>
<td></td>
<td></td>
<td></td>
<td>MG</td>
<td>Hull</td>
<td>-</td>
</tr>
</table>

<table>
<tr>
<th class="main-header" colspan="2">WEAPON</th>
<th class="main-header">AMMO</th>
<th class="main-header">HE</th>
<th class="main-header" colspan="6">RANGE</th>
</tr>
<tr>
<th></th>
<th></th>
<th></th>
<th>weight</th>
<th>0-10"</th>
<th>10-20"</th>
<th>20-30"</th>
<th>30-40"</th>
<th>40-50"</th>
<th>50-70"</th>
</tr>
<tr>
<td>75mm L/43</td>
<td></td>
<td>HE</td>
<td>Medium</td>
<td>4</td>
<td>4</td>
<td>4</td>
<td>4</td>
<td>4</td>
<td>4</td>
</tr>
<tr>
<td>75mm L/43</td>
<td></td>
<td>AP</td>
<td>-</td>
<td>7</td>
<td>7</td>
<td>6</td>
<td>5</td>
<td>4</td>
<td>-</td>
</tr>
</table>
</div>

</div>

---

## Format Notes

### Bottom Weapon Performance Table Structure

```
| WEAPON | [blank] | AMMO | HE     | RANGE (6 columns)...
|        |         |      | weight | 0-10" | 10-20" | ...
| 75mm   |         | HE   | Medium | 3     | 3      | ...
| 75mm   |         | AP   | -      | 6     | 6      | ...
```

### HE Shell Weight Classifications
- **Light**: 20-49mm caliber (37mm, 40mm 2-pdr, 45mm)
- **Medium**: 50-104mm caliber (50mm, 75mm, 76mm, 88mm)
- **Heavy**: 105mm+ caliber (105mm, 120mm, 150mm howitzers)

### Data Fields Shown
1. **HE weight** (Light/Medium/Heavy) - Based on caliber classification
2. **HE effectiveness range** - Actual HE penetration/effect at each range band
3. **AP values** - Armor penetration at each range band (from penetration_converter)

Note: The "weight" subheader under HE column shows shell weight class, NOT HE effectiveness (which would be dice/target notation like "4/4+")
