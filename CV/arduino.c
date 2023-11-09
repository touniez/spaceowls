#include <Adafruit_NeoPixel.h>
#ifdef __AVR__
  #include <avr/power.h>
#endif

uint8_t Data[34] = {0};
int sensitivity = 10; //number of averages for distance gathering
int deadzone = 340;
String mode;
String input = "";

#define PIN 6
int input1;
int input2;
int x1;
int x2;
int bruh;
Adafruit_NeoPixel strip = Adafruit_NeoPixel(256, PIN, NEO_GRB + NEO_KHZ800);

void setup()
{
  Serial.begin(115200);
  //Serial1.begin(115200);
   Serial.setTimeout(250);

  
  mode = String('standby');
  strip.begin();
  strip.setBrightness(100);
  reset(); // Initialize all pixels to 'off'
  
}

void loop() {
   Serial.println(Serial.available());
   input = Serial.readStringUntil('\r');
//   Serial.println(input);
//     Serial.print("R\n");
   

  /*if (input == 'standby'){
    reset();
    mode = 'standby';
    giveD();
  }
  */

  if(input.indexOf(',') != -1){
    reset();
//    strip.show();
    int commaIndex = input.indexOf(',');
    x1 = input.substring(0, commaIndex).toInt();
    x2 = input.substring(commaIndex + 1).toInt();
    Serial.flush();
    light_block(x1, x2);
    strip.show();
    

    
  }
  
  
  /*if(mode == 'standby'){
    reset();
    giveD();
    delay(100); 
  }*/

  /*if(mode == 'active'){
    
  }*/
}

void giveD() {
  
  readData(Data);
  int distance = readD(Data);
  int lb = deadzone - sensitivity;
  int ub = deadzone + sensitivity;
  if ((distance<lb)||(distance>ub)){
        Serial.print("go active\n");
        mode = 'active';
  }


}

int readD(uint8_t *buf)
{
  int d;
  char *p = strstr(buf, "Range Valid");
  /*if (p != 0) {
    d = atoi(&Data[25]);
    return d;
  } else {
    return -1;
  }*/
  d = atoi(&Data[25]);
  return d;
}

void readData(uint8_t *buf)
{
  bool flag = 0;
  uint8_t ch;
  while (!flag) {
    if (Serial1.available() == 0){
      //Serial.print(Serial1.available());
      flag = 1;
    }
    if (readN(&ch, 1) == 1) {
      //Serial.print(Serial1.available());
      if (ch == 'S') {
        Data[0] = ch;
        if (readN(&ch, 1) == 1) {
          if (ch == 't') {
            Data[1] = ch;
            if (readN(&ch, 1) == 1) {
              if (ch == 'a') {
                Data[2] = ch;
                readN(&Data[3],30);
                Data[31] == 'm';
                Data[32] == 'm';
                flag = 1;
              }
            }
          }
        }
      }
    }
  }
}
int readN(uint8_t *buf, size_t len)
{
  size_t offset = 0, left = len;
  long curr = millis();
  while (left) {
    if (Serial1.available()) {
      buf[offset++] = Serial1.read();
      left--;
    }
    if (millis() - curr > 500) {
      break;
    }
  }
  return offset;
}

void light_block(int x1, int x2) {
    int big = max(x1,x2);
    int lil = min(x1,x2);
    for(int i = lil; i <= big; i++){
      for(int j = 0; j <= 7; j++){
        lightColor2D(i, j);
        }
      }
    
}

void reset(){
  for (int i = 0; i<=31; i++){
    for (int j = 0; j<=7; j++){
      darken(i,j);
    }
  }
}


void lightColor2D(int input1, int input2) {
    if (input1 % 2 == 0) {
      bruh = (7 * (input1 + 1) + input1) - input2;
    }
    else
    {
      bruh = (8 * input1) + input2;
    }
    strip.setPixelColor(bruh, strip.Color(255, 0, 0));
}

void darken(int input1, int input2) {
    if (input1 % 2 == 0) {
      bruh = (7 * (input1 + 1) + input1) - input2;
    }
    else
    {
      bruh = (8 * input1) + input2;
    }
    strip.setPixelColor(bruh, strip.Color(0, 0, 0));
}
