import logging
import os
import threading

from flask import Flask, jsonify, request
from gpt4all import GPT4All

from prompt import Conversation

# Set up logging
log_file = "/tmp/server.log"
logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# Redirect Flask's logger to the file
for handler in logging.getLogger("werkzeug").handlers:
    logging.getLogger("werkzeug").removeHandler(handler)
logging.getLogger("werkzeug").addHandler(logging.FileHandler(log_file))

app = Flask(__name__)

# Initialize the GPT4All model
MODEL_NAME = os.getenv("GPT4ALL_MODEL", "Nous-Hermes-2-Mistral-7B-DPO.Q4_0.gguf")
model = GPT4All(MODEL_NAME)

server_thread = None


def generate_ai_response(prompt, max_tokens):
    """Generate AI response using the GPT4All model."""
    with model.chat_session() as session:
        return session.generate(prompt, max_tokens=max_tokens)


@app.route("/chat", methods=["POST"])
def chat():
    conversation_data = request.json.get("conversation", [])
    personality = request.json.get("personality", "flirty")

    if not conversation_data:
        return jsonify({"error": "No conversation provided"}), 400
    conversation = Conversation(personality)
    for message in conversation_data:
        conversation.add_message(message["role"], message["content"])

    prompt = conversation.format_prompt()
    max_tokens = int(os.getenv("MAX_TOKENS", 400))

    response = generate_ai_response(prompt, max_tokens)
    ai_response = Conversation.extract_ai_response(response)

    logging.info(f"AI response: {ai_response}")
    return jsonify({"response": ai_response})


def run_server():
    host = os.getenv("FLASK_HOST", "0.0.0.0")
    port = int(os.getenv("FLASK_PORT", 5001))
    logging.info(f"Starting server on {host}:{port}")
    app.run(
        host=host, port=port, debug=os.getenv("FLASK_DEBUG", True), use_reloader=False
    )


def start_server():
    global server_thread
    server_thread = threading.Thread(target=run_server)
    server_thread.daemon = True
    server_thread.start()


if __name__ == "__main__":
    run_server()
