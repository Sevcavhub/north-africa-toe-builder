# Guns & Artillery

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

/* Nation-Specific Color Themes */
.datacard.datacard-german {
    background-color: #797768;
    border-color: #1a1a1a;
}

.datacard.datacard-german .datacard-title {
    color: white;
}

.datacard.datacard-german .datacard-subtitle {
    color: white;
}

.datacard.datacard-german .datacard-special-rules {
    color: white;
}

.datacard.datacard-german th {
    background-color: #ECD1A2;
    color: #1a1a1a;
}

.datacard.datacard-german td {
    background-color: #e8dcc8;
    color: #1a1a1a;
}

.datacard.datacard-british {
    background-color: #d4c5a0;
    border-color: #2c2416;
}

.datacard.datacard-british th {
    background-color: #8b7355;
    color: white;
}

.datacard.datacard-british td {
    background-color: #f5f5dc;
    color: #1a1a1a;
}

.datacard.datacard-italian {
    background-color: #739A64;
    border-color: #5a4a2a;
}

.datacard.datacard-italian th {
    background-color: #6b5d3f;
    color: white;
}

.datacard.datacard-italian td {
    background-color: #e8dcc0;
    color: #1a1a1a;
}

.datacard.datacard-american {
    background-color: #b8c5a0;
    border-color: #3a4a2a;
}

.datacard.datacard-american th {
    background-color: #5a6d45;
    color: white;
}

.datacard.datacard-american td {
    background-color: #dce8cf;
    color: #1a1a1a;
}

.datacard.datacard-french {
    background-color: #b8c4d4;
    border-color: #2a3a4a;
}

.datacard.datacard-french th {
    background-color: #4a5a6d;
    color: white;
}

.datacard.datacard-french td {
    background-color: #d8e4f4;
    color: #1a1a1a;
}

.datacard-header {
    display: flex;
    gap: 10px;
    margin-bottom: 8px;
    align-items: center;
}

.datacard-silhouette {
    width: 140px;
    height: 70px;
    background-color: transparent;
    border: none;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    padding: 5px;
}

.datacard-silhouette img {
    max-width: 100%;
    max-height: 100%;
    width: auto;
    height: auto;
    object-fit: contain;
    mix-blend-mode: multiply;
}

.datacard-title-block {
    flex: 1;
    text-align: center;
    display: flex;
    flex-direction: column;
    justify-content: center;
}

