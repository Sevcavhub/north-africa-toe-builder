# Vehicles

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
    background-color: #c8b88a;
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
</style>

---

<div class="datacard-grid">

<div class="datacard datacard-american">
<div class="datacard-header">
<div class="datacard-silhouette">
<span style="color: white; font-size: 10px;">🔲</span>
</div>
<div class="datacard-title-block">
<p class="datacard-title">M2 HALFTRACK</p>
<p class="datacard-subtitle">1940-1945 | Halftrack</p>
<p class="datacard-special-rules">American Firepower Doctrine, Desert Adapted, Half-Tracked, Thin Armor, Transport</p>
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
<td>Halftrack</td>
<td>8"</td>
<td>12"</td>
<td>-</td>
<td>N</td>
<td>O</td>
<td>O</td>
<td>None</td>
<td>-</td>
<td>-</td>
</tr>

</table>

</div>

<div class="datacard datacard-british">
<div class="datacard-header">
<div class="datacard-silhouette">
<span style="color: white; font-size: 10px;">🔲</span>
</div>
<div class="datacard-title-block">
<p class="datacard-title">A9 RECOVERY</p>
<p class="datacard-subtitle">1940-1945 | Vehicle</p>
<p class="datacard-special-rules">British Resolve, Desert Adapted, Recovery Vehicle, Thin Armor</p>
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
<td>Vehicle</td>
<td>8"</td>
<td>12"</td>
<td>-</td>
<td>N</td>
<td>O</td>
<td>O</td>
<td>None</td>
<td>-</td>
<td>-</td>
</tr>

</table>

</div>

<div class="datacard datacard-british">
<div class="datacard-header">
<div class="datacard-silhouette">
<span style="color: white; font-size: 10px;">🔲</span>
</div>
<div class="datacard-title-block">
<p class="datacard-title">AUSTIN K2</p>
<p class="datacard-subtitle">1940-1945 | Vehicle</p>
<p class="datacard-special-rules">British Resolve, Desert Adapted, Thin Armor</p>
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
<td>Vehicle</td>
<td>6"</td>
<td>24"</td>
<td>-</td>
<td>Soft-Skinned</td>
<td>-</td>
<td>-</td>
<td>None</td>
<td>-</td>
<td>-</td>
</tr>

</table>

</div>

<div class="datacard datacard-british">
<div class="datacard-header">
<div class="datacard-silhouette">
<span style="color: white; font-size: 10px;">🔲</span>
</div>
<div class="datacard-title-block">
<p class="datacard-title">BEDFORD MW</p>
<p class="datacard-subtitle">1940-1945 | Vehicle</p>
<p class="datacard-special-rules">British Resolve, Desert Adapted, Thin Armor</p>
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
<td>Vehicle</td>
<td>6"</td>
<td>24"</td>
<td>-</td>
<td>Soft-Skinned</td>
<td>-</td>
<td>-</td>
<td>None</td>
<td>-</td>
<td>-</td>
</tr>

</table>

</div>

<div class="datacard datacard-british">
<div class="datacard-header">
<div class="datacard-silhouette">
<span style="color: white; font-size: 10px;">🔲</span>
</div>
<div class="datacard-title-block">
<p class="datacard-title">BEDFORD MW 15CWT</p>
<p class="datacard-subtitle">1940-1945 | Vehicle</p>
<p class="datacard-special-rules">British Resolve, Desert Adapted, Thin Armor</p>
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
<td>Vehicle</td>
<td>8"</td>
<td>12"</td>
<td>-</td>
<td>N</td>
<td>O</td>
<td>O</td>
<td>None</td>
<td>-</td>
<td>-</td>
</tr>

</table>

</div>

<div class="datacard datacard-british">
<div class="datacard-header">
<div class="datacard-silhouette">
<span style="color: white; font-size: 10px;">🔲</span>
</div>
<div class="datacard-title-block">
<p class="datacard-title">BEDFORD QL</p>
<p class="datacard-subtitle">1940-1945 | Vehicle</p>
<p class="datacard-special-rules">British Resolve, Desert Adapted, Thin Armor</p>
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
<td>Vehicle</td>
<td>6"</td>
<td>24"</td>
<td>-</td>
<td>Soft-Skinned</td>
<td>-</td>
<td>-</td>
<td>None</td>
<td>-</td>
<td>-</td>
</tr>

</table>

</div>

<div class="datacard datacard-british">
<div class="datacard-header">
<div class="datacard-silhouette">
<span style="color: white; font-size: 10px;">🔲</span>
</div>
<div class="datacard-title-block">
<p class="datacard-title">CMP TRUCKS (ALL VARIANTS)</p>
<p class="datacard-subtitle">1940-1945 | Vehicle</p>
<p class="datacard-special-rules">British Resolve, Desert Adapted, Thin Armor, Transport</p>
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
<td>Vehicle</td>
<td>8"</td>
<td>12"</td>
<td>-</td>
<td>N</td>
<td>O</td>
<td>O</td>
<td>None</td>
<td>-</td>
<td>-</td>
</tr>

