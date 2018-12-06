#define DEBUG //отладка
//#define LOCALHOST

#if !defined(__AVR_ATmega2560__)
#error "Only ATmega2560!"
#endif

#if defined(LOCALHOST)
#define SITE "localhost"
#define IP_site IPAddress site(192,168,6,2)
#else
#define SITE "<skip>"
#endif

#define LOG "LOG.TXT"
#define BUF_HTTP 512
#define SPACE 238 //скан код '#' на клавиатуре

#include <avr/power.h>
#include <avr/sleep.h>  //-
#include <avr/eeprom.h>
#include <Arduino.h>
#include <Wire.h>
#include <SPI.h>
#include <Ethernet.h>
#include <utility/w5100.h>
#include <Dns.h>
#include <SD.h>
#include "macros.h"
#include "Buffer.cpp"

//глобальные переменные:
byte i4 = 0;
byte i5 = 0;
byte i6 = 0;
byte **key4;//byte key4[i4][10];//fix
byte **key5;//byte key5[i5][6];
byte **key6;//byte key6[i6][7];

// T <<< M
byte status = 2;
// Т >>> M
byte index=0, mas[32];
// M >>> S
byte i_s=0, mas_s[10][32], mas_i[10];//памяти всем хватит
// M <<< S
byte is_update=0;

//функции:
void int1() {
  //M >>> Т
  Wire.write(status);
  status = 2;
}

void int2(int kol) {
  //Т >>> M
  index = 0;
  while(Wire.available()>0) {
    mas[index++]=Wire.read();
  }
  if(index!=0) {
    route();
    //save log
    for(register byte i=0;i<index;i++){
      mas_s[i_s][i]=mas[i];
    }
    mas_i[i_s++]=index;
  }
}

inline void route() {
  switch(mas[0]) {
    case 0://включился
    case 4://логи
    case 5:
    case 6:
      return;
    case 14://запросы
      case14();
      return;
    case 15:
      case15();
      return;
    case 16:
      case16();
      return;
    default:
      PRINTF("Internal error ");PRINTLN(mas[0]);
      return;
  }
}

inline void case14() {
#if defined(DEBUG)
  PRINTF("T> ");
  for(register byte i=1;i<index;i++){
    PRINT(mas[i]); PRINT(' ');   
  }
  PRINTLNE;
#endif
  for(register byte i=0;i<i4;i++){
    PRINTF(">>>");
    register byte flag = 1;
    for(byte j=0;j<index-1;j++){
      PRINT(key4[i][j]); PRINT(' '); 
      if (key4[i][j] != mas[j+1]) {
        flag = 0;
        break;
      }
    }
    PRINTLNE;
    if (flag==0) continue;
    PRINTLNF("find");
    status = 0;//ok
    return;     
  }//end for
  PRINTLNF("not find");
  mas[0] = 24;
}

inline void case15() {
  PRINTF("T> ");PRINT(mas[1]);
  PRINT(' ');  PRINT(mas[2]);
  PRINT(' ');  PRINT(mas[3]);
  PRINT(' ');  PRINT(mas[4]);
  PRINT(' ');  PRINT(mas[5]);
  PRINT(' ');PRINTLN(mas[6]);
  for(register byte i=0;i<i5;i++){
    PRINTF(">>>");PRINT(key5[i][0]);
    PRINT(' ');  PRINT(key5[i][1]);
    PRINT(' ');  PRINT(key5[i][2]);
    PRINT(' ');  PRINT(key5[i][3]);
    PRINT(' ');  PRINT(key5[i][4]);
    PRINT(' ');PRINTLN(key5[i][5]);
    if (key5[i][0] != mas[1]) continue;
    if (key5[i][1] != mas[2]) continue;
    if (key5[i][2] != mas[3]) continue;
    if (key5[i][3] != mas[4]) continue;
    if (key5[i][4] != mas[5]) continue;
    if (key5[i][5] != mas[6]) continue;
    PRINTLNF("find");
    status = 0;//ok
    return;      
  }
  PRINTLNF("not find");
  mas[0] = 25;
}