.datacard-title {
    font-weight: bold;
    font-size: 16px;
    margin: 0;
    line-height: 1.2;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.datacard-subtitle {
    font-size: 9px;
    font-style: italic;
    margin: 2px 0 0 0;
    line-height: 1.2;
}

.datacard-special-rules {
    font-size: 7px;
    font-style: italic;
    margin: 2px 0 0 0;
    line-height: 1.2;
    color: #5a4a3a;
}

.datacard table {
    width: 100%;
    border-collapse: collapse;
    margin: 2px 0;
    font-size: 8px;
}

.datacard th {
    background-color: #8b7355;
    color: white;
    font-weight: bold;
    padding: 1px 2px;
    border: 1px solid #2c2416;
    text-align: center;
    font-size: 7px;
    line-height: 1.0;
}

.datacard td {
    background-color: #f5f5dc;
    border: 1px solid #2c2416;
    padding: 1px 2px;
    text-align: center;
    font-size: 8px;
    line-height: 1.0;
}

.datacard .main-header {
    font-size: 8px;
    font-weight: bold;
}

.armor-modifier-row td {
    font-style: italic;
    font-size: 7px;
    padding: 1px 3px;
}

.datacard-footer {
    display: flex;
    justify-content: space-between;
    margin-top: 5px;
    padding: 3px 5px;
    font-size: 9px;
    font-weight: bold;
}

.datacard-footer .footer-stat {
    flex: 1;
    text-align: center;
}
</style>

---

<div class="datacard-grid">

<div class="datacard datacard-american">
<div class="datacard-header">
<div class="datacard-silhouette">
<span style="color: white; font-size: 10px;">🔲</span>
</div>
<div class="datacard-title-block">
<p class="datacard-title">M1 81MM MORTAR</p>
<p class="datacard-subtitle"></p>
<p class="datacard-subtitle"></p>
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
<td>Unknown</td>
<td>3"</td>
<td>3"</td>
<td>-</td>
<td>N</td>
<td>O</td>
<td>O</td>
<td>81 gun</td>
<td>Turret</td>
<td>-</td>
</tr>
</table>

<div class="datacard-footer">
<div class="footer-stat"><strong>Points:</strong> -</div>
<div class="footer-stat"><strong>BR:</strong> 2</div>
</div>
</div>

<div class="datacard datacard-british">
<div class="datacard-header">
<div class="datacard-silhouette">
<span style="color: white; font-size: 10px;">🔲</span>
</div>
<div class="datacard-title-block">
<p class="datacard-title">FIELD</p>
<p class="datacard-subtitle"></p>
<p class="datacard-subtitle"></p>
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
<td>Artillery</td>
<td>1"</td>
<td>1"</td>
<td>-</td>
<td>N</td>
<td>O</td>
<td>O</td>
<td>None</td>
<td>-</td>
<td>-</td>
</tr>
</table>

<div class="datacard-footer">
<div class="footer-stat"><strong>Points:</strong> 20</div>
<div class="footer-stat"><strong>BR:</strong> 1</div>
</div>
</div>

<div class="datacard datacard-british">
<div class="datacard-header">
<div class="datacard-silhouette">
<span style="color: white; font-size: 10px;">🔲</span>
</div>
<div class="datacard-title-block">
<p class="datacard-title">QF 17-POUNDER</p>
<p class="datacard-subtitle"></p>
<p class="datacard-subtitle"></p>
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
<td>Artillery</td>
<td>1"</td>
<td>1"</td>
<td>-</td>
<td>N</td>
<td>O</td>
<td>O</td>
<td>Self (towed gun)</td>
<td>-</td>
<td>-</td>
</tr>
</table>

<div class="datacard-footer">
<div class="footer-stat"><strong>Points:</strong> 20</div>
<div class="footer-stat"><strong>BR:</strong> 1</div>
</div>
</div>

<div class="datacard datacard-german">
<div class="datacard-header">
<div class="datacard-silhouette">
<span style="color: white; font-size: 10px;">🔲</span>
</div>
<div class="datacard-title-block">
<p class="datacard-title">37MM PAK 36</p>
<p class="datacard-subtitle"></p>
<p class="datacard-subtitle"></p>
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
<td>Artillery</td>
<td>3"</td>
<td>3"</td>
<td>-</td>
<td>N</td>
<td>O</td>
<td>O</td>
<td>PaK36</td>
<td>Turret</td>
<td>-</td>
</tr>
</table>

<div class="datacard-footer">
<div class="footer-stat"><strong>Points:</strong> -</div>
<div class="footer-stat"><strong>BR:</strong> 1</div>
</div>
</div>

<div class="datacard datacard-italian">
<div class="datacard-header">
<div class="datacard-silhouette">
<span style="color: white; font-size: 10px;">🔲</span>
</div>
<div class="datacard-title-block">
<p class="datacard-title">20MM BREDA</p>
<p class="datacard-subtitle"></p>
<p class="datacard-subtitle"></p>
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
<td>Artillery</td>
<td>3"</td>
<td>3"</td>
<td>-</td>
<td>N</td>
<td>O</td>
<td>O</td>
<td>None</td>
<td>-</td>
<td>-</td>
</tr>
</table>

<div class="datacard-footer">
<div class="footer-stat"><strong>Points:</strong> -</div>
<div class="footer-stat"><strong>BR:</strong> 1</div>
</div>
</div>

<div class="datacard datacard-italian">
<div class="datacard-header">
<div class="datacard-silhouette">
<span style="color: white; font-size: 10px;">🔲</span>
</div>
<div class="datacard-title-block">
<p class="datacard-title">20MM CANNONE DA 20/65</p>
<p class="datacard-subtitle"></p>
<p class="datacard-subtitle"></p>
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
<td>Artillery</td>
<td>3"</td>
<td>3"</td>
<td>-</td>
<td>N</td>
<td>O</td>
<td>O</td>
<td>None</td>
<td>-</td>
<td>-</td>
</tr>
</table>

<div class="datacard-footer">
<div class="footer-stat"><strong>Points:</strong> -</div>
<div class="footer-stat"><strong>BR:</strong> 1</div>
</div>
</div>

<div class="datacard datacard-italian">
<div class="datacard-header">
<div class="datacard-silhouette">
<span style="color: white; font-size: 10px;">🔲</span>
</div>
<div class="datacard-title-block">
<p class="datacard-title">47MM CANNONE DA 47/32 M35</p>
<p class="datacard-subtitle"></p>
<p class="datacard-subtitle"></p>
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
<td>Artillery</td>
<td>3"</td>
<td>3"</td>
<td>-</td>
<td>N</td>
<td>O</td>
<td>O</td>
<td>None</td>
<td>-</td>
<td>-</td>
</tr>
</table>

<div class="datacard-footer">
<div class="footer-stat"><strong>Points:</strong> -</div>
<div class="footer-stat"><strong>BR:</strong> 1</div>
</div>
</div>

<div class="datacard datacard-italian">
<div class="datacard-header">
<div class="datacard-silhouette">
<span style="color: white; font-size: 10px;">🔲</span>
</div>
<div class="datacard-title-block">
<p class="datacard-title">75MM CANNONE DA 75/27 MODELLO 11</p>
<p class="datacard-subtitle"></p>
<p class="datacard-subtitle"></p>
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
<td>Artillery</td>
<td>1"</td>
<td>1"</td>
<td>-</td>
<td>N</td>
<td>O</td>
<td>O</td>
<td>None</td>
<td>-</td>
<td>-</td>
</tr>
</table>

<div class="datacard-footer">
<div class="footer-stat"><strong>Points:</strong> -</div>
<div class="footer-stat"><strong>BR:</strong> 1</div>
</div>
</div>

</div>
