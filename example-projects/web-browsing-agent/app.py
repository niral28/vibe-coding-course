import os
import tempfile
from flask import Flask, render_template, request, jsonify, send_file
from dotenv import load_dotenv
import uuid
from datetime import datetime

# Import our utility modules
try:
    from voice_utils import generate_gemini_response, speech_to_text_gemini
    from agent_utils import integrate_api_calls_with_gemini
except ImportError as e:
    print(f"Warning: Could not import utility modules: {e}")
    # Fallback functions for testing
    def generate_gemini_response(text):
        print(f"TTS: {text}")
        return "out.wav"
    
    def speech_to_text_gemini(audio_path):
        return "Test transcription"
    
    def integrate_api_calls_with_gemini(**kwargs):
        return kwargs.get('messages', []) + [{"role": "assistant", "content": "Test response"}]

load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Global storage for chat sessions (in production, use a database)
chat_sessions = {}

def generate_call_id(prefix="call_"):
    return f"{prefix}{uuid.uuid4()}"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json or {}
    query = data.get('query', '')
    session_id = data.get('session_id', str(uuid.uuid4()))
    
    # Initialize session if it doesn't exist
    if session_id not in chat_sessions:
        chat_sessions[session_id] = {
            'messages': [{
                "role": "system", 
                "content": "You are a helpful assistant that can search wikipedia for variety of facts and figures. DO NOT rely on your own knowledge to answer any question, it is all outdated. Take a deep breath, before you call the tools break down the query and explain your thoughts, what are the keywords you are going to use to search the wikipedia article. If the user asks you a question and the answer is not found try rephrasing the question and searching again. You may run parallel tool calls to search for the answer."
            }],
            'created_at': datetime.now().isoformat()
        }
    
    # Add user query to messages
    chat_sessions[session_id]['messages'].append({
        "role": "user", 
        "content": f"[system] Today's date is: {datetime.now().strftime('%Y-%m-%d')}, the user's question is: {query}"
    })
    
    try:
        # Process the query using your existing agent
        messages = integrate_api_calls_with_gemini(
            model="gemini-2.5-pro", 
            query=query, 
            messages=chat_sessions[session_id]['messages'].copy(),
            query_style="2"  # Text mode
        )
        
        # Update session messages
        chat_sessions[session_id]['messages'] = messages
        
        # Extract the final answer from the messages
        answer = ""
        for msg in reversed(messages):
            if msg.get('role') == 'tool' and msg.get('name') == 'answer_question':
                answer = msg.get('content', '').replace('Encyclopedia answer: ', '')
                break
        
        # Convert messages to JSON-serializable format
        serializable_messages = []
        for msg in messages:
            serialized_msg = {
                'role': msg.get('role'),
                'content': msg.get('content', ''),
            }
            
            # Handle tool calls
            if 'tool_calls' in msg and msg['tool_calls']:
                serialized_msg['tool_calls'] = []
                for tool_call in msg['tool_calls']:
                    serialized_msg['tool_calls'].append({
                        'id': getattr(tool_call, 'id', ''),
                        'function': {
                            'name': getattr(tool_call.function, 'name', ''),
                            'arguments': getattr(tool_call.function, 'arguments', '')
                        },
                        'type': getattr(tool_call, 'type', 'function')
                    })
            
            # Handle tool-specific fields
            if 'tool_call_id' in msg:
                serialized_msg['tool_call_id'] = msg['tool_call_id']
            if 'name' in msg:
                serialized_msg['name'] = msg['name']
                
            serializable_messages.append(serialized_msg)
        
        return jsonify({
            'success': True,
            'answer': answer,
            'session_id': session_id,
            'messages': serializable_messages
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'session_id': session_id
        }), 500

@app.route('/api/voice-to-text', methods=['POST'])
def voice_to_text():
    if 'audio' not in request.files:
        return jsonify({'success': False, 'error': 'No audio file provided'}), 400
    
    audio_file = request.files['audio']
    
    if audio_file.filename == '':
        return jsonify({'success': False, 'error': 'No audio file selected'}), 400
    
    try:
        # Save uploaded audio file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_file:
            audio_file.save(tmp_file.name)
            
            # Convert speech to text
            text = speech_to_text_gemini(tmp_file.name)
            
            # Clean up temp file
            os.unlink(tmp_file.name)
            
            return jsonify({
                'success': True,
                'text': text
            })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/text-to-speech', methods=['POST'])
def text_to_speech():
    data = request.json or {}
    text = data.get('text', '')
    
    if not text:
        return jsonify({'success': False, 'error': 'No text provided'}), 400
    
    try:
        # Generate speech using your existing function
        audio_file = generate_gemini_response(text)
        
        # Return the generated audio file
        return send_file(audio_file, as_attachment=True, download_name='response.wav')
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/session/<session_id>')
def get_session(session_id):
    if session_id not in chat_sessions:
        return jsonify({'success': False, 'error': 'Session not found'}), 404
    
    return jsonify({
        'success': True,
        'session': chat_sessions[session_id]
    })

@app.route('/api/sessions')
def list_sessions():
    return jsonify({
        'success': True,
        'sessions': {k: {'created_at': v['created_at'], 'message_count': len(v['messages'])} 
                    for k, v in chat_sessions.items()}
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)