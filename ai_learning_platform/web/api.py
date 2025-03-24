# Enhanced api.py with better error handling, logging, and CORS configuration
import os
import json
import sys
import logging
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.exceptions import HTTPException
import traceback

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("api_server.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Add the parent directory to the path so we can import from gray_swan
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from gray_swan.prompt_analyzer import PromptAnalyzer

app = Flask(__name__)

# Enhanced CORS configuration
CORS(app, resources={
    r"/api/*": {
        "origins": "*",  # In production, restrict to specific origins
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# Initialize the PromptAnalyzer
analyzer = PromptAnalyzer()

# Request validation middleware
@app.before_request
def validate_request():
    """Validate incoming requests."""
    if request.method == "POST" and request.is_json:
        if not request.json:
            logger.warning("Invalid request: No JSON data")
            return jsonify({
                'success': False,
                'error': 'Request must contain valid JSON data'
            }), 400

# Global error handler
@app.errorhandler(Exception)
def handle_exception(e):
    """Handle all exceptions."""
    # Pass through HTTP exceptions
    if isinstance(e, HTTPException):
        logger.warning(f"HTTP exception: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'status_code': e.code
        }), e.code
        
    # Log the exception
    logger.error(f"Unhandled exception: {str(e)}")
    logger.error(traceback.format_exc())
    
    # Return a generic error response
    return jsonify({
        'success': False,
        'error': 'An unexpected error occurred. Please try again later.',
        'details': str(e) if app.debug else None
    }), 500

# Health check endpoint
@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'version': '1.0.0',
        'timestamp': datetime.now().isoformat()
    })

# Existing endpoints with improved error handling...
@app.route('/api/templates', methods=['GET'])
def get_templates():
    """Get all available prompt templates."""
    try:
        # Load templates
        analyzer.load_templates()
        
        # Convert templates to a list for the response
        templates_list = []
        for name, template in analyzer.templates.items():
            templates_list.append({
                'name': name,
                'description': template.get('description', ''),
                'challenge_type': template.get('challenge_type', '')
            })
            
        logger.info(f"Successfully retrieved {len(templates_list)} templates")
        return jsonify({
            'success': True,
            'templates': templates_list
        })
    except Exception as e:
        logger.error(f"Error retrieving templates: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Other endpoints with similar improvements...
@app.route('/api/successful-prompts', methods=['GET'])
def get_successful_prompts():
    """Get successful prompts for a specific challenge."""
    challenge = request.args.get('challenge')
    if not challenge:
        logger.error("Missing 'challenge' parameter in request")
        return jsonify({
            'success': False,
            'error': 'Challenge parameter is required'
        }), 400
        
    try:
        # Load results
        analyzer.load_results()
        
        # Filter prompts for the specified challenge
        challenge_prompts = [p for p in analyzer.successful_prompts if p["challenge"] == challenge]
        
        # Format prompts for the response
        prompts_list = []
        for prompt in challenge_prompts:
            prompts_list.append({
                'challenge': prompt['challenge'],
                'model': prompt['model'],
                'content': prompt['content'],
                'file_path': os.path.basename(prompt['file_path'])
            })
        
        logger.info(f"Successfully retrieved {len(prompts_list)} successful prompts for challenge: {challenge}")
        return jsonify({
            'success': True,
            'prompts': prompts_list
        })
    except Exception as e:
        logger.error(f"Error retrieving successful prompts: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/analyze-prompts', methods=['POST'])
def analyze_prompts():
    """Analyze patterns in successful prompts for a challenge."""
    data = request.json
    challenge = data.get('challenge')
    
    if not challenge:
        logger.error("Missing 'challenge' parameter in request")
        return jsonify({
            'success': False,
            'error': 'Challenge parameter is required'
        }), 400
        
    try:
        # Load results and analyze patterns
        analyzer.load_results()
        analyzer.analyze_patterns()
        
        # Get patterns for the specified challenge
        patterns = analyzer.prompt_patterns.get(challenge, {})
        
        # Format the response
        techniques = []
        if 'techniques' in patterns:
            for technique in patterns['techniques']:
                # Get the count from the Counter
                count = sum(1 for p in analyzer.successful_prompts
                           if p["challenge"] == challenge and
                           technique in analyzer.prompt_patterns.get(p["challenge"], {}).get('techniques', []))
                
                # Calculate success rate
                total = analyzer.challenge_stats[challenge]['total']
                success_rate = (count / total * 100) if total > 0 else 0
                
                techniques.append({
                    'name': technique.replace('_', ' ').title(),
                    'count': count,
                    'success_rate': f"{success_rate:.1f}"
                })
        
        logger.info(f"Successfully analyzed patterns for challenge: {challenge}")
        return jsonify({
            'success': True,
            'challenge': challenge,
            'techniques': techniques,
            'phrases': patterns.get('phrases', [])
        })
    except Exception as e:
        logger.error(f"Error analyzing prompts: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/generate-prompts', methods=['POST'])
def generate_prompts():
    """Generate new prompts based on patterns and/or templates."""
    data = request.json
    challenge = data.get('challenge')
    count = data.get('count', 5)
    template_name = data.get('template')
    
    if not challenge:
        logger.error("Missing 'challenge' parameter in request")
        return jsonify({
            'success': False,
            'error': 'Challenge parameter is required'
        }), 400
        
    try:
        # Load results and analyze patterns
        analyzer.load_results()
        analyzer.analyze_patterns()
        
        # Generate prompts
        generated_prompts = analyzer.generate_prompts(challenge, count, template_name)
        
        logger.info(f"Successfully generated {len(generated_prompts)} prompts for challenge: {challenge}")
        return jsonify({
            'success': True,
            'prompts': generated_prompts
        })
    except Exception as e:
        logger.error(f"Error generating prompts: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    # Make the script executable
    if not os.access(__file__, os.X_OK):
        os.chmod(__file__, 0o755)
        
    # Start the Flask app
    logger.info("Starting API server on port 5000")
    app.run(host='0.0.0.0', port=5000, debug=True)