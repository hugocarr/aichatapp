import asyncio
import signal
import sys
import threading
import time

import urwid

from app import run_server
from model import ChatAppModel
from prompt import PERSONALITY_PROMPTS
from view import UIComponents


class ChatApp:
    def __init__(self):
        self.model = ChatAppModel()
        self.typing_animation_task = None

        self.ui = UIComponents(
            on_send_message=self.send_message,
            on_switch_personality=self.switch_personality,
            on_add_personality=self.show_add_personality_popup,
        )
        self.ui.on_save_personality = self.save_new_personality
        self.ui.on_close_popup = self.close_popup

        self.frame = urwid.Frame(self.ui.main_layout)
        self.loop = urwid.MainLoop(
            self.frame,
            unhandled_input=self.handle_input,
            event_loop=urwid.AsyncioEventLoop(),
            palette=[
                ("menu", "black", "light gray"),
                ("button", "black", "light gray"),
                ("button_focus", "white", "dark blue"),
            ],
        )

        self.ui.update_personalities(self.model.get_personalities())
        self.ui.set_chat_title(self.model.get_current_personality().name.capitalize())

    def handle_input(self, key):
        if key == "enter":
            user_input = self.ui.input_edit.edit_text
            if user_input.lower() == "quit":
                raise urwid.ExitMainLoop()
            self.display_user_message(user_input)
            self.ui.input_edit.edit_text = ""
            asyncio.create_task(self.send_message(user_input))
            return True
        return False

    def show_add_personality_popup(self, button):
        self.popup = self.ui.show_add_personality_popup(self.frame)
        self.loop.widget = self.popup

    def save_new_personality(self, button):
        name = self.ui.add_personality_menu.get_name()
        description = self.ui.add_personality_menu.get_description()
        if name and description:
            new_personality = self.model.add_personality(name, description)
            self.ui.update_personalities(self.model.get_personalities())
        self.close_popup(button)

    def close_popup(self, button):
        self.loop.widget = self.frame

    def switch_personality(self, button):
        new_personality = next(
            p for p in self.model.get_personalities() if p.name == button.label
        )
        self.model.set_current_personality(new_personality)
        self.ui.set_chat_title(new_personality.name.capitalize())
        self.ui.update_chat_history(self.model.get_conversation())

    def display_user_message(self, message):
        self.model.add_message("Human", message)
        self.ui.update_chat_history(self.model.get_conversation())

    async def send_message(self, message):
        self.start_typing_animation()
        response = await self.model.send_message(message)
        self.stop_typing_animation()
        self.ui.update_chat_history(self.model.get_conversation())
        self.loop.draw_screen()

    def start_typing_animation(self):
        self.typing_text = urwid.Text("AI is typing...")
        self.ui.chat_walker.append(self.typing_text)
        self.ui.scroll_to_bottom()
        self.typing_animation_task = asyncio.create_task(self.animate_typing())

    def stop_typing_animation(self):
        if self.typing_animation_task:
            self.typing_animation_task.cancel()
        if self.typing_text in self.ui.chat_walker:
            self.ui.chat_walker.remove(self.typing_text)
        self.loop.draw_screen()

    async def animate_typing(self):
        dots = 0
        while True:
            dots = (dots + 1) % 4
            self.typing_text.set_text(f"AI is typing{'.' * dots}")
            self.loop.draw_screen()
            await asyncio.sleep(0.5)

    def run(self):
        self.loop.run()

    def stop(self):
        raise urwid.ExitMainLoop()


server_thread = None


def start_server():
    global server_thread
    server_thread = threading.Thread(target=run_server)
    server_thread.daemon = True
    server_thread.start()
    # Give the server a moment to start
    time.sleep(1)


def signal_handler(signum, frame):
    print("\nReceived signal to terminate. Shutting down gracefully...")
    if "chat_app" in globals():
        chat_app.stop()
    sys.exit(0)


def main():
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)

    print("Starting the web server...")
    start_server()
    print("Web server started. Server logs will be written to server.log")
    print("Initializing UI...")

    global chat_app
    chat_app = ChatApp()

    try:
        chat_app.run()
    except urwid.ExitMainLoop:
        pass


if __name__ == "__main__":
    main()