inline void case16() {
  PRINTF("T> ");PRINT(mas[1]);
  PRINT(' ');  PRINT(mas[2]);
  PRINT(' ');  PRINT(mas[3]);
  PRINT(' ');  PRINT(mas[4]);
  PRINT(' ');  PRINT(mas[5]);
  PRINT(' ');  PRINT(mas[6]);
  PRINT(' ');PRINTLN(mas[7]);
  for(register byte i=0;i<i6;i++){
    PRINTF(">>>");PRINT(key6[i][0]);
    PRINT(' ');  PRINT(key6[i][1]);
    PRINT(' ');  PRINT(key6[i][2]);
    PRINT(' ');  PRINT(key6[i][3]);
    PRINT(' ');  PRINT(key6[i][4]);
    PRINT(' ');  PRINT(key6[i][5]);
    PRINT(' ');PRINTLN(key6[i][6]);
    if (key6[i][0] != mas[1]) continue;
    if (key6[i][1] != mas[2]) continue;
    if (key6[i][2] != mas[3]) continue;
    if (key6[i][3] != mas[4]) continue;
    if (key6[i][4] != mas[5]) continue;
    if (key6[i][5] != mas[6]) continue;
    if (key6[i][6] != mas[7]) continue;
    PRINTLNF("find");
    status = 0;//ok
    return;       
  }
  PRINTLNF("not find");
  mas[0] = 26;
}

inline void log(byte* str, byte kol){
  PRINTF("open file...");
  File f = SD.open(LOG, FILE_WRITE);
  if(!f) {
    FAIL;
    return;
  }
  OK;
  f.write(str,kol);
  f.close();
}

