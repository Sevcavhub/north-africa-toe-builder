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
                }
            },
            'status': 'Railway deployment active'
        })

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
