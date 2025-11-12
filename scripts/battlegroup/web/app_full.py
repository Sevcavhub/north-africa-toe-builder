#!/usr/bin/env python3
"""
Flask REST API for North Africa TO&E Builder
Phase 9B: BattleGroup Web Services

Main application entry point with REST endpoints for:
- Scenario generation (historical, random, from imported)
- Army list generation
- BG Builder import/export
- Equipment database queries
"""

import sys
from pathlib import Path
from flask import Flask, jsonify, request
from flask_cors import CORS
from werkzeug.exceptions import HTTPException

# Add project paths
PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.battlegroup.web.config import get_config
from scripts.battlegroup.web.services.scenario_service import ScenarioService
from scripts.battlegroup.web.services.army_list_service import ArmyListService


def create_app(config_name='development'):
    """
    Application factory pattern.

    Args:
        config_name: Configuration environment (development, production, testing)

    Returns:
        Configured Flask application
    """
    app = Flask(__name__)

    # Load configuration
    config = get_config(config_name)
    app.config.from_object(config)

    # Configure CORS
    CORS(app, origins=config.CORS_ORIGINS, supports_credentials=True)

    # Initialize services
    scenario_service = ScenarioService()
    army_list_service = ArmyListService()

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
            'service': app.config.get('API_TITLE', 'North Africa TO&E Builder API')
        })

    @app.route('/api', methods=['GET'])
    def api_info():
        """API information endpoint."""
        return jsonify({
            'title': app.config['API_TITLE'],
            'version': app.config['API_VERSION'],
            'description': app.config['API_DESCRIPTION'],
            'endpoints': {
                'scenarios': {
                    'historical': 'POST /api/scenarios/historical',
                    'random': 'POST /api/scenarios/random',
                    'from_import': 'POST /api/scenarios/from-import',
                    'locations': 'GET /api/scenarios/locations/{quarter}'
                },
                'army_lists': {
                    'generate': 'POST /api/army-lists/generate',
                    'validate': 'POST /api/army-lists/validate'
                },
                'bg_builder': {
                    'import': 'POST /api/bg-builder/import',
                    'export': 'GET /api/bg-builder/export/{force_id}'
                },
                'equipment': {
                    'search': 'GET /api/equipment/search',
                    'details': 'GET /api/equipment/{equipment_id}'
                }
            }
        })

    # ============================================================================
    # SCENARIO ENDPOINTS
    # ============================================================================

    @app.route('/api/scenarios/historical', methods=['POST'])
    def generate_historical_scenario():
        """
        Generate historical scenario.

        Request JSON:
        {
            "quarter": "1941q2",
            "battle": "battleaxe",
            "location": "Halfaya Pass",
            "nations": ["german", "british"],  // optional
            "points": 1000  // optional
        }

        Returns:
            Complete scenario JSON with terrain, weather, forces
        """
        data = request.get_json()

        # Validate required fields
        if not data:
            return jsonify({'error': 'Request body required'}), 400

        quarter = data.get('quarter')
        battle = data.get('battle')
        location = data.get('location')

        if not all([quarter, battle, location]):
            return jsonify({
                'error': 'Missing required fields',
                'required': ['quarter', 'battle', 'location']
            }), 400

        # Validate quarter
        if quarter not in app.config['VALID_QUARTERS']:
            return jsonify({
                'error': 'Invalid quarter',
                'valid_quarters': app.config['VALID_QUARTERS']
            }), 400

        # Validate battle
        if battle not in app.config['VALID_BATTLES']:
            return jsonify({
                'error': 'Invalid battle',
                'valid_battles': app.config['VALID_BATTLES']
            }), 400

        try:
            scenario = scenario_service.generate_historical_scenario(
                quarter=quarter,
                battle=battle,
                location=location,
                **{k: v for k, v in data.items() if k not in ['quarter', 'battle', 'location']}
            )
            return jsonify(scenario), 200
        except Exception as e:
            return jsonify({
                'error': 'Scenario generation failed',
                'message': str(e)
            }), 500

    @app.route('/api/scenarios/random', methods=['POST'])
    def generate_random_scenario():
        """
        Generate random scenario.

        Request JSON:
        {
            "points": 1000,
            "nations": ["german", "british"],
            "quarter": "1941q2"
        }

        Returns:
            Random scenario with balanced forces
        """
        data = request.get_json()

        if not data:
            return jsonify({'error': 'Request body required'}), 400

        points = data.get('points')
        nations = data.get('nations')
        quarter = data.get('quarter')

        if not all([points, nations, quarter]):
            return jsonify({
                'error': 'Missing required fields',
                'required': ['points', 'nations', 'quarter']
            }), 400

        # Validate points range
        if not (app.config['MIN_POINTS'] <= points <= app.config['MAX_POINTS']):
            return jsonify({
                'error': 'Invalid points value',
                'min': app.config['MIN_POINTS'],
                'max': app.config['MAX_POINTS']
            }), 400

        # Validate nations
        if len(nations) != 2:
            return jsonify({
                'error': 'Exactly 2 nations required',
                'provided': len(nations)
            }), 400

        for nation in nations:
            if nation not in app.config['VALID_NATIONS']:
                return jsonify({
                    'error': f'Invalid nation: {nation}',
                    'valid_nations': app.config['VALID_NATIONS']
                }), 400

        # Validate quarter
        if quarter not in app.config['VALID_QUARTERS']:
            return jsonify({
                'error': 'Invalid quarter',
                'valid_quarters': app.config['VALID_QUARTERS']
            }), 400

        try:
            scenario = scenario_service.generate_random_scenario(
                points=points,
                nations=nations,
                quarter=quarter
            )
            return jsonify(scenario), 200
        except Exception as e:
            return jsonify({
                'error': 'Scenario generation failed',
                'message': str(e)
            }), 500

    @app.route('/api/scenarios/from-import', methods=['POST'])
    def generate_from_import():
        """
        Generate scenario from BG Builder import.

        Request JSON:
        {
            "imported_scenario": { ... }  // Full imported scenario JSON
        }

        Returns:
            Enriched scenario with terrain, weather, victory conditions
        """
        data = request.get_json()

        if not data or 'imported_scenario' not in data:
            return jsonify({
                'error': 'Missing required field',
                'required': 'imported_scenario'
            }), 400

        try:
            scenario = scenario_service.generate_from_imported(
                data['imported_scenario']
            )
            return jsonify(scenario), 200
        except Exception as e:
            return jsonify({
                'error': 'Scenario generation failed',
                'message': str(e)
            }), 500

    @app.route('/api/scenarios/locations/<quarter>', methods=['GET'])
    def get_locations(quarter):
        """
        Get available battlefield locations for quarter.

        Args:
            quarter: Quarter code (e.g., '1941q2')

        Returns:
            List of location names
        """
        if quarter not in app.config['VALID_QUARTERS']:
            return jsonify({
                'error': 'Invalid quarter',
                'valid_quarters': app.config['VALID_QUARTERS']
            }), 400

        try:
            locations = scenario_service.get_available_locations(quarter)
            return jsonify({
                'quarter': quarter,
                'locations': locations
            }), 200
        except Exception as e:
            return jsonify({
                'error': 'Failed to fetch locations',
                'message': str(e)
            }), 500

    # ============================================================================
    # ARMY LIST ENDPOINTS
    # ============================================================================

    @app.route('/api/army-lists/generate', methods=['POST'])
    def generate_army_list():
        """
        Generate army list based on historical TO&E.

        Request JSON:
        {
            "nation": "german",
            "quarter": "1941q2",
            "unit_type": "panzer_division",  // optional
            "points": 1000  // optional
        }

        Returns:
            Complete army list with equipment and organization
        """
        data = request.get_json()

        if not data:
            return jsonify({'error': 'Request body required'}), 400

        nation = data.get('nation')
        quarter = data.get('quarter')

        if not all([nation, quarter]):
            return jsonify({
                'error': 'Missing required fields',
                'required': ['nation', 'quarter']
            }), 400

        # Validate nation
        if nation not in app.config['VALID_NATIONS']:
            return jsonify({
                'error': 'Invalid nation',
                'valid_nations': app.config['VALID_NATIONS']
            }), 400

        # Validate quarter
        if quarter not in app.config['VALID_QUARTERS']:
            return jsonify({
                'error': 'Invalid quarter',
                'valid_quarters': app.config['VALID_QUARTERS']
            }), 400

        try:
            army_list = army_list_service.generate_army_list(
                nation=nation,
                quarter=quarter,
                unit_type=data.get('unit_type'),
                points_budget=data.get('points')
            )
            return jsonify(army_list), 200
        except Exception as e:
            return jsonify({
                'error': 'Army list generation failed',
                'message': str(e)
            }), 500

    @app.route('/api/army-lists/validate', methods=['POST'])
    def validate_army_list():
        """
        Validate BG Builder army list.

        Request JSON:
        {
            "army_list": { ... }  // BG Builder format army list
        }

        Returns:
            Validation result with errors/warnings
        """
        data = request.get_json()

        if not data or 'army_list' not in data:
            return jsonify({
                'error': 'Missing required field',
                'required': 'army_list'
            }), 400

        try:
            result = army_list_service.validate_army_list(data['army_list'])
            return jsonify(result), 200
        except Exception as e:
            return jsonify({
                'error': 'Validation failed',
                'message': str(e)
            }), 500

    # ============================================================================
    # BG BUILDER INTEGRATION ENDPOINTS
    # ============================================================================

    @app.route('/api/bg-builder/import', methods=['POST'])
    def import_bg_builder():
        """
        Import BG Builder JSON export.

        Request JSON:
        {
            "bg_builder_json": { ... }  // BG Builder export
        }

        Returns:
            Imported and enriched scenario data
        """
        data = request.get_json()

        if not data or 'bg_builder_json' not in data:
            return jsonify({
                'error': 'Missing required field',
                'required': 'bg_builder_json'
            }), 400

        try:
            # Import using bg_builder_import service
            from scripts.phase9b.bg_builder_import import BGBuilderImporter

            importer = BGBuilderImporter()
            result = importer.import_json(data['bg_builder_json'])
            importer.close()

            return jsonify(result), 200
        except Exception as e:
            return jsonify({
                'error': 'Import failed',
                'message': str(e)
            }), 500

    @app.route('/api/bg-builder/export/<force_id>', methods=['GET'])
    def export_bg_builder(force_id):
        """
        Export force as BG Builder JSON.

        Args:
            force_id: Database force ID

        Returns:
            BG Builder compatible JSON
        """
        try:
            # Export using bg_builder_export service
            from scripts.phase9b.bg_builder_export import BGBuilderExporter

            exporter = BGBuilderExporter()
            result = exporter.export_force(int(force_id))
            exporter.close()

            return jsonify(result), 200
        except ValueError:
            return jsonify({
                'error': 'Invalid force_id',
                'message': 'force_id must be an integer'
            }), 400
        except Exception as e:
            return jsonify({
                'error': 'Export failed',
                'message': str(e)
            }), 500

    # ============================================================================
    # EQUIPMENT DATABASE ENDPOINTS
    # ============================================================================

    @app.route('/api/equipment/search', methods=['GET'])
    def search_equipment():
        """
        Search equipment database.

        Query parameters:
            - name: Equipment name (partial match)
            - nation: Nation filter
            - category: Category filter (tank, gun, vehicle, etc.)
            - quarter: Available in quarter

        Returns:
            List of matching equipment items
        """
        name = request.args.get('name', '')
        nation = request.args.get('nation')
        category = request.args.get('category')
        quarter = request.args.get('quarter')

        try:
            results = army_list_service.search_equipment(
                name=name,
                nation=nation,
                category=category,
                quarter=quarter
            )
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

        Args:
            equipment_id: Equipment database ID

        Returns:
            Complete equipment details with BG stats
        """
        try:
            details = army_list_service.get_equipment_details(equipment_id)

            if not details:
                return jsonify({
                    'error': 'Equipment not found',
                    'equipment_id': equipment_id
                }), 404

            return jsonify(details), 200
        except Exception as e:
            return jsonify({
                'error': 'Failed to fetch equipment',
                'message': str(e)
            }), 500

    # ============================================================================
    # CLEANUP
    # ============================================================================

    @app.teardown_appcontext
    def cleanup(error):
        """Cleanup resources on request end."""
        if error:
            app.logger.error(f"Request error: {str(error)}")

    return app


# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    import os

    # Get configuration from environment
    config_name = os.getenv('FLASK_ENV', 'development')

    # Create and run app
    app = create_app(config_name)

    # Development server settings
    port = int(os.getenv('PORT', 5000))
    host = os.getenv('HOST', '0.0.0.0')

    print(f"Starting North Africa TO&E Builder API")
    print(f"Environment: {config_name}")
    print(f"URL: http://{host}:{port}")
    print(f"API Info: http://{host}:{port}/api")

    app.run(
        host=host,
        port=port,
        debug=(config_name == 'development')
    )
