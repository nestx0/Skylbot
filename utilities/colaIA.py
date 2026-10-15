import threading
from collections import deque


class TextBlock:
    def __init__(self, question: str, answer: str) -> None:
        self.question = question
        self.answer = answer

    def getNumCharacters(self) -> int:
        return len(self.question) + len(self.answer)

    def parse(self) -> str:
        return "Pregunta: " + self.question + "\n" + "Respuesta: " + self.answer + "\n"


class IAQueue:
    def __init__(self, max_tam: int = 3, max_chars: int = 5000) -> None:
        self.MAX_TAM = max_tam
        self.MAX_CHARS = max_chars
        self.deque: deque[TextBlock] = deque()
        self.current_characters: int = 0
        self.lock = threading.Lock()

    def addMessage(self, txt: TextBlock):
        # Como no estamos usando async y await hay que echarle el cerrojo
        with self.lock:
            if txt.getNumCharacters() > self.MAX_CHARS:
                return

            while len(self.deque) >= self.MAX_TAM or (
                self.current_characters + txt.getNumCharacters() > self.MAX_CHARS
            ):
                x = self.deque.popleft()
                self.current_characters -= x.getNumCharacters()

            self.deque.append(txt)
            self.current_characters += txt.getNumCharacters()

    def getHistory(self) -> list[TextBlock]:
        with self.lock:
            return list(self.deque)


class GlobalQueue:
    def __init__(self) -> None:
        self.queue_map = {}
        self.global_lock = threading.Lock()

    def interact(self, user: str, txt: TextBlock):
        with self.global_lock:
            if user not in self.queue_map:
                self.queue_map[user] = IAQueue()

        self.queue_map[user].addMessage(txt)

    def getHistory(self, user: str):
        with self.global_lock:
            if user not in self.queue_map:
                return []
            user_queue = self.queue_map[user]

        return user_queue.getHistory()