</table>

</div>

<div class="datacard datacard-british">
<div class="datacard-header">
<div class="datacard-silhouette">
<span style="color: white; font-size: 10px;">🔲</span>
</div>
<div class="datacard-title-block">
<p class="datacard-title">CHEVROLET C15A</p>
<p class="datacard-subtitle">1940-1945 | Vehicle</p>
<p class="datacard-special-rules">British Resolve, Desert Adapted, Thin Armor</p>
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
<td>Vehicle</td>
<td>8"</td>
<td>12"</td>
<td>-</td>
<td>N</td>
<td>O</td>
<td>O</td>
<td>None</td>
<td>-</td>
<td>-</td>
</tr>

</table>

</div>

<div class="datacard datacard-british">
<div class="datacard-header">
<div class="datacard-silhouette">
<span style="color: white; font-size: 10px;">🔲</span>
</div>
<div class="datacard-title-block">
<p class="datacard-title">DAIMLER ARMORED CAR</p>
<p class="datacard-subtitle">1940-1945 | Armored Car</p>
<p class="datacard-special-rules">British Resolve, Desert Adapted, Thin Armor, Wheeled</p>
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
<td>Armored Car</td>
<td>8"</td>
<td>24"</td>
<td>-</td>
<td>N</td>
<td>O</td>
<td>O</td>
<td>None</td>
<td>-</td>
<td>-</td>
</tr>

</table>

</div>

<div class="datacard datacard-british">
<div class="datacard-header">
<div class="datacard-silhouette">
<span style="color: white; font-size: 10px;">🔲</span>
</div>
<div class="datacard-title-block">
<p class="datacard-title">FORD F15 15CWT</p>
<p class="datacard-subtitle">1940-1945 | Vehicle</p>
<p class="datacard-special-rules">British Resolve, Desert Adapted, Thin Armor</p>
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
<td>Vehicle</td>
<td>8"</td>
<td>12"</td>
<td>-</td>
<td>N</td>
<td>O</td>
<td>O</td>
<td>None</td>
<td>-</td>
<td>-</td>
</tr>

</table>

</div>

<div class="datacard datacard-british">
<div class="datacard-header">
<div class="datacard-silhouette">
<span style="color: white; font-size: 10px;">🔲</span>
</div>
<div class="datacard-title-block">
<p class="datacard-title">HUMBER MK I</p>
<p class="datacard-subtitle">1940-1945 | Armored Car</p>
<p class="datacard-special-rules">British Resolve, Desert Adapted, Thin Armor</p>
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
<td>Armored Car</td>
<td>8"</td>
<td>12"</td>
<td>-</td>
<td>N</td>
<td>O</td>
<td>O</td>
<td>None</td>
<td>-</td>
<td>-</td>
</tr>

</table>

</div>

<div class="datacard datacard-british">
<div class="datacard-header">
<div class="datacard-silhouette">
<span style="color: white; font-size: 10px;">🔲</span>
</div>
<div class="datacard-title-block">
<p class="datacard-title">MARMON-HERRINGTON</p>
<p class="datacard-subtitle">1940-1945 | Armored Car</p>
<p class="datacard-special-rules">British Resolve, Desert Adapted, Thin Armor</p>
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
<td>Armored Car</td>
<td>8"</td>
<td>12"</td>
<td>-</td>
<td>N</td>
<td>O</td>
<td>O</td>
<td>None</td>
<td>-</td>
<td>-</td>
</tr>

</table>

</div>

<div class="datacard datacard-british">
<div class="datacard-header">
<div class="datacard-silhouette">
<span style="color: white; font-size: 10px;">🔲</span>
</div>
<div class="datacard-title-block">
<p class="datacard-title">MORRIS C8</p>
<p class="datacard-subtitle">1940-1945 | Vehicle</p>
<p class="datacard-special-rules">British Resolve, Desert Adapted, Thin Armor</p>
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
<td>Vehicle</td>
<td>8"</td>
<td>12"</td>
<td>-</td>
<td>N</td>
<td>O</td>
<td>O</td>
<td>None</td>
<td>-</td>
<td>-</td>
</tr>

</table>

</div>

