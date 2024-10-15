import asyncio
import json

import requests

from prompt import PERSONALITY_PROMPTS


class Personality:
    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.conversation = []

    def add_message(self, role, content):
        self.conversation.append({"role": role, "content": content})

    def get_conversation(self):
        return self.conversation


class ChatAppModel:
    def __init__(self):
        self.url = "http://localhost:5001/chat"
        self.headers = {"Content-Type": "application/json"}
        self.personalities = [
            Personality(name, desc) for name, desc in PERSONALITY_PROMPTS.items()
        ]
        self.current_personality = self.personalities[0]

    def get_personalities(self):
        return self.personalities

    def get_current_personality(self):
        return self.current_personality

    def set_current_personality(self, personality):
        self.current_personality = personality

    def add_personality(self, name, description):
        new_personality = Personality(name, description)
        self.personalities.append(new_personality)
        return new_personality

    def add_message(self, role, content):
        self.current_personality.add_message(role, content)

    def get_conversation(self):
        return self.current_personality.get_conversation()

    async def send_message(self, message):
        try:
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: requests.post(
                    self.url,
                    headers=self.headers,
                    data=json.dumps(
                        {
                            "conversation": self.get_conversation(),
                            "personality": self.current_personality.description,
                        }
                    ),
                ),
            )
            response.raise_for_status()
            result = response.json()
            if "response" in result:
                ai_response = result["response"]
                self.add_message("AI", ai_response)
                return ai_response
            else:
                return "Unexpected response format from the server."
        except requests.exceptions.RequestException as e:
            return f"Error sending request: {e}"
