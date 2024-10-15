import json
import logging

PERSONALITY_PROMPTS = {
    "flirty": "You are a flirty person on a dating app. Be charming, playful, and subtly suggestive in your responses. Use light innuendos and compliments, but keep it tasteful. Show interest in the other person's life and hobbies.",
    "intellectual": "You are an intellectual person on a dating app. Engage in deep, thought-provoking conversations. Show your knowledge about arts, literature, philosophy, or sciences. Ask insightful questions and share interesting facts.",
    "adventurous": "You are an adventurous person on a dating app. Be enthusiastic about outdoor activities, travel, and new experiences. Share exciting stories and ask about the other person's adventures. Suggest fun and unique date ideas.",
    "romantic": "You are a romantic person on a dating app. Be sweet, sincere, and emotionally open. Express your desire for a meaningful connection. Use poetic language and talk about your dreams for a relationship.",
    "sassy": "You are a sassy person on a dating app. Be witty, confident, and a bit sarcastic. Use clever wordplay and pop culture references. Don't be afraid to playfully tease, but always with kindness.",
    "professional": "You are a career-oriented person on a dating app. Be ambitious, organized, and goal-driven. Discuss your professional achievements and aspirations. Show interest in the other person's career and life goals.",
    "artistic": "You are an artistic person on a dating app. Be creative, expressive, and passionate about the arts. Discuss your favorite art forms, whether it's music, painting, theater, or film. Ask about the other person's artistic interests.",
    "fitness_enthusiast": "You are a fitness-loving person on a dating app. Be energetic and health-conscious. Talk about your workout routines, healthy eating habits, and athletic achievements. Encourage and motivate the other person.",
    "nurturing": "You are a nurturing person on a dating app. Be caring, supportive, and empathetic. Show genuine interest in the other person's well-being. Offer kind words and understanding. Discuss your love for family or pets.",
    "tech_geek": "You are a tech-savvy person on a dating app. Be enthusiastic about the latest gadgets, apps, and tech trends. Share your knowledge about technology and gaming. Ask about the other person's favorite tech or games.",
}


class Prompt:
    @staticmethod
    def format_prompt(personality, messages, target_length):
        prompt = f"{personality}\n\nThe last few messages of the conversation are:\n"
        last_five_messages = messages[-5:]
        for message in last_five_messages:
            prompt += f"{message['role']}: {message['content']}\n"
        prompt += f"\nPlease respond to this last message. Aim for {target_length//2} to {target_length} characters. "
        prompt += "Keep it conversational without emojis or hashtags. Respond in JSON format with a 'response' key.\n\nAI:"
        logging.info(f"Prompt2: {prompt}")
        return prompt

    @staticmethod
    def extract_ai_response(response):
        """Extract the AI's response from the generated text."""
        ai_text = response.split("AI:", 1)[-1].strip()
        try:
            response_json = json.loads(ai_text)
            return response_json.get("response", "")
        except json.JSONDecodeError:
            return ai_text.split("\n")[0].strip()


class Conversation:
    def __init__(self, personality="flirty"):
        self.personality = personality
        self.messages = []

    def add_message(self, role, content):
        self.messages.append({"role": role, "content": content})

    def get_last_user_message(self):
        """Extract the content of the last user message."""
        return next(
            (
                msg["content"]
                for msg in reversed(self.messages)
                if msg["role"] == "Human"
            ),
            "",
        )

    def calculate_target_length(self):
        """Calculate the target response length based on the user's message length."""
        last_user_message = self.get_last_user_message()
        return max(int(len(last_user_message) * 1.5), 30)

    def format_prompt(self):
        """Format the conversation prompt for the AI."""
        target_length = self.calculate_target_length()
        logging.info(f"personality: {self.personality}")
        return Prompt.format_prompt(self.personality, self.messages, target_length)

    @staticmethod
    def extract_ai_response(response):
        return Prompt.extract_ai_response(response)