<div class="datacard datacard-british">
<div class="datacard-header">
<div class="datacard-silhouette">
<span style="color: white; font-size: 10px;">🔲</span>
</div>
<div class="datacard-title-block">
<p class="datacard-title">UNIVERSAL CARRIER</p>
<p class="datacard-subtitle">1940-1945 | Vehicle</p>
<p class="datacard-special-rules">British Resolve, Desert Adapted, Thin Armor</p>
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
<td>Vehicle</td>
<td>8"</td>
<td>12"</td>
<td>-</td>
<td>N</td>
<td>O</td>
<td>O</td>
<td>None</td>
<td>-</td>
<td>-</td>
</tr>

</table>

</div>

<div class="datacard datacard-german">
<div class="datacard-header">
<div class="datacard-silhouette">
<span style="color: white; font-size: 10px;">🔲</span>
</div>
<div class="datacard-title-block">
<p class="datacard-title">HENSCHEL TYPE 33G1</p>
<p class="datacard-subtitle">1940-1945 | Vehicle</p>
<p class="datacard-special-rules">Desert Adapted, German Tactical Doctrine, Thin Armor</p>
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
<td>Vehicle</td>
<td>8"</td>
<td>12"</td>
<td>-</td>
<td>N</td>
<td>O</td>
<td>O</td>
<td>None</td>
<td>-</td>
<td>-</td>
</tr>

</table>

</div>

<div class="datacard datacard-german">
<div class="datacard-header">
<div class="datacard-silhouette">
<span style="color: white; font-size: 10px;">🔲</span>
</div>
<div class="datacard-title-block">
<p class="datacard-title">MERCEDES-BENZ L3000A</p>
<p class="datacard-subtitle">1940-1945 | Vehicle</p>
<p class="datacard-special-rules">Desert Adapted, German Tactical Doctrine, Thin Armor</p>
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
<td>Vehicle</td>
<td>8"</td>
<td>12"</td>
<td>-</td>
<td>N</td>
<td>O</td>
<td>O</td>
<td>None</td>
<td>-</td>
<td>-</td>
</tr>

</table>

</div>

<div class="datacard datacard-german">
<div class="datacard-header">
<div class="datacard-silhouette">
<span style="color: white; font-size: 10px;">🔲</span>
</div>
<div class="datacard-title-block">
<p class="datacard-title">OPEL BLITZ</p>
<p class="datacard-subtitle">1940-1945 | Vehicle</p>
<p class="datacard-special-rules">Desert Adapted, German Tactical Doctrine, Thin Armor</p>
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
<td>Vehicle</td>
<td>6"</td>
<td>24"</td>
<td>-</td>
<td>Soft-Skinned</td>
<td>-</td>
<td>-</td>
<td>None</td>
<td>-</td>
<td>-</td>
</tr>

</table>

</div>

<div class="datacard datacard-german">
<div class="datacard-header">
<div class="datacard-silhouette">
<span style="color: white; font-size: 10px;">🔲</span>
</div>
<div class="datacard-title-block">
<p class="datacard-title">WORKSHOP VEHICLES</p>
<p class="datacard-subtitle">1940-1945 | Vehicle</p>
<p class="datacard-special-rules">Desert Adapted, German Tactical Doctrine, Thin Armor</p>
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
<td>Vehicle</td>
<td>8"</td>
<td>12"</td>
<td>-</td>
<td>N</td>
<td>O</td>
<td>O</td>
<td>None</td>
<td>-</td>
<td>-</td>
</tr>

</table>

</div>

<div class="datacard datacard-italian">
<div class="datacard-header">
<div class="datacard-silhouette">
<span style="color: white; font-size: 10px;">🔲</span>
</div>
<div class="datacard-title-block">
<p class="datacard-title">AB40</p>
<p class="datacard-subtitle">1940-1945 | Armored Car</p>
<p class="datacard-special-rules">Desert Adapted, Reluctant Warriors, Thin Armor</p>
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
<td>Armored Car</td>
<td>8"</td>
<td>12"</td>
<td>-</td>
<td>N</td>
<td>O</td>
<td>O</td>
<td>None</td>
<td>-</td>
<td>-</td>
</tr>

</table>

</div>

<div class="datacard datacard-italian">
<div class="datacard-header">
<div class="datacard-silhouette">
<span style="color: white; font-size: 10px;">🔲</span>
</div>
<div class="datacard-title-block">
<p class="datacard-title">AB41</p>
<p class="datacard-subtitle">1940-1945 | Armored Car</p>
<p class="datacard-special-rules">Desert Adapted, Reluctant Warriors, Thin Armor</p>
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
<td>Armored Car</td>
<td>8"</td>
<td>12"</td>
<td>-</td>
<td>N</td>
<td>O</td>
<td>O</td>
<td>None</td>
<td>-</td>
<td>-</td>
</tr>

</table>

</div>

