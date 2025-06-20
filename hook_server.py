import sys
import ctypes
import json
from pynput import keyboard

try:
    sys.stdout.reconfigure(encoding='utf-8')
except AttributeError:
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding='utf-8')

VK_CODE_TO_ENG = {
    0x41: 'a', 0x42: 'b', 0x43: 'c', 0x44: 'd', 0x45: 'e', 0x46: 'f', 0x47: 'g',
    0x48: 'h', 0x49: 'i', 0x4A: 'j', 0x4B: 'k', 0x4C: 'l', 0x4D: 'm', 0x4E: 'n',
    0x4F: 'o', 0x50: 'p', 0x51: 'q', 0x52: 'r', 0x53: 's', 0x54: 't', 0x55: 'u',
    0x56: 'v', 0x57: 'w', 0x58: 'x', 0x59: 'y', 0x5A: 'z',
    0x30: '0', 0x31: '1', 0x32: '2', 0x33: '3', 0x34: '4',
    0x35: '5', 0x36: '6', 0x37: '7', 0x38: '8', 0x39: '9',
    0xBA: ';', 0xBB: '=', 0xBC: ',', 0xBD: '-', 0xBE: '.',
    0xBF: '/', 0xC0: '`', 0xDB: '[', 0xDC: '\\', 0xDD: ']', 0xDE: "'",
    0x20: ' ', 0x09: 'TAB',
    0x60: '0', 0x61: '1', 0x62: '2', 0x63: '3', 0x64: '4',
    0x65: '5', 0x66: '6', 0x67: '7', 0x68: '8', 0x69: '9',
    0x6A: '*', 0x6B: '+', 0x6C: '\u000C', 0x6D: '-', 0x6E: '.', 0x6F: '/',
}

VK_CODE_SHIFTED = {
    0x31: '!', 0x32: '@', 0x33: '#', 0x34: '$', 0x35: '%',
    0x36: '^', 0x37: '&', 0x38: '*', 0x39: '(', 0x30: ')',
    0xBA: ':', 0xBB: '+', 0xBC: '<', 0xBD: '_', 0xBE: '>',
    0xBF: '?', 0xC0: '~', 0xDB: '{', 0xDC: '|', 0xDD: '}', 0xDE: '"',
}

SERVICE_KEYS = {
    keyboard.Key.enter: 'ENTER',
    keyboard.Key.backspace: 'BACKSPACE',
    keyboard.Key.esc: 'ESC',
    keyboard.Key.tab: 'TAB',
    keyboard.Key.caps_lock: 'CAPSLOCK',
    keyboard.Key.shift: 'SHIFT',
    keyboard.Key.shift_r: 'SHIFT',
    keyboard.Key.ctrl: 'CTRL',
    keyboard.Key.ctrl_r: 'CTRL',
    keyboard.Key.alt: 'ALT',
    keyboard.Key.alt_r: 'ALT',
    keyboard.Key.left: 'LEFT',
    keyboard.Key.up: 'UP',
    keyboard.Key.right: 'RIGHT',
    keyboard.Key.down: 'DOWN',
    keyboard.Key.delete: 'DELETE',
    keyboard.Key.home: 'HOME',
    keyboard.Key.end: 'END',
    keyboard.Key.page_up: 'PAGEUP',
    keyboard.Key.page_down: 'PAGEDOWN',
    keyboard.Key.num_lock: 'NUMLOCK',
    keyboard.Key.print_screen: 'PRINTSCREEN',
    keyboard.Key.pause: 'PAUSE',
    keyboard.Key.cmd: 'WIN',
    keyboard.Key.cmd_r: 'WIN',
    keyboard.Key.menu: 'APPS',
}
# F1-F12
for i in range(1, 13):
    SERVICE_KEYS[getattr(keyboard.Key, f"f{i}")] = f"F{i}"

user32 = ctypes.WinDLL('user32', use_last_error=True)
GetKeyState = user32.GetKeyState
GetKeyState.argtypes = [ctypes.c_int]
GetKeyState.restype = ctypes.c_short

def is_shift_pressed():
    return (GetKeyState(0x10) & 0x8000) != 0

def on_press(key):
    out = None
    shift = is_shift_pressed()
    if key in SERVICE_KEYS:
        out = SERVICE_KEYS[key]
    elif hasattr(key, 'vk') and key.vk in VK_CODE_TO_ENG:
        vk = key.vk
        if 0x60 <= vk <= 0x69 or 0x6A <= vk <= 0x6F:
            out = VK_CODE_TO_ENG[vk]
        elif shift and vk in VK_CODE_SHIFTED:
            out = VK_CODE_SHIFTED[vk]
        else:
            out = VK_CODE_TO_ENG[vk]
    if out:
        event = {"type": "key_press", "key": out}
        print(json.dumps(event, ensure_ascii=True), flush=True)

def main():
    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()

if __name__ == "__main__":
    main()
