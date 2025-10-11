# Web-Based Secondary Sources for Equipment Data

## Tier 2 Sources (75% Confidence)

### 1. Lexikon der Wehrmacht
- **URL**: http://www.lexikon-der-wehrmacht.de/
- **Coverage**: German units, commanders, equipment variants
- **Data Quality**: Compiled from primary sources, generally reliable
- **Search Pattern**: Unit name → Gliederung section → Equipment lists
- **Example**: http://www.lexikon-der-wehrmacht.de/Gliederungen/PanzerDivisionen/21PD.htm

### 2. Niehorster World War II Order of Battle
- **URL**: http://www.niehorster.org/
- **Coverage**: All nations, detailed TO&E with equipment
- **Data Quality**: Very high - Niehorster is a respected researcher
- **Search Pattern**: Nation → Theater → Date → Unit
- **Example**: German/Afrika/1941/5.leichte-Division

### 3. Feldgrau.com
- **URL**: http://www.feldgrau.com/
- **Coverage**: German formations, equipment, organization
- **Data Quality**: Good, community-verified
- **Search Pattern**: Browse units → Select division → View TO&E
- **Equipment Details**: Often includes variant information (Pz.Kpfw. III Ausf. G vs H)

### 4. Axis History Forum
- **URL**: https://forum.axishistory.com/
- **Coverage**: Detailed discussions, primary source extracts
- **Data Quality**: Variable, but serious researchers
- **Search Pattern**: Forum search → Unit name + equipment
- **Notes**: Often has scans of actual KStN documents

## Tier 3 Sources (60% Confidence)

### 5. achtungpanzer.com
- **URL**: https://www.achtungpanzer.com/
- **Coverage**: German armor units, detailed equipment
- **Data Quality**: Good for panzer units
- **Focus**: Tank variants, production numbers, unit assignments

### 6. tanks-encyclopedia.com
- **URL**: https://tanks-encyclopedia.com/
- **Coverage**: All nations' armored vehicles
- **Data Quality**: Good technical data
- **Use**: Vehicle variant identification

## KStN Archives

### Known KStN Document Repositories
1. **Bundesarchiv-Militärarchiv (German Federal Military Archive)**
   - Location**: Freiburg, Germany
   - Holdings**: Original KStN/KAN documents
   - Access**: Research visits or document requests
   - **Online**: Some digitized: https://www.bundesarchiv.de/

2. **US National Archives (NARA)**
   - **Captured German Documents**: Microfilm T-78, T-79, T-311, T-312
   - **G-2 Handbooks**: US Army intelligence compilations
   - **Online**: fold3.com has some digitized records

3. **The Nafziger Collection**
   - **George Nafziger's OOB Collection** (now hosted by USACAC)
   - **Coverage**: Detailed TO&E from various sources
   - **URL**: http://usacac.army.mil/CAC2/CGSC/CARL/nafziger.asp

## British Sources

### 1. UK National Archives (TNA)
- **WO Series**: War Office records with unit establishments
- **Online Catalog**: https://discovery.nationalarchives.gov.uk/

### 2. Long Long Trail
- **URL**: http://www.1914-1918.net/
- **Coverage**: British Army organization (WWI focus but has WWII)
- **Data Quality**: Very detailed

### 3. British War Office Publications
- Already have: British Army Lists (quarterly 1941-1943)
- Need: War Establishments (WE) tables - equivalent to German KStN

## Italian Sources

### 1. Already Have
- **TME 30-420**: US War Department handbook on Italian forces
- Should contain equipment tables

### 2. Comando Supremo
- **URL**: http://www.comandosupremo.com/
- **Coverage**: Italian military forces WWII
- **Data Quality**: Excellent, primary source based
- **Equipment**: Often has vehicle/weapon counts

### 3. Regio Esercito
- Italian Army official histories and documents
- **Search**: Web search for specific units + "ordine di battaglia"

## Search Strategy for Each Unit

### Step 1: Primary Source Check
1. Search Tessin for organizational structure (confirmed)
2. Search British Army Lists for British units
3. Search TME 30-420 for Italian units

### Step 2: Tier 2 Web Sources
1. Check Lexikon der Wehrmacht (German units)
2. Check Niehorster (all nations)
3. Check Feldgrau.com (German units)

### Step 3: Tier 3 Supplemental
1. Achtungpanzer for German armor details
2. Comando Supremo for Italian units
3. Axis History Forum for specific questions

### Step 4: Archive Requests (if needed)
1. Bundesarchiv for KStN documents
2. NARA for G-2 handbooks
3. Nafziger Collection for compiled TO&E

## Equipment Variant Identification

### Tank Variants
- **Pz.Kpfw. II**: Ausf. A-F (light)
- **Pz.Kpfw. III**: Ausf. E-N (medium, 3.7cm or 5cm gun)
- **Pz.Kpfw. IV**: Ausf. A-J (medium, 7.5cm gun)
- **Pz.Kpfw. 38(t)**: Czech tank, 3.7cm gun

### Artillery Variants
- **10.5cm leFH 18**: Standard light field howitzer
- **15cm sFH 18**: Heavy field howitzer
- **3.7cm PaK 35/36**: Light anti-tank gun
- **5cm PaK 38**: Medium anti-tank gun
- **8.8cm FlaK 18/36/37**: Heavy anti-aircraft (also anti-tank)

### Vehicle Types
- **Opel Blitz**: 3-ton truck
- **Krupp L2H143**: Light truck
- **Sd.Kfz. 251**: Halftrack APC
- **BMW R75**: Motorcycle with sidecar

## Confidence Score Assignment

- **90-100%**: Data from KStN/KAN documents or official unit war diaries
- **85-89%**: Data from Tessin + Niehorster + Lexikon (triangulated)
- **75-84%**: Data from 2 Tier 2 sources (Niehorster OR Lexikon + Feldgrau)
- **60-74%**: Data from single Tier 2 source or multiple Tier 3 sources
- **<60%**: Single Tier 3 source or educated estimation

## Workflow Integration

For each unit:
1. Extract organizational structure from Tessin (confirmed facts)
2. Search Niehorster for TO&E data
3. Cross-reference with Lexikon der Wehrmacht
4. Verify equipment variants with Feldgrau/Achtungpanzer
5. Record all sources in metadata
6. Assign confidence score based on source quality
7. Mark any estimated or inferred data clearly

## Puppeteer MCP Usage

Since web scraping hit CAPTCHA issues, alternative approaches:
1. **Manual research**: You manually navigate to sources and extract data
2. **Puppeteer for simple pages**: Try sources without heavy bot protection
3. **WebFetch tool**: For specific URL + prompt combinations
4. **API access**: Some sources have APIs or data exports
