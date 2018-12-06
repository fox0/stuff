# -*- coding: utf-8 -*-
import os
import sys


class Sprite(object):
    """Спрайт"""
    def __init__(self, x, y, tile_id, attr):
        self.x = x
        self.y = y
        self.tile_id = tile_id
        self.attr = attr


class Nes(object):
    def __init__(self):
        self.name = sys.argv[0].rsplit('.', 1)[0]

        self.ines_prg = 16 * 1024  # PRG-ROM set
        self.ines_chr = 8 * 1024  # CHR-ROM set
        self.ines_mirroring = True  # vertical mirroring set
        self.ines_mapper = False  # mapper set

        self.background_palette = []
        self.sprite_palette = []
        self.sprites = []
        self.include = None

    def compile(self):
        with open(self.name + '.asm', 'w') as f:
            f.write(self._build())
        # TODO парсить ошибки в stdout
        os.system('nesasm %s.asm' % self.name)

    def run(self):
        os.system('nestopia %s.nes' % self.name)

    def _build(self):
        # $0000-0800 - Internal RAM, 2KB chip in the NES
        # $2000-2007 - PPU access ports
        # $4000-4017 - Audio and controller access ports
        # $6000-7FFF - Optional WRAM inside the game cart
        # $8000-FFFF - Game cart ROM
        result = []
        result.extend(self._asm_ines())
        result.extend(self._asm_ram())
        result.extend(self._asm_reset_function())
        result.extend(self._asm_nmi_function())
        result.extend(self._asm_rom())
        result.extend(self._asm_bin())
        return '\n'.join(result)

    def _asm_ines(self):
        assert self.ines_prg % 16 * 1024 == 0
        assert self.ines_chr % 8 * 1024 == 0
        return [
            '  .inesprg %d' % (self.ines_prg // (16 * 1024)),
            '  .ineschr %d' % (self.ines_chr // (8 * 1024)),
            '  .inesmap %d' % (1 if self.ines_mapper else 0),
            '  .inesmir %d' % (1 if self.ines_mirroring else 0),
        ]

    def _asm_ram(self):
        return [
            '  .rsset $0000',
            # TODO
        ]

    def _asm_reset_function(self):
        result = []
        result.extend(self._asm_init())
        result.extend(self._asm_vblankwait(label='vblankwait1'))
        result.extend(self._asm_clrmem())
        result.extend(self._asm_vblankwait(label='vblankwait2'))
        if self.background_palette and self.sprite_palette:
            result.extend(self._asm_load_palettes())
            if self.sprites:
                result.extend(self._asm_load_sprites())
        result.extend(self._asm_forever())
        return result

    @staticmethod
    def _asm_init():
        return '''
  .bank 0
  .org $C000

RESET:
  SEI          ; disable IRQs
  CLD          ; disable decimal mode
  LDX #$40
  STX $4017    ; disable APU frame IRQ
  LDX #$FF
  TXS          ; Set up stack
  LDX #$00
  STX $2000    ; disable NMI
  STX $2001    ; disable rendering
  STX $4010    ; disable DMC IRQs'''.split('\n')

    @staticmethod
    def _asm_vblankwait(label):
        result = '''
%s:       ; wait for vblank to make sure PPU is ready
  BIT $2002
  BPL %s''' % (label, label)
        return result.split('\n')

    @staticmethod
    def _asm_clrmem():
        return '''
clrmem:
  LDA #$00
  STA $0000, x
  STA $0100, x
  STA $0300, x
  STA $0400, x
  STA $0500, x
  STA $0600, x
  STA $0700, x
  LDA #$FE
  STA $0200, x
  INX              ; X += 1
  BNE clrmem'''.split('\n')

    @staticmethod
    def _asm_load_palettes():
        return '''
LoadPalettes:
  LDA $2002             ; read PPU status to reset the high/low latch
  LDA #$3F
  STA $2006             ; write the high byte of $3F00 address
  LDA #$00
  STA $2006             ; write the low byte of $3F00 address
  LDX #$00              ; X = 0
LoadPalettesLoop:
  LDA palette, x        ; load data from address (palette + x)
  STA $2007             ; write to PPU
  INX                   ; X += 1
  CPX #$20              ; 32
  BNE LoadPalettesLoop'''.split('\n')

    def _asm_load_sprites(self):
        result = '''
LoadSprites:
  LDX #$00              ; X = 0
LoadSpritesLoop:
  LDA sprites, x        ; load data from address (sprites + x)
  STA $0200, x          ; store into RAM address ($0200 + x)
  INX                   ; X += 1
  CPX #${:02x}
  BNE LoadSpritesLoop'''.format(len(self.sprites) * 4)
        return result.split('\n')

    @staticmethod
    def _asm_forever():
        # TODO!
        return '''
  LDA #%10000000   ; enable NMI, sprites from Pattern Table 1
  STA $2000

  LDA #%00010000   ; enable sprites
  STA $2001

forever:
  JMP forever'''.split('\n')

    def _asm_nmi_function(self):
        return '''
NMI:
;  LDA #$00
;  STA $2003       ; set the low byte (00) of the RAM address
  LDA #$02
  STA $4014       ; set the high byte (02) of the RAM address, start the transfer

StartInput:
  LDA #$01
  STA $4016
  LDA #$00
  STA $4016

; Reading A button
StartA:
  LDA $4016
  AND #%00000001
  BEQ EndA
EndA:

; Reading B button
StartB:
  LDA $4016
  AND #%00000001
  BEQ EndB
EndB:

; Reading Select button
StartSelect:
  LDA $4016
  AND #%00000001
  BEQ EndSelect
EndSelect:

; Reading Start button
StartStart:
  LDA $4016
  AND #%00000001
  BEQ EndStart
EndStart:

; Reading Up button
StartUp:
  LDA $4016
  AND #%00000001
  BEQ EndUp
  LDA $0200       ; Y position
  SEC
  SBC #$01        ; Y = Y - 1
  STA $0200

  LDA $0204       ; Y position
  SEC
  SBC #$01        ; Y = Y - 1
  STA $0204

  LDA $0208       ; Y position
  SEC
  SBC #$01        ; Y = Y - 1
  STA $0208

  LDA $020C       ; Y position
  SEC
  SBC #$01        ; Y = Y - 1
  STA $020C

EndUp:

; Reading Down button
StartDown:
  LDA $4016
  AND #%00000001
  BEQ EndDown
  LDA $0200       ; Y position  ;sprite 0 + (y, id, att, x)
  CLC
  ADC #$01        ; Y = Y + 1
  STA $0200
EndDown:

; Reading Left button
StartLeft:
  LDA $4016
  AND #%00000001
  BEQ EndLeft
  LDA $0203       ; X Position
  SEC
  SBC #$01        ; X = X - 1
  STA $0203
EndLeft:

; Reading Right button
StartRight:
  LDA $4016
  AND #%00000001
  BEQ EndRight
  LDA $0203       ; X Position
  CLC
  ADC #$01        ; X = X + 1
  STA $0203
EndRight:




  RTI'''.split('\n')

    def _asm_rom(self):
        result = []
        result.extend('''
  .bank 1
  .org $E000'''.split('\n'))
        if self.background_palette and self.sprite_palette:
            result.extend(self._asm_rom_palettes())
            if self.sprites:
                result.extend(self._asm_rom_sprites())
        result.extend('''
  .org $FFFA
  .dw NMI
  .dw RESET
  .dw 0'''.split('\n'))
        return result

    def _asm_rom_palettes(self):
        assert len(self.background_palette) == 16
        assert len(self.sprite_palette) == 16
        return [
            'palette:',
            '  .db ' + ','.join('${:02x}'.format(i) for i in self.background_palette),
            '  .db ' + ','.join('${:02x}'.format(i) for i in self.sprite_palette),
        ]

    def _asm_rom_sprites(self):
        result = ['sprites:']
        for i in self.sprites:
            assert isinstance(i, Sprite)
            result.append('  .db ${:02x},${:02x},${:02x},${:02x}'.format(i.y, i.tile_id, i.attr, i.x))
        return result

    def _asm_bin(self):
        result = ['', '  .bank 2', '  .org $0000']
        if self.include:
            result.append('  .incbin "%s"' % self.include)
        return result
