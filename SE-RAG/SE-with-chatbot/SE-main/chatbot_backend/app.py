import os
import threading
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Allow cross-origin requests, especially from local Flutter web/emulator

# Global readiness state
is_initialized = False

# Import our engine components (this will take a few seconds to load PyTorch)
from chatbot_engine import generate_response, _get_chroma_setup
generate_response_fn = generate_response

print("Pre-loading FAQ embedding models before starting server...")
_get_chroma_setup()
is_initialized = True
print("Backend initialization complete! Server is 100% ready.")

# Global conversation memory (for demo purposes)
global_conversation_history = []

@app.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint for the Flutter app.
    Returns 200 OK if 100% reachable and initialized.
    """
    if is_initialized:
        return jsonify({"status": "ready"}), 200
    else:
        return jsonify({"status": "initializing"}), 503

@app.route('/chat', methods=['POST'])
def chat():
    """
    Main chat endpoint for Flutter.
    Expects JSON:
    {
        "message": "user message",
        "products": [...],
        "inventoryItems": [...]
    }
    """
    global global_conversation_history
    
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({"error": "No message provided."}), 400
            
        user_message = data['message']
        
        # Check if it's the first message in the session
        is_first = len(global_conversation_history) == 0
        
        # Note: We are currently ignoring the 'products' and 'inventoryItems' 
        # sent from the frontend because our backend already pulls directly 
        # from Firebase using firebase_connector.py.
        
        # Check if backend is ready
        if not is_initialized or generate_response_fn is None:
            return jsonify({
                "response": "The backend is still initializing. Please try again in a few seconds.",
                "intent": "fallback"
            }), 503
            
        # Generate response using our LLM engine
        reply, updated_history = generate_response_fn(
            user_input=user_message,
            conversation_history=global_conversation_history,
            is_first_message=is_first
        )
        
        # Update global memory
        global_conversation_history = updated_history
        
        # Return response matching the expected Dart model
        return jsonify({
            "response": reply,
            "intent": "general" # Can be dynamically populated if needed
        }), 200
        
    except Exception as e:
        return jsonify({
            "response": f"I'm sorry, I encountered an internal error: {e}",
            "intent": "error"
        }), 500

if __name__ == '__main__':
    # Run on 0.0.0.0 to allow emulator (10.0.2.2) and external local access
    app.run(host='0.0.0.0', port=5000, debug=False)
