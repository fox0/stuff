//sizeof(char)  1
//sizeof(int)   2
//sizeof(long)  4

#if defined(DEBUG)
#define PRINT(i)    Serial.print(i)
#define PRINTLN(i)  Serial.println(i)
#define PRINTF(i)   Serial.print(F(i))
#define PRINTLNF(i) Serial.println(F(i))
#define PRINTH(i)   Serial.print(i,HEX)
#define PRINTLNH(i) Serial.println(i,HEX)
#define PRINTLNE    Serial.println()
//const __FlashStringHelper* _ok = reinterpret_cast<const __FlashStringHelper *>(PSTR("ok");
//const __FlashStringHelper* _fail = (const __FlashStringHelper*)"fail";
//TODO const __???
#define OK          Serial.println(F("ok")) 
#define FAIL        Serial.println(F("fail")) 
#else
#define PRINT(i)    ;
#define PRINTLN(i)  ;
#define PRINTF(i)   ;
#define PRINTLNF(i) ;
#define PRINTH(i)   ;
#define PRINTLNH(i) ;
#define PRINTLNE    ;
#define OK          ;
#define FAIL        ;
#endif

#define null NULL
#define NOP __asm__ __volatile__ ( "nop" "\n\t" :: )

void (*soft_reset)() = 0;

int free_ram() {
  extern int __heap_start, *__brkval; 
  int v; 
  return (int)&v - (__brkval == 0 ? (int)&__heap_start : (int)__brkval); 
}

//byte get_port(byte port) //прочитать регистр порта
#define get_port(i) *portInputRegister(i)

//void set_port(byte port, byte val) //записать в регистр порта
#define set_port(i,val) *portOutputRegister(i)=val

//void set_mode(byte port, byte model) //режим порта 1=OUT
#define set_mode(i,mode) *portModeRegister(i)=mode

//byte eeprom_read(byte index)
#define eeprom_read(i) eeprom_read_byte((const uint8_t*)(i))

//void eeprom_write(byte index, byte val)
#define eeprom_write(i,val) eeprom_write_byte((uint8_t*)(i),(val))

#undef EEMEM //не работает

//работает в СОТНЮ раз медленнее чем прямой вывод в порт
#define on(i) digitalWrite(i, HIGH)
#define off(i) digitalWrite(i, LOW)
#define in(i) pinMode(i, INPUT)
#define in_pull(i) pinMode(i, INPUT_PULLUP)
#define out(i) pinMode(i, OUTPUT)
#define get_pin(i) digitalRead(i) //медленно

//#define SEND(b,k) Wire.beginTransmission(0);Wire.write(b,k);Wire.endTransmission()

/*
#if defined(__AVR_ATmega2560__)
#  define INT_PIN2  0
#  define INT_PIN3  1
#  define INT_PIN21 2
#  define INT_PIN20 3
#  define INT_PIN19 4
#  define INT_PIN18 5
//#elif defined(__AVR_ATmega2560__) //TODO
//Uno 0 and 1
#else
#  error "TODO INT_PIN"
#endif
*/
