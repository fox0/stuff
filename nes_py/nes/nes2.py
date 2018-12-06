import logging
from pyparsing import ParseBaseException, ParseResults
from nes.tokens import nes

log = logging.getLogger(__name__)


class Const(object):
    def __init__(self, type_, name, value):
        self.type_ = type_
        self.name = name
        self.value = value  # todo hex

    def __str__(self):
        result = ['%s:' % self.name]
        t = {
            'byte': 'db',
            # todo
        }[self.type_]
        result.append('  .%s %s' % (t, ','.join(self.value)))
        return '\n'.join(result)


class Nes2(object):
    # $0000-0800 - Internal RAM, 2KB chip in the NES
    # $2000-2007 - PPU access ports
    # $4000-4017 - Audio and controller access ports
    # $6000-7FFF - Optional WRAM inside the game cart
    # $8000-FFFF - Game cart ROM

    def __init__(self):
        self.ines_mirroring = True  # vertical mirroring set
        self.ines_mapper = False  # mapper set

        self._ram = {}
        self._code = []
        self._rom = []
        self._register_x = None

    def parse(self, string):
        try:
            ast = nes.parseString(string, parseAll=True)
        except ParseBaseException as e:
            log.error('\n'.join(('Parse error', e.line, ' ' * (e.column - 1) + '^', e.__str__())))
            return

        for i in ast:
            assert isinstance(i, ParseResults)
            log.debug(i)
            self._s(i)

    def _s(self, i):
        token = i.getName()
        if token == 'const':
            self._const(i)
        elif token == 'func':
            self._function(i)
        else:
            raise NotImplementedError

    def _const(self, i):
        type_ = i[1]
        for name, _, value in i[2]:
            self._rom.append(Const(type_, name, value))

    def _function(self, i):
        name, ls = i
        self._code.append('%s:' % name)
        for i2 in ls:
            assert isinstance(i2, ParseResults)
            self._operator(i2)

    def _operator(self, i):
        token = i.getName()
        if token == 'call':
            self._call(i)
        # else:
        #     raise NotImplementedError

    def _call(self, i):
        name, = i
        if name in ('sei', 'cld'):
            self._code.append('  %s' % name)
        else:
            raise NotImplementedError

    def _operator1(self, i):
        string = i[0]
        if string[0] == '"' and string[-1] == '"':
            self._code.append(string[1:-1])
        else:
            raise NotImplementedError

    def _operator4(self, i):
        if i[0] == '0x':  # 0x1234 = 123;
            register = i[1]
            const = i[3]
            self._set_x(const)
            self._code.append('  stx $%s' % register)
        else:
            raise NotImplementedError

    def _set_x(self, x):
        x = int(x)
        if x != self._register_x:
            self._register_x = x
            self._code.append('  ldx #$%02x' % self._register_x)

            # LDA #$00 a =0

    def __str__(self):
        return self.build()

    def build(self):
        result = []

        # nes
        result.append('  .inesprg 1')  # x16KB
        result.append('  .ineschr 0')  # x8KB
        result.append('  .inesmap %d' % (1 if self.ines_mapper else 0))
        result.append('  .inesmir %d' % (1 if self.ines_mirroring else 0))

        # ram
        result.append('  .rsset $0000')
        # todo

        # code
        result.append('  .bank 0')
        result.append('  .org $C000')
        result += self._code

        # rom
        result.append('  .bank 1')
        result.append('  .org $E000')
        for i in self._rom:
            assert isinstance(i, Const)
            result.append(i.__str__())

        # irq
        result.append('  .org $FFFA')
        result.append('  .dw nmi')
        result.append('  .dw reset')
        result.append('  .dw 0')

        result.append('  .bank 2')
        result.append('  .org $0000')

        r = '\n'.join(result)
        log.debug('asm:\n%s', r)
        return r
