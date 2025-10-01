# utils/gamepad_manager.py
import threading
from inputs import get_gamepad
from PyQt5.QtCore import QObject, pyqtSignal

class GamepadManager(QObject):
    dpad_up = pyqtSignal()
    dpad_down = pyqtSignal()
    dpad_left = pyqtSignal()
    dpad_right = pyqtSignal()
    button_a = pyqtSignal()
    button_b = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.running = False
        self.thread = None

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._listen, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False

    def _listen(self):
        while self.running:
            try:
                events = get_gamepad()
                for event in events:
                    if event.ev_type == "Absolute":
                        if event.code == "ABS_HAT0Y":
                            if event.state == -1:
                                self.dpad_up.emit()
                            elif event.state == 1:
                                self.dpad_down.emit()
                        elif event.code == "ABS_HAT0X":
                            if event.state == -1:
                                self.dpad_left.emit()
                            elif event.state == 1:
                                self.dpad_right.emit()
                    elif event.ev_type == "Key":
                        if event.code in ["BTN_SOUTH", "BTN_A"] and event.state == 1:
                            self.button_a.emit()
                        elif event.code in ["BTN_EAST", "BTN_B"] and event.state == 1:
                            self.button_b.emit()
            except:
                break  # No hay gamepad conectado