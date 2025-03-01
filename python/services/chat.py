class ChatService:
    def __init__(self):
        self.chat = []

    def add_message(self, message):
        self.chat.append(message)

    def get_messages(self):
        return self.chat

    def clear(self):
        self.chat = []
