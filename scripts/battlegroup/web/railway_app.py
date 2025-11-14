#!/usr/bin/env python3
"""
Railway deployment entry point for Flask REST API
Simplified version without external dependencies
"""

from pathlib import Path
from flask import Flask, jsonify, request
from flask_cors import CORS
from werkzeug.exceptions import HTTPException
import os

# Import Railway-specific config
from railway_config import RailwayConfig


def create_app():
    """
    Application factory for Railway deployment.
    """
    app = Flask(__name__)
    app.config.from_object(RailwayConfig)

    # Configure CORS
    CORS(app, origins=RailwayConfig.CORS_ORIGINS, supports_credentials=True)

    # ============================================================================
    # ERROR HANDLERS
    # ============================================================================

    @app.errorhandler(HTTPException)
    def handle_http_exception(e):
        """Handle HTTP exceptions with JSON response."""
        response = {
            'error': e.name,
            'message': e.description,
            'status': e.code
        }
        return jsonify(response), e.code

    @app.errorhandler(Exception)
    def handle_generic_exception(e):
        """Handle generic exceptions with JSON response."""
        app.logger.error(f"Unhandled exception: {str(e)}", exc_info=True)
        response = {
            'error': 'Internal Server Error',
            'message': 'An unexpected error occurred',
            'status': 500
        }
        return jsonify(response), 500

    # ============================================================================
    # HEALTH CHECK
    # ============================================================================

    @app.route('/api/health', methods=['GET'])
    def health_check():
        """Health check endpoint."""
        return jsonify({
            'status': 'healthy',
            'api_version': app.config.get('API_VERSION', '1.0.0'),
            'service': app.config.get('API_TITLE', 'North Africa TO&E Builder API'),
            'database_exists': Path(app.config['DATABASE_PATH']).exists()
        })

    @app.route('/api', methods=['GET'])
    def api_info():
        """API information endpoint."""
        return jsonify({
            'title': app.config['API_TITLE'],
            'version': app.config['API_VERSION'],
            'description': app.config['API_DESCRIPTION'],
            'endpoints': {
                'health': 'GET /api/health',
                'equipment': {
                    'search': 'GET /api/equipment/search',
                    'details': 'GET /api/equipment/{equipment_id}'
                },
                'scenarios': {
                    'random': 'POST /api/scenarios/random',
                    'historical': 'POST /api/scenarios/historical',
                    'locations': 'GET /api/scenarios/locations/{quarter}',
                    'printable': 'GET /api/scenarios/{battle}/{scenario_id}/printable'
                },
                'datacards': {
                    'osjones': 'POST /api/datacards/osjones'
                }
            },
            'status': 'Railway deployment active'
        })

    # ============================================================================
    # SCENARIO ENDPOINTS
    # ============================================================================

    @app.route('/api/scenarios/random', methods=['POST'])
    def generate_random_scenario():
        """Generate a random scenario."""
        import sqlite3
        import random

        data = request.get_json() or {}
        points = data.get('points', 1000)
        nation1 = data.get('nation1', 'german')
        nation2 = data.get('nation2', 'british')
        quarter = data.get('quarter', '1942q2')

        try:
            # Simple scenario generation
            scenario = {
                'title': f'Random Encounter - {quarter.upper()}',
                'description': f'A meeting engagement between {nation1.title()} and {nation2.title()} forces in North Africa.',
                'points': points,
                'quarter': quarter,
                'attacker': {
                    'nation': nation1,
                    'points': points,
                    'force': f'{nation1.title()} battlegroup'
                },
                'defender': {
                    'nation': nation2,
                    'points': points,
                    'force': f'{nation2.title()} battlegroup'
                },
                'objectives': [
                    'Control the central objective',
                    'Inflict casualties on enemy forces',
                    'Hold defensive positions'
                ],
                'special_rules': [
                    'Meeting Engagement',
                    'Standard deployment'
                ],
                'terrain': random.choice([
                    'Desert plain with scattered rocks',
                    'Rocky outcrops and wadis',
                    'Open desert with dunes',
                    'Village ruins and fields'
                ])
            }

            return jsonify(scenario), 200

        except Exception as e:
            return jsonify({
                'error': 'Failed to generate scenario',
                'message': str(e)
            }), 500

    @app.route('/api/scenarios/locations/<quarter>', methods=['GET'])
    def get_scenario_locations(quarter):
        """Get available battle locations for a quarter."""
        # Predefined locations for each quarter
        locations = {
            '1941q1': ['Agedabia', 'El Agheila', 'Mersa Brega'],
            '1941q2': ['Halfaya Pass', 'Fort Capuzzo', 'Sollum'],
            '1941q3': ['Tobruk Perimeter', 'Bardia', 'Sidi Barrani'],
            '1941q4': ['Sidi Rezegh', 'Tobruk', 'Bir el Gubi'],
            '1942q1': ['Gazala Line', 'Bir Hacheim', 'Tobruk'],
            '1942q2': ['Gazala', 'Bir Hacheim', 'Got el Ualeb', 'Knightsbridge'],
            '1942q3': ['El Alamein', 'Ruweisat Ridge', 'Alam el Halfa'],
            '1942q4': ['El Alamein', 'Fuka', 'Mersa Matruh']
        }

        quarter_locations = locations.get(quarter, ['Generic Desert Location'])

        return jsonify({
            'quarter': quarter,
            'locations': quarter_locations
        }), 200

    @app.route('/api/scenarios/historical', methods=['POST'])
    def generate_historical_scenario():
        """Generate a historical scenario."""
        data = request.get_json() or {}
        location = data.get('location', 'El Alamein')
        quarter = data.get('quarter', '1942q3')

        # Return a placeholder historical scenario
        scenario = {
            'title': f'Battle of {location}',
            'quarter': quarter,
            'location': location,
            'description': f'Historical engagement at {location} during {quarter.upper()}.',
            'historical_context': f'This battle was part of the North Africa campaign.',
            'forces': {
                'axis': 'German/Italian forces',
                'allies': 'British/Commonwealth forces'
            }
        }

        return jsonify(scenario), 200

    @app.route('/api/scenarios/<battle>/<scenario_id>/printable', methods=['GET'])
    def get_printable_scenario(battle, scenario_id):
        """
        Generate printable HTML scenario with embedded AFV datacards.

        Path parameters:
            - battle: Battle name (battleaxe, crusader, gazala, first_alamein)
            - scenario_id: Scenario ID (scenario_01, scenario_02, etc.)

        Returns:
            HTML content ready for printing (A4 landscape, 2-page format)
        """
        from services.scenario_html_generator import generate_printable_scenario_html

        try:
            # Generate HTML
            html = generate_printable_scenario_html(scenario_id, battle)

            # Return HTML with proper content type
            from flask import make_response
            response = make_response(html)
            response.headers['Content-Type'] = 'text/html; charset=utf-8'
            response.headers['Content-Disposition'] = f'inline; filename="{battle}_{scenario_id}_printable.html"'

            return response

        except FileNotFoundError:
            return jsonify({
                'error': 'Scenario not found',
                'battle': battle,
                'scenario_id': scenario_id,
                'message': f'Scenario file not found: {battle}/book/src/scenarios/{scenario_id}.md'
            }), 404
        except Exception as e:
            app.logger.error(f"Failed to generate printable scenario: {str(e)}", exc_info=True)
            return jsonify({
                'error': 'Failed to generate printable scenario',
                'message': str(e)
            }), 500

    # ============================================================================
    # DATACARD GENERATION ENDPOINTS
    # ============================================================================

    @app.route('/api/datacards/osjones', methods=['POST'])
    def generate_osjones_datacards():
        """
        Generate BattleGroup V5.5 datacards from OSJones Builder army list.

        Request body:
            {
                "army_list_text": "Paste OSJones Builder print output here..."
            }

        Returns:
            {
                "success": true,
                "datacards": {
                    "tanks": "...markdown content...",
                    "guns_and_artillery": "...markdown content..."
                },
                "equipment_found": ["Panzer III G", "88mm FlaK 36", ...],
                "equipment_not_found": ["Some vehicle", ...]
            }
        """
        import sys
        import tempfile
        from pathlib import Path

        # Add project root to path
        project_root = Path(__file__).resolve().parents[3]
        sys.path.insert(0, str(project_root))

        try:
            from scripts.battlegroup.book.parse_osjones_army_list import OSJonesArmyListParser
            from scripts.battlegroup.book.generate_datacards_from_army_list import ArmyListDatacardGenerator

            data = request.get_json() or {}
            army_list_text = data.get('army_list_text', '').strip()

            if not army_list_text:
                return jsonify({
                    'error': 'No army list provided',
                    'message': 'Please provide army_list_text in request body'
                }), 400

            # Parse army list
            parser = OSJonesArmyListParser()
            result = parser.parse_army_list(army_list_text)
            equipment_names = list(result['equipment'])

            if not equipment_names:
                return jsonify({
                    'error': 'No equipment found',
                    'message': 'Could not extract any equipment from the army list',
                    'force_name': result.get('force_name', 'Unknown'),
                    'points': result.get('points_total', 0),
                    'br': result.get('br_total', 0)
                }), 400

            # Generate datacards in temporary directory
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)

                generator = ArmyListDatacardGenerator()
                try:
                    # Track found/not found equipment
                    found_equipment = []
                    not_found_equipment = []

                    # Generate datacards
                    for equipment_name in equipment_names:
                        bg_vehicle = generator.lookup_bg_builder_vehicle(equipment_name)
                        bg_weapon = generator.lookup_bg_builder_weapon_by_name(equipment_name)

                        if bg_vehicle or bg_weapon:
                            found_equipment.append(equipment_name)
                        else:
                            not_found_equipment.append(equipment_name)

                    # Generate datacard files
                    generator.generate_datacards_from_list(equipment_names, temp_path)

                    # Read generated markdown files
                    datacards = {}
                    for category_file in ['tanks.md', 'guns_and_artillery.md', 'vehicles.md', 'other_equipment.md']:
                        file_path = temp_path / category_file
                        if file_path.exists():
                            with open(file_path, 'r', encoding='utf-8') as f:
                                datacards[category_file.replace('.md', '')] = f.read()

                    return jsonify({
                        'success': True,
                        'force_name': result.get('force_name', 'Unknown Force'),
                        'points_total': result.get('points_total', 0),
                        'br_total': result.get('br_total', 0),
                        'equipment_count': len(equipment_names),
                        'equipment_found': found_equipment,
                        'equipment_not_found': not_found_equipment,
                        'datacards': datacards
                    }), 200

                finally:
                    generator.close()

        except ImportError as e:
            app.logger.error(f"Import error: {str(e)}", exc_info=True)
            return jsonify({
                'error': 'Module not found',
                'message': f'Failed to import required modules: {str(e)}'
            }), 500
        except Exception as e:
            app.logger.error(f"Failed to generate datacards: {str(e)}", exc_info=True)
            return jsonify({
                'error': 'Failed to generate datacards',
                'message': str(e)
            }), 500

    @app.route('/api/datacards/osjones/html', methods=['POST'])
    def generate_osjones_datacards_html():
        """
        Generate BattleGroup V5.5 datacards as complete HTML page with V5.5 CSS.
        Returns full HTML document ready for printing (A4 landscape).
        """
        import sys
        import tempfile
        from pathlib import Path

        # Add project root to path
        project_root = Path(__file__).resolve().parents[3]
        sys.path.insert(0, str(project_root))

        try:
            from scripts.battlegroup.book.parse_osjones_army_list import OSJonesArmyListParser
            from scripts.battlegroup.book.generate_datacards_from_army_list import ArmyListDatacardGenerator

            data = request.get_json() or {}
            army_list_text = data.get('army_list_text', '').strip()

            if not army_list_text:
                return '<html><body><h1>Error: No army list provided</h1></body></html>', 400

            # Parse army list
            parser = OSJonesArmyListParser()
            result = parser.parse_army_list(army_list_text)
            equipment_names = list(result['equipment'])

            if not equipment_names:
                return f'<html><body><h1>Error: No equipment found</h1><p>Force: {result.get("force_name", "Unknown")}</p></body></html>', 400

            # Generate datacards in temporary directory
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)

                generator = ArmyListDatacardGenerator()
                try:
                    # Generate datacard files
                    generator.generate_datacards_from_list(equipment_names, temp_path)

                    # Read generated markdown files and combine into single HTML
                    html_parts = []

                    for category_file in ['tanks.md', 'guns_and_artillery.md', 'vehicles.md', 'other_equipment.md']:
                        file_path = temp_path / category_file
                        if file_path.exists():
                            with open(file_path, 'r', encoding='utf-8') as f:
                                content = f.read()
                                # Extract just the HTML datacard divs (skip CSS and markdown header)
                                if '<div class="datacard-grid">' in content:
                                    # Get everything from first datacard-grid to end
                                    html_content = content[content.find('<div class="datacard-grid">'):content.rfind('</div>') + 6]
                                    html_parts.append(html_content)

                    # Build complete HTML document
                    html = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{result.get("force_name", "BattleGroup Army List")} - Datacards</title>
    <style>
{get_v55_css()}
    </style>
