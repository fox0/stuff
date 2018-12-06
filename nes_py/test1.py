#!/usr/bin/env python3
import os
import sys
import logging

from nes.nes import Nes, Sprite
from nes.nes2 import Nes2

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    nes = Nes2()
    nes.parse('''
    /*
    const byte b=1, background_palette = [
        0x22, 0x29, 0x1A, 0x0F,  0x22, 0x36, 0x17, 0x0F,  0x22, 0x30, 0x21, 0x0F,  0x22, 0x27, 0x17, 0x0F
        ];
    */

    function reset() {
        sei();        // disable IRQs
        cld();        // disable decimal mode
        0x4017 = 64;  // disable APU frame IRQ
        "  LDX #$FF"
        "  TXS          ; Set up stack"
        0x2000 = 0;
        0x2001 = 0;
        0x4010 = 0;

        "forever:"
        "  JMP forever"
    }

    function nmi() {

    }
    ''')

    asm = nes.build()
    filename = sys.argv[0].rsplit('.', 1)[0]
    with open(filename + '.asm', 'w') as f:
        f.write(asm)
    os.system('nesasm %s.asm' % filename)
    os.system('nestopia %s.nes' % filename)

    sys.exit()

    app = Nes()
    app.background_palette = [
        0x22, 0x29, 0x1A, 0x0F,  0x22, 0x36, 0x17, 0x0F,  0x22, 0x30, 0x21, 0x0F,  0x22, 0x27, 0x17, 0x0F,
    ]
    app.sprite_palette = [
        0x3C, 0x16, 0x27, 0x18,  0x22, 0x1A, 0x30, 0x27,  0x22, 0x16, 0x30, 0x27,  0x22, 0x0F, 0x36, 0x17,
    ]
    app.sprites = [
        # x, y, ...
        Sprite(128, 128, 0x32, 0x00),  # 8x8
        Sprite(136, 128, 0x33, 0x00),
        Sprite(128, 136, 0x34, 0x00),
        Sprite(136, 136, 0x35, 0x00),
        # Sprite(136, 144, 0x32, 0x00),
        # Sprite(144, 136, 0x33, 0x00),
    ]
    app.include = 'mario.chr'

    app.compile()
    app.run()
