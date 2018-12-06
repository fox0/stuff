#include <Arduino.h>

class Buffer {
private:
  byte* arr;
  long i;  
public:
  Buffer(long kol) {
    arr = new byte[kol];
    i = 0;
  }
  ~Buffer() {
    delete []arr; 
  }
  char* get(){
    arr[i] = '\0';
    return (char*)arr; 
  }
  char get(long index){
    return arr[index]; 
  }
  long len(){
    return i; 
  }
  void clear(){
    i = 0;
  }
  void print(char c){
    arr[i++] = c;
  }
  void println() {
    print('\r');
    print('\n');
  }
  void println(char* c) {
    print(c);
    println();
  }
  void print(const __FlashStringHelper* str){
    strcpy_P((char*)(arr+i), (const char*)str);
    i += strlen_P((const char*)str);
  }
  void print(char* c) {
    int j=0;
    while(c[j]){
      print(c[j++]);
    } 
  }
  void println(const __FlashStringHelper* str){
    print(str);
    println();
  }
  void println(char c) {
    print(c);
    println();
  }
  void print(int n) {
    char buf[8 * sizeof(int) + 1]; // Assumes 8-bit chars plus zero byte.
    char *str = &buf[sizeof(buf) - 1];
    *str = '\0'; 
    do {
      int m = n;
      n /= 10;
      char c = m - 10*n;
      *--str = c < 10 ? c+'0' : c+'A'-10;
    } while(n);
    print(str);
  }
  void print(byte b) {
    print((int)b); 
  }
  void println(byte b) {
    print(b);
    println();
  }     
};
