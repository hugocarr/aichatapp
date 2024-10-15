import urwid


class UIComponents:
    def __init__(self, on_send_message, on_switch_personality, on_add_personality):
        self.on_send_message = on_send_message
        self.on_switch_personality = on_switch_personality
        self.on_add_personality = on_add_personality
        self.on_save_personality = None  # We'll set this later
        self.on_close_popup = None  # We'll set this later

        self.menu = self._create_menu()
        self.personality_box, self.personality_listbox = self._create_personality_box()
        self.chat_box, self.chat_walker = self._create_chat_box()
        self.input_box, self.input_edit = self._create_input_box()
        self.main_layout = self._create_main_layout()

    def _create_menu(self):
        menu_items = [
            urwid.AttrMap(
                urwid.Button("Add Personality", on_press=self.on_add_personality),
                "button",
                "button_focus",
            ),
        ]
        return urwid.AttrMap(urwid.Columns(menu_items), "menu")

    def _create_personality_box(self):
        listbox = urwid.ListBox(urwid.SimpleListWalker([]))
        box = urwid.LineBox(listbox, title="Personalities")
        return box, listbox

    def _create_chat_box(self):
        walker = urwid.SimpleListWalker([])
        listbox = urwid.ListBox(walker)
        box = urwid.LineBox(listbox, title="Chat")
        return box, walker

    def _create_input_box(self):
        edit = urwid.Edit("You: ")
        box = urwid.LineBox(edit)
        return box, edit

    def _create_main_layout(self):
        right_column = urwid.Pile(
            [("weight", 1, self.chat_box), ("pack", self.input_box)]
        )
        columns = urwid.Columns(
            [("weight", 1, self.personality_box), ("weight", 3, right_column)]
        )
        return urwid.Pile([("pack", self.menu), ("weight", 1, columns)])

    def update_personalities(self, personalities):
        self.personality_listbox.body[:] = [
            urwid.Button(p.name, on_press=self.on_switch_personality)
            for p in personalities
        ]

    def update_chat_history(self, conversation):
        self.chat_walker[:] = []
        for message in conversation:
            role = message["role"]
            content = message["content"]
            self.chat_walker.append(urwid.Text([("bold", f"{role}: "), content]))
            self.chat_walker.append(urwid.Divider())
        self.scroll_to_bottom()

    def append_to_chat_history(self, text):
        self.chat_walker.append(urwid.Text(text))
        self.chat_walker.append(urwid.Divider())
        self.scroll_to_bottom()

    def scroll_to_bottom(self):
        if self.chat_walker:
            self.chat_box.base_widget.focus_position = len(self.chat_walker) - 1
        self.chat_box.base_widget.set_focus_valign("bottom")

    def set_chat_title(self, title):
        self.chat_box.set_title(title)

    def show_add_personality_popup(self, base_widget):
        self.add_personality_menu = AddPersonalityMenu(
            on_save=self.on_save_personality, on_cancel=self.on_close_popup
        )
        self.popup = urwid.Overlay(
            self.add_personality_menu.popup,
            base_widget,
            "center",
            ("relative", 50),
            "middle",
            ("relative", 50),
        )
        return self.popup


class AddPersonalityMenu:
    def __init__(self, on_save, on_cancel):
        self.name_edit = urwid.Edit("Name: ")
        self.description_edit = urwid.Edit("Description: ")
        save_button = urwid.Button("Save", on_press=on_save)
        cancel_button = urwid.Button("Cancel", on_press=on_cancel)

        popup_content = urwid.ListBox(
            urwid.SimpleListWalker(
                [
                    self.name_edit,
                    self.description_edit,
                    urwid.Columns([save_button, cancel_button]),
                ]
            )
        )

        self.popup = urwid.LineBox(popup_content, title="Add New Personality")

    def get_name(self):
        return self.name_edit.edit_text.strip()

    def get_description(self):
        return self.description_edit.edit_text.strip()