void send(byte* str, byte kol){
  //попытка записи логов на SD карту
  log(str,kol);
  /** создаём заголовки **/
  Buffer b(BUF_HTTP);//bytes
#if defined(LOCALHOST)
  b.print(F("GET /<skip> HTTP/1.1\r\nHost: "SITE"\r\nUser-Agent: <skip>"));
#else
  b.print(F("GET /?m=fox HTTP/1.1\r\nHost: "SITE"\r\nUser-Agent: <skip>"));
#endif
  PRINTF("M> ");
  b.print(str[0]); PRINT(str[0]);
  for(byte i=1;i<kol;i++){
    b.print('.');   PRINT('.');
    b.print(str[i]);PRINT(str[i]);
  }
  b.print(F("\r\nConnection: close\r\n\r\n"));
  PRINTF("\nS> ");
  /** отправляем **/
  EthernetClient conn;
#if defined(LOCALHOST)
  IP_site;
  if (!conn.connect(site, 80)) {
#else
  if (!conn.connect(SITE, 80)) {
#endif
    FAIL;
    return; 
  }
  //PRINTLNF("DEBUG>>");PRINTLN(b.get());
  conn.write(b.get());
  conn.flush();
  delay(10);//ms
  /** принимаем **/
  b.clear();
  do {
    while(conn.available()) b.print((char)conn.read());
    delay(10);//ms
  } while(conn.connected());
  conn.stop();//close();  
  //PRINTLNF("DEBUG>>");PRINTLN(b.get());
  /** парсим **/
  if(b.get(9) !='2') goto error;
  if(b.get(10)!='0') goto error;
  if(b.get(11)!='0') goto error;
  goto next;
error:
  PRINTF("Error ");
  PRINT(b.get(9));
  PRINT(b.get(10));
  PRINT(b.get(11));
  PRINTLNE;
  return;
next:
  for(int i=12;i<512;) {
    if(b.get(i++)!='\r') continue;
    if(b.get(i++)!='\n') continue;
    if(b.get(i++)!='\r') continue;
    if(b.get(i++)!='\n') continue;
#if defined(DEBUG)
    bool bug=false;
#endif 
    if(b.get(i)>3) {//TODO if(b.len()-i>1) /////////////////////////////////////////////////
      i+=3;//осторожно, костыль!
#if defined(DEBUG)
      bug=true;
#endif
    }
    PRINT((byte)b.get(i));PRINT(' ');
    switch(b.get(i)){
      case 0:
        OK;
        return;
      case 1:
        status=0;//ok
        PRINTLNF("status=0 -> ok"); 
        return;
      case 2:
        status=1;//fail
        PRINTLNF("status=1 -> fail");
        return;
      case 3:
        is_update=1;
        PRINTLNF("update = true");
        return;
      default:
#if defined(DEBUG)
        if (bug) i-=3;
        PRINTF("Internal error!!!\nS_DEBUG>>>");
        for (int j=i;j<b.len();j++) {
          PRINT((byte)b.get(j));PRINT(' ');
        }
        PRINTLNE;
#endif
        return;
    }//end switch
  }//end for
}

inline void update0(){
  PRINTLNF("update0... ");
  /** отправляем **/
  EthernetClient conn;
#if defined(LOCALHOST)
  IP_site;
  if (!conn.connect(site, 80)) {
#else
  if (!conn.connect(SITE, 80)) {
#endif  
    PRINTLNF("server FAIL!");
    return; 
  }
#if defined(LOCALHOST)
  conn.write("GET /<skip> HTTP/1.1\r\nHost: "SITE"\r\nConnection: close\r\n\r\n");
#else
  conn.write("GET /data.bin HTTP/1.1\r\nHost: "SITE"\r\nConnection: close\r\n\r\n");
#endif
  conn.flush();
  delay(10);//ms
  /** принимаем и парсим **/
  do {
    if(conn.available()<=0) {
      delay(10);
      continue;
    }
    if(conn.read()!='\r') continue;
    if(conn.read()!='\n') continue;
    if(conn.read()!='\r') continue;
    if(conn.read()!='\n') continue;
    register int index = 0;
    do {
      if(conn.available()<=0) {
        delay(10);
        continue;
      }
      eeprom_write(index++,conn.read());
    } while(conn.connected());
    conn.stop();
    byte a[2];
    a[0]=2;
    a[1]=0;//id
    OK;
    send(a,2);//update ok
#if defined(DEBUG)
    PRINTF("reset...");
    register byte i=5;
    do {
      PRINT(i--);
      PRINTF("...");
      delay(1000);
    } while(i!=0);
    PRINTLNE;
#endif
    soft_reset();
  } while(conn.connected());
  conn.stop();
}

inline void update1(){
  PRINTF("update1");
  /** отправляем **/
  EthernetClient conn;
#if defined(LOCALHOST)
  IP_site;
  if (!conn.connect(site, 80)) {
#else
  if (!conn.connect(SITE, 80)) {
#endif  
    PRINTLNF("server FAIL!");
    return; 
  }
#if defined(LOCALHOST)
  conn.write("GET /<skip> HTTP/1.1\r\nHost: "SITE"\r\nConnection: close\r\n\r\n");
#else
  conn.write("GET /id1.bin HTTP/1.1\r\nHost: "SITE"\r\nConnection: close\r\n\r\n");
#endif
  conn.flush();
  delay(10);//ms
  /** принимаем и парсим **/
  do {
    if(conn.available()<=0) {
      delay(10);
      continue;
    }
    if(conn.read()!='\r') continue;
    if(conn.read()!='\n') continue;
    if(conn.read()!='\r') continue;
    if(conn.read()!='\n') continue;
    Wire.beginTransmission(1);
    Wire.write(0);//begin
    if(Wire.endTransmission()!=0) {
      FAIL;
      break;
    }
    PRINT('.');
    register int index = 0;
    byte asd[32];
    do {
      if(conn.available()<=0) {
        delay(10);
        continue;
      }
      asd[index++] = conn.read();
      if(index>=32){
        index=0;
        Wire.beginTransmission(1);
        Wire.write(asd,32);
        if(Wire.endTransmission()!=0) {
          PRINTLNF("fail");
          break;
        }
        PRINT('.');
      }    
    } while(conn.connected());
    if(index!=0){
      Wire.beginTransmission(1);
      Wire.write(asd,32);
      if(Wire.endTransmission()!=0) {
        FAIL;
        break;
      }
      PRINT('.');
    }
    Wire.beginTransmission(1);
    Wire.write(2);//end
    if(Wire.endTransmission()!=0) {
      FAIL;
      break;
    }
    OK;
    mas_s[i_s][0] = 2; //update ok
    mas_s[i_s][1] = 1; //id
    mas_i[i_s++]  = 2; //len
  } while(conn.connected());
  conn.stop();
}
////////////////////////////////////////////////////////////////////////
inline void init_power(){
  PRINTF("Выключение неиспользуемых модулей... ");
  //power_all_disable();
  power_adc_disable();
  //power_spi_disable();
  //power_timer0_disable();
  power_timer1_disable();
  power_timer2_disable();
  power_timer3_disable();
  power_timer4_disable();
  power_timer5_disable();
  //power_twi_disable();
#if !defined(DEBUG)
  power_usart0_disable();
#endif
  power_usart1_disable(); 
  power_usart2_disable();
  power_usart3_disable();
  OK;
}
inline void init_mem(){
  PRINTF("Загрузка данных в память... ");
  //eeprom_write(0,0);eeprom_write(1,0);eeprom_write(2,0);//DEBUG
  i4 = eeprom_read(0);
  i5 = eeprom_read(1);
  i6 = eeprom_read(2);
  PRINT(i4);PRINT(' ');PRINT(i5);PRINT(' ');PRINTLN(i6);
  PRINTF("  read4 ");
  register int index = 3;
  key4 = new byte*[i4];
  for(register byte i=0;i<i4;i++){
    key4[i] = new byte[10];
    register byte j = 0, b;
    do {
      b = eeprom_read(index++);
      key4[i][j++] = b;
      if(j>10) {
        i4=0;//если данные в памяти битые
        FAIL;
        break;
      } 
    } while (b!=SPACE);
    PRINT('.');
  }
  OK;
  PRINTF("  read5 ");
  key5 = new byte*[i5];
  for(register byte i=0;i<i5;i++){
    key5[i] = new byte[6];
    for(register byte j=0;j<6;j++){
      key5[i][j] = eeprom_read(index++);
    }
    PRINT('.');
  }
  OK;
  PRINTF("  read6 ");
  key6 = new byte*[i6];
  for(register byte i=0;i<i6;i++){
    key6[i] = new byte[7];
    for(register byte j=0;j<7;j++){
      key6[i][j] = eeprom_read(index++);
    }
    PRINT('.');
  }
  OK;
  register int qqq = free_ram();
#if defined(__AVR_ATmega2560__)
  PRINT(qqq);PRINTF(" байт (");PRINT(qqq/82);PRINTLNF("%) cвободно ОЗУ.");//8 192
  qqq = 1024-index;
  PRINT(qqq);PRINTF(" байт (");PRINT(qqq/10);PRINTLNF("%) cвободно ПЗУ.");//1 024
#else
  PRINT(index);PRINTF(" байт (??%) занято ПЗУ.\n  ");
  PRINT(qqq);PRINTLNF(" байт (??%) cвободно ОЗУ.");
#endif
}
inline void init_sd(){
  PRINTF("Инициализация SD-карты... ");
  out(4);
  if (!SD.begin(4)) {
    FAIL;
  } else {
    OK;
  }
  //информация о карте
  //тесты попытка создать файл
}
#if defined(DEBUG)
inline void init_eth3(){
  byte b[6];
  W5100.getMACAddress(b);
  PRINTF("  mac     = "); PRINTH(b[0]);
  for(byte i=1;i<6;i++){PRINT(':');PRINTH(b[i]);}
  PRINTLNE;
}
inline void init_eth2(){
  init_eth3();
  union {
    uint32_t i;
    uint8_t b[4];
  } t;
  W5100.getIPAddress(t.b);
  PRINTF("  ip      = ");PRINTLN((IPAddress)t.i);
  W5100.getSubnetMask(t.b);
  PRINTF("  netmask = ");PRINTLN((IPAddress)t.i);
  W5100.getGatewayIp(t.b);
  PRINTF("  gateway = ");PRINTLN((IPAddress)t.i);
  t.i = Ethernet.dnsServerIP();
  PRINTF("  dns     = ");PRINTLN((IPAddress)t.i);
  PRINTF(SITE"... ");
#if defined(LOCALHOST)
  IP_site;
  PRINT(site);PRINTF("... ");
  EthernetClient conn;
  if (conn.connect(site, 80)) {
    conn.stop();
    OK;
    return;
  }
#else
  //обратиться к днс, получить и сохранить адрес.
  DNSClient dns;
  dns.begin(t.i);
  if (dns.getHostByName(SITE, (IPAddress&)t.i)==1) {
    PRINTLN((IPAddress)t.i);
    return;
  }
#endif
  FAIL;
}
#endif
inline void init_eth(){
  //00:14:5E:A4:36:27
  const byte mac[] = {0x00, 0x14, 0x5E, 0xA4, 0x36, 0x27};
#if defined(LOCALHOST)
  IPAddress ip(192, 168, 6, 3);
  IPAddress dns(192, 162, 6, 2);
  IPAddress gateway(192, 168, 6, 1);
  IPAddress subnet(255, 255, 255, 0);
  Ethernet.begin((uint8_t*)mac, ip, dns, gateway, subnet);
#else
  PRINTF("Получение ip-адреса по dhcp... ");
  if (Ethernet.begin((uint8_t*)mac) != 0) {
    OK;
  } else {
    FAIL;
    IPAddress ip(10, 1, 11, 92);
    IPAddress dns(8, 8, 8, 8);
    IPAddress gateway(10, 1, 11, 65);
    IPAddress subnet(255, 255, 255, 192);
    Ethernet.begin((uint8_t*)mac, ip, dns, gateway, subnet);
  }
#endif
#if defined(DEBUG)
  init_eth2();
#endif
}
inline void init_i2c(){
  PRINTF("Инициализация шины I2C... ");
  Wire.begin(0);        //address
  Wire.onRequest(int1); //int1()  
  Wire.onReceive(int2); //int2()
  OK;
  //TODO поиск устройств (пинг)
}
inline void init2(){
  mas_s[i_s][0] = 1; //включился
  mas_s[i_s][1] = i4;
  mas_s[i_s][2] = i5;
  mas_s[i_s][3] = i6;
  mas_s[i_s][4] = free_ram()/16;
  mas_i[i_s++]  = 5; //len
}
inline void inits(){
#if defined(DEBUG)
  Serial.begin(9600);
  PRINTF("\n"SITE" v0.15 by <skip>");
#endif
  init_power();
  init_mem();
  //init_sd();//NO!
  init_eth();  
  init_i2c();//вызывать последним
  init2();
}
////////////////////////////////////////////////////////////////////////
inline void loop(){
  //delay(0xFFFF);//int = 2 bytes
  delay(100);//not touch!
  //отправим логи если есть
  while(i_s>0) {
    send(mas_s[--i_s],mas_i[i_s]);
  }
  if(is_update==1) {
    is_update=0;
    update1();
    update0();//обновим БД
  }  
}
////////////////////////////////////////////////////////////////////////
int main() {
  init(); //setup core arduino
  inits();
  for(;;) loop();
}
/*
Sketch uses 33 604 bytes (13%) of program storage space. Maximum is 258 048 bytes.
Global variables use 1 842 bytes (22%) of dynamic memory, leaving 6 342 bytes for local variables. Maximum is 8 192 bytes.
*/

/* 
  //TODO поиск устройств (пинг)
  //TODO чтение/запись файла
*/
