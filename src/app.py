"""
Simple Flask app runner for generated API code.
This imports and runs the AI-generated API from src/generated/
"""

from flask import Flask

app = Flask(__name__)

# Import and register the generated API blueprint
try:
    from generated.api import claims_bp
    app.register_blueprint(claims_bp)
    print("✅ Successfully loaded AI-generated API")
except ImportError as e:
    print(f"⚠️  Generated API not found: {e}")
    print("Run the workflow to generate the API code first")

@app.route('/health')
def health():
    return {'status': 'healthy', 'service': 'glow-claims-api'}

if __name__ == '__main__':
    print("🚀 Starting Glow Claims API...")
    print("📍 Health check: http://localhost:5000/health")
    print("📍 API endpoint: http://localhost:5000/api/v1/claims/screen-damage/approve")
    app.run(debug=True, host='0.0.0.0', port=5000)