</head>
<body>
    <h1>{result.get("force_name", "Army List")} Datacards</h1>
    <p><strong>Points:</strong> {result.get("points_total", 0)} | <strong>BR:</strong> {result.get("br_total", 0)}</p>

    {"".join(html_parts)}

    <p style="margin-top: 2rem; font-size: 0.9em; color: #666;">
        Generated from OSJones Builder army list using North Africa TO&E Builder API
    </p>
</body>
</html>'''

                    return html, 200, {'Content-Type': 'text/html; charset=utf-8'}

                finally:
                    generator.close()

        except Exception as e:
            app.logger.error(f"Failed to generate datacards HTML: {str(e)}", exc_info=True)
            return f'<html><body><h1>Error generating datacards</h1><p>{str(e)}</p></body></html>', 500

    def get_v55_css():
        """Return V5.5 datacard CSS styling."""
        return """
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

body {
    font-family: Arial, sans-serif;
    margin: 20px;
}

h1 {
    color: #4A5335;
    border-bottom: 2px solid #6B7F3D;
    padding-bottom: 0.5rem;
    margin-bottom: 1rem;
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

.datacard.datacard-german .datacard-title,
.datacard.datacard-german .datacard-subtitle,
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
}

.datacard td {
    background-color: #f5f5dc;
    color: #1a1a1a;
    padding: 1px 2px;
    border: 1px solid #2c2416;
    text-align: center;
}
"""

    # ============================================================================
    # EQUIPMENT DATABASE ENDPOINTS (Basic implementation)
    # ============================================================================

    @app.route('/api/equipment/search', methods=['GET'])
    def search_equipment():
        """
        Search equipment database.

        Query parameters:
            - name: Equipment name (partial match)
            - nation: Nation filter
            - category: Category filter (tank, gun, vehicle, etc.)
        """
        import sqlite3

        name = request.args.get('name', '')
        nation = request.args.get('nation')
        category = request.args.get('category')

        try:
            conn = sqlite3.connect(app.config['DATABASE_PATH'])
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            # Build query
            query = "SELECT * FROM equipment WHERE 1=1"
            params = []

            if name:
                query += " AND name LIKE ?"
                params.append(f"%{name}%")

            if nation:
                query += " AND nation = ?"
                params.append(nation)

            if category:
                query += " AND category = ?"
                params.append(category)

            query += " LIMIT 100"

            cursor.execute(query, params)
            results = [dict(row) for row in cursor.fetchall()]
            conn.close()

            return jsonify({
                'count': len(results),
                'results': results
            }), 200
        except Exception as e:
            return jsonify({
                'error': 'Search failed',
                'message': str(e)
            }), 500

    @app.route('/api/equipment/<int:equipment_id>', methods=['GET'])
    def get_equipment_details(equipment_id):
        """
        Get detailed equipment information.
        """
        import sqlite3

        try:
            conn = sqlite3.connect(app.config['DATABASE_PATH'])
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute("SELECT * FROM equipment WHERE id = ?", (equipment_id,))
            result = cursor.fetchone()
            conn.close()

            if not result:
                return jsonify({
                    'error': 'Equipment not found',
                    'equipment_id': equipment_id
                }), 404

            return jsonify(dict(result)), 200
        except Exception as e:
            return jsonify({
                'error': 'Failed to fetch equipment',
                'message': str(e)
            }), 500

    return app


# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    # Create and run app
    app = create_app()

    # Railway sets PORT environment variable
    port = int(os.getenv('PORT', 5000))
    host = '0.0.0.0'

    print(f"Starting North Africa TO&E Builder API (Railway Deployment)")
    print(f"URL: http://{host}:{port}")
    print(f"Database: {app.config['DATABASE_PATH']}")
    print(f"Database exists: {Path(app.config['DATABASE_PATH']).exists()}")

    app.run(
        host=host,
        port=port,
        debug=False
    )