<div class="datacard datacard-italian">
<div class="datacard-header">
<div class="datacard-silhouette">
<span style="color: white; font-size: 10px;">🔲</span>
</div>
<div class="datacard-title-block">
<p class="datacard-title">ALFA ROMEO 800RE</p>
<p class="datacard-subtitle">1940-1945 | Vehicle</p>
<p class="datacard-special-rules">Desert Adapted, Reluctant Warriors, Thin Armor</p>
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
<td>Vehicle</td>
<td>8"</td>
<td>12"</td>
<td>-</td>
<td>N</td>
<td>O</td>
<td>O</td>
<td>None</td>
<td>-</td>
<td>-</td>
</tr>

</table>

</div>

<div class="datacard datacard-italian">
<div class="datacard-header">
<div class="datacard-silhouette">
<span style="color: white; font-size: 10px;">🔲</span>
</div>
<div class="datacard-title-block">
<p class="datacard-title">FIAT 508C BALILLA</p>
<p class="datacard-subtitle">1940-1945 | Vehicle</p>
<p class="datacard-special-rules">Desert Adapted, Reluctant Warriors, Thin Armor</p>
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
<td>Vehicle</td>
<td>8"</td>
<td>12"</td>
<td>-</td>
<td>N</td>
<td>O</td>
<td>O</td>
<td>None</td>
<td>-</td>
<td>-</td>
</tr>

</table>

</div>

<div class="datacard datacard-italian">
<div class="datacard-header">
<div class="datacard-silhouette">
<span style="color: white; font-size: 10px;">🔲</span>
</div>
<div class="datacard-title-block">
<p class="datacard-title">FIAT 626 RECOVERY</p>
<p class="datacard-subtitle">1940-1945 | Vehicle</p>
<p class="datacard-special-rules">Desert Adapted, Recovery Vehicle, Reluctant Warriors, Thin Armor</p>
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
<td>Vehicle</td>
<td>8"</td>
<td>12"</td>
<td>-</td>
<td>N</td>
<td>O</td>
<td>O</td>
<td>None</td>
<td>-</td>
<td>-</td>
</tr>

</table>

</div>

<div class="datacard datacard-italian">
<div class="datacard-header">
<div class="datacard-silhouette">
<span style="color: white; font-size: 10px;">🔲</span>
</div>
<div class="datacard-title-block">
<p class="datacard-title">FIAT 665NM</p>
<p class="datacard-subtitle">1940-1945 | Vehicle</p>
<p class="datacard-special-rules">Desert Adapted, Reluctant Warriors, Thin Armor</p>
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
<td>Vehicle</td>
<td>8"</td>
<td>12"</td>
<td>-</td>
<td>N</td>
<td>O</td>
<td>O</td>
<td>None</td>
<td>-</td>
<td>-</td>
</tr>

</table>

</div>

<div class="datacard datacard-italian">
<div class="datacard-header">
<div class="datacard-silhouette">
<span style="color: white; font-size: 10px;">🔲</span>
</div>
<div class="datacard-title-block">
<p class="datacard-title">LANCIA 3RO</p>
<p class="datacard-subtitle">1940-1945 | Vehicle</p>
<p class="datacard-special-rules">Desert Adapted, Reluctant Warriors, Thin Armor</p>
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
<td>Vehicle</td>
<td>8"</td>
<td>12"</td>
<td>-</td>
<td>N</td>
<td>O</td>
<td>O</td>
<td>None</td>
<td>-</td>
<td>-</td>
</tr>

</table>

</div>

<div class="datacard datacard-italian">
<div class="datacard-header">
<div class="datacard-silhouette">
<span style="color: white; font-size: 10px;">🔲</span>
</div>
<div class="datacard-title-block">
<p class="datacard-title">MOTO GUZZI TRIALCE</p>
<p class="datacard-subtitle">1940-1945 | Vehicle</p>
<p class="datacard-special-rules">Desert Adapted, Reluctant Warriors, Thin Armor</p>
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
<td>Vehicle</td>
<td>8"</td>
<td>12"</td>
<td>-</td>
<td>N</td>
<td>O</td>
<td>O</td>
<td>None</td>
<td>-</td>
<td>-</td>
</tr>

</table>

</div>

<div class="datacard datacard-italian">
<div class="datacard-header">
<div class="datacard-silhouette">
<span style="color: white; font-size: 10px;">🔲</span>
</div>
<div class="datacard-title-block">
<p class="datacard-title">SPA 38R</p>
<p class="datacard-subtitle">1940-1945 | Vehicle</p>
<p class="datacard-special-rules">Desert Adapted, Reluctant Warriors, Thin Armor</p>
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
<td>Vehicle</td>
<td>8"</td>
<td>12"</td>
<td>-</td>
<td>N</td>
<td>O</td>
<td>O</td>
<td>None</td>
<td>-</td>
<td>-</td>
</tr>

</table>

</div>

</div>
