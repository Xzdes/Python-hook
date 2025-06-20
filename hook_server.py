# File: hook_server.py (Финальная версия)

import sys
import ctypes
import json
import string
from pynput import keyboard

# --- КОНФИГУРАЦИЯ КОДИРОВКИ ВЫВОДА ---
try:
    sys.stdout.reconfigure(encoding='utf-8')
except TypeError:
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# --- КОНСТАНТЫ VIRTUAL-KEY (VK) КОДОВ ---
VK_SHIFT = 0x10
VK_CONTROL = 0x11
VK_ALT = 0x12
VK_CAPSLOCK = 0x14
VK_NUMLOCK = 0x90

# --- СЛОВАРИ СИМВОЛОВ (KEY MAPS) ---
VK_MAP = {
    **{0x41 + i: char for i, char in enumerate(string.ascii_lowercase)},
    **{0x30 + i: str(i) for i in range(10)},
    0xBA: ';', 0xBB: '=', 0xBC: ',', 0xBD: '-', 0xBE: '.', 0xBF: '/', 0xC0: '`',
    0xDB: '[', 0xDC: '\\', 0xDD: ']', 0xDE: "'",
}
VK_SHIFT_MAP = {
    **{0x30 + i: char for i, char in enumerate(')!@#$%^&*(')},
    0xBA: ':', 0xBB: '+', 0xBC: '<', 0xBD: '_', 0xBE: '>', 0xBF: '?', 0xC0: '~',
    0xDB: '{', 0xDC: '|', 0xDD: '}', 0xDE: '"'
}
NUMPAD_MAP = {
    **{0x60 + i: str(i) for i in range(10)},
    0x6A: '*', 0x6B: '+', 0x6D: '-', 0x6E: '.', 0x6F: '/'
}
NUMPAD_OFF_MAP = {
    0x60: 'INSERT', 0x61: 'END',   0x62: 'DOWN',  0x63: 'PAGEDOWN',
    0x64: 'LEFT',   0x65: 'CLEAR', 0x66: 'RIGHT', 0x67: 'HOME',
    0x68: 'UP',     0x69: 'PAGEUP',0x6E: 'DELETE'
}

# --- СЛУЖЕБНЫЕ КЛАВИШИ (полностью переработано для ясности) ---
_base_service_keys = [
    keyboard.Key.enter, keyboard.Key.backspace, keyboard.Key.esc, keyboard.Key.tab,
    keyboard.Key.caps_lock, keyboard.Key.left, keyboard.Key.up, keyboard.Key.right, 
    keyboard.Key.down, keyboard.Key.delete, keyboard.Key.home, keyboard.Key.end,
    keyboard.Key.page_up, keyboard.Key.page_down, keyboard.Key.num_lock,
    keyboard.Key.print_screen, keyboard.Key.pause, keyboard.Key.cmd, 
    keyboard.Key.cmd_r, keyboard.Key.menu
]
SERVICE_KEYS = {k: k.name.upper() for k in _base_service_keys}

# Явно определяем модификаторы, чтобы левая и правая клавиши давали одно имя
SERVICE_KEYS.update({
    keyboard.Key.shift: 'SHIFT', keyboard.Key.shift_r: 'SHIFT',
    keyboard.Key.ctrl: 'CTRL', keyboard.Key.ctrl_r: 'CTRL',
    keyboard.Key.alt: 'ALT', keyboard.Key.alt_r: 'ALT', keyboard.Key.alt_gr: 'ALT'
})
# Отдельно обрабатываем пробел, чтобы он был символом, а не словом 'SPACE'
SERVICE_KEYS[keyboard.Key.space] = ' '
# Добавляем F1-F12
for i in range(1, 13):
    SERVICE_KEYS[getattr(keyboard.Key, f'f{i}')] = f'F{i}'

# --- ДОСТУП К WINAPI ДЛЯ ПОЛУЧЕНИЯ СОСТОЯНИЯ КЛАВИШ ---
user32 = ctypes.WinDLL('user32', use_last_error=True)
def get_key_state(vk_code):
    if vk_code in [VK_SHIFT, VK_CONTROL, VK_ALT]:
        return (user32.GetKeyState(vk_code) & 0x8000) != 0
    else:
        return (user32.GetKeyState(vk_code) & 0x0001) != 0

# --- ГЛАВНЫЙ ОБРАБОТЧИК НАЖАТИЙ ---
def on_press(key):
    state = {
        "shift": get_key_state(VK_SHIFT),
        "ctrl": get_key_state(VK_CONTROL),
        "alt": get_key_state(VK_ALT),
        "caps_lock": get_key_state(VK_CAPSLOCK),
        "num_lock": get_key_state(VK_NUMLOCK)
    }
    out_key = None
    if key in SERVICE_KEYS:
        out_key = SERVICE_KEYS[key]
    elif hasattr(key, 'vk'):
        vk = key.vk
        if 0x60 <= vk <= 0x6F:
            out_key = NUMPAD_MAP.get(vk) if state['num_lock'] else NUMPAD_OFF_MAP.get(vk)
        elif vk in VK_MAP:
            char = VK_MAP[vk]
            is_letter = 'a' <= char <= 'z'
            if state['shift'] and vk in VK_SHIFT_MAP:
                out_key = VK_SHIFT_MAP[vk]
            elif is_letter:
                is_upper = state['shift'] ^ state['caps_lock']
                out_key = char.upper() if is_upper else char
            else:
                out_key = char
    if out_key:
        event = {
            "type": "key_press",
            "key": out_key,
            "modifiers": { "shift": state['shift'], "ctrl": state['ctrl'], "alt": state['alt'] }
        }
        try:
            print(json.dumps(event, ensure_ascii=True), flush=True)
        except (OSError, BrokenPipeError):
            pass # Игнорируем ошибки при закрытии

def main():
    print("pyiohook server started.", file=sys.stderr, flush=True)
    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()

if __name__ == "__main__":
    main()