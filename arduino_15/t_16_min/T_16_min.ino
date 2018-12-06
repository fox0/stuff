#define ID_DEV  1   //номер аудитории

/** пины: **/
#define LED_G    9   //green LED
#define LED_R    A0  //reg LED
#define BUT      11  //iButton
#define LED      13  

#define SLEEP    delay(5000)//ms

#include <avr/power.h>
#include <avr/eeprom.h>
#include <Arduino.h>
#include <Wire.h>
#include <OneWire.h>
#include "macros.h"
#if !defined(__AVR_ATmega328P__)
#error "Only ATmega328P"
#endif

//глобальные переменные:
byte addr[8];//key5 and key6

//iButton
OneWire ibutton(BUT);

inline void open(){//5 сек.
  off(LED_G);
  SLEEP;  
  on(LED_G);
}

inline void fail(){//5 сек.
  on(LED_R);
  SLEEP;  
  off(LED_R);
}

inline void error(){//3 сек.
  for(register byte i=0;i<6;i++){
    on(LED_R);  delay(250);
    off(LED_R); delay(250);
  }
}

inline void blink(){//10 ms
  on(LED_R);  delay(50);
  off(LED_R); delay(50);
}

void func6(){//ключ
  if (!ibutton.search(addr)) {
    off(LED);
    ibutton.reset_search();
    return;
  }
  on(LED);
  if (addr[0] != 0x01) return;
  if (OneWire::crc8(addr, 7) != addr[7]) return;
  ibutton.reset();

  Wire.beginTransmission(0);
  Wire.write(16);
  Wire.write(ID_DEV);
  Wire.write(addr[1]);
  Wire.write(addr[2]);
  Wire.write(addr[3]);
  Wire.write(addr[4]);
  Wire.write(addr[5]);
  Wire.write(addr[6]);
  if(Wire.endTransmission()!=0) error();
  else m();
}

void m(){
  register byte b = 2;
  for(register byte i=0;i<50;i++){//50 запросов. 50*100 = 5 с.
    blink();
    if(Wire.requestFrom(0,1)>0) {
      b = Wire.read();
      if(b!=2) break;
    }
  }
  switch(b) {
    case 0://ok
      open(); return;
    case 1://fail
      fail(); return;
    default:
      error(); return;
  }
}

inline void init_led(){
  out(LED);
  out(LED_G);
  out(LED_R);
  func0();
}

void func0(){//DEBUG
  off(LED);
  on(LED_G);
  off(LED_R);
}

inline void init_i2c(){
  Wire.begin(ID_DEV);
  Wire.beginTransmission(0);
  Wire.write(0);
  Wire.write(ID_DEV);
  Wire.write(eeprom_read(0));
  Wire.write(eeprom_read(1));
  Wire.write(eeprom_read(2));
  Wire.write(eeprom_read(3));
  Wire.write(free_ram()/8);
  if(Wire.endTransmission()!=0) error();
  else blink();
}

int main() {
  init(); //setup core arduino
  init_led();
  init_i2c();
  for (;;) {
    func6();
    func0();//debug
  }
}//end main
/*
Sketch uses 9 738 bytes (31%) of program storage space.
*/

