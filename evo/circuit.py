"""Small original pinout helper. Not a hardware-control driver."""

PARTS = {
    ('arduino-uno', 'dht11'): {
        'links': [('VCC', '5V'), ('DATA', 'D2'), ('GND', 'GND')],
        'note': 'Use 5V. Add a 10k pull-up on DATA if the module does not include one.',
        'sketch': 'read DHT11 on digital pin 2 and print humidity and temperature',
    },
    ('esp32', 'hc-sr04'): {
        'links': [('VCC', '5V'), ('TRIG', 'GPIO5'), ('ECHO', 'GPIO18'), ('GND', 'GND')],
        'note': 'ECHO is 5V. Level-shift it before an ESP32 input.',
        'sketch': 'pulse TRIG and time ECHO',
    },
}


def connection_plan(board: str, part: str) -> dict:
    key = (board.strip().lower(), part.strip().lower())
    plan = PARTS.get(key)
    if plan is None:
        return {'known': False, 'board': board, 'part': part, 'links': []}
    return {'known': True, 'board': key[0], 'part': key[1], **plan}
