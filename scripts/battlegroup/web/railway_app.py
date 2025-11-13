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
