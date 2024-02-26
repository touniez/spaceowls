#include "MatrixCascade.h"
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
int comma_index, colon_index, question_index, excl_index, prev_colon;
int x1, y1;
int x2, y2;
int bruh;
int lightArray[32][8];

// This time we have more than one device.


// pin 11 is connected to the DataIn
// pin 13 is connected to the CLK
// pin 10 is connected to LOAD (cs)
const uint8_t CascadeSize = 4;
MatrixCascade<CascadeSize> cascade(11, 13, 10);

unsigned long delaytime = 30;

void setup()
{
  Serial.begin(115200);
  
  Serial.setTimeout(500);

  // Set the brightness. (0..15)
  cascade.setIntensity(15);
  for(int i = 0; i<=31; i+=2){
    setPixelOn(i,0);
          }
  mode = String('standby');

  
}

void loop() {
  
   Serial.println(Serial.available());
   input = Serial.readStringUntil('\r');
   //Serial.print(input);
   memset(lightArray,0,sizeof(lightArray));

   if(input.indexOf(',') != -1){
      //cascade.clear();
      comma_index = input.indexOf(',');
      colon_index = input.indexOf(':');
      question_index = input.indexOf('?');
      excl_index = input.indexOf('!');
      prev_colon = 0;
      while(colon_index != -1){
          
          x1 = input.substring(prev_colon, comma_index).toInt();
          x2 = input.substring(comma_index + 1,question_index).toInt();
          y1 = input.substring(question_index + 1,excl_index).toInt();
          y2 = input.substring(excl_index + 1,colon_index).toInt();
          int minX = min(x1,x2);
          int maxX = max(x1,x2);
          int minY = min(y1,y2);
          int maxY = max(y1,y2);
          Serial.println(String(x1)+" "+String(x2)+" "+String(y1)+" "+String(y2));
          maxX = min(31,maxX);
          minY = max(1,minY);
          maxY = min(7, maxY);
          for(int i = minX; i<=maxX; i++){
            for(int j = minY; j<=maxY; j++){
              lightArray[i][j] = 1; 
            }
          }
          Serial.flush();
          // setBlockOn(minX, maxX, 0, 7);
          prev_colon = colon_index + 1;
          colon_index = input.indexOf(':',prev_colon);
          comma_index = input.indexOf(',',prev_colon);
          question_index = input.indexOf('?',prev_colon);
          excl_index = input.indexOf('!',prev_colon);
      }

//      x1 = input.substring(prev_colon, comma_index).toInt();
//      x2 = input.substring(comma_index + 1).toInt();
//      y1 = input.substring(question_index + 1,excl_index).toInt();
//      y2 = input.substring(excl_index + 1,colon_index).toInt();
//      int minX = min(x1,x2);
//      int maxX = max(x1,x2);
//      int minY = min(y1,y2);
//      int maxY = max(y1,y2);
//      maxX = min(31,maxX);
//      maxY = min(7, maxY);
//      minY = max(1,minY);
//      //Serial.println(x2);
      Serial.flush();
//
//      for(int i = minX; i<=maxX; i++){
//          for(int j = minY; j<=maxY; j++){
//              lightArray[i][j] = 1; 
//            }
//          }
          
      // setBlockOn(x1, x2, 0, 7);
     
   }
   for(int i = 0; i<=31; i++){
          for(int j = 1; j<=7; j++){
              if(lightArray[i][j] == 1){
                setPixelOn(i,j); 
              }
              else{
                setPixelOff(i,j);
              }
            }
          }
   
   
  
}  /*if(mode == 'standby'){
    reset();
    giveD();
    delay(100); 
  }*/

  /*if(mode == 'active'){
    
  }*/



void setPixelOn(int x, int y)
{
  // x is between 0 and 32, y is between 0 and 7
  if (x <= 7){
    if (y == 7){
      cascade[0].set(7-x,0,true);
    }
    else{
      cascade[0].set(7-x,y+1,true);
    }

  }  

  else if (x <= 15){
    if (y == 7){
      cascade[1].set(7-(x-8),0,true);
    }
    else{
      cascade[1].set(7-(x-8),y+1,true);
    }
         
  }

  else if (x <= 23){
    if (y == 7){
      cascade[2].set(7-(x-16),0,true);
    }
    else{
      cascade[2].set(7-(x-16),y+1,true);
    }
   
  }

  else if (x <= 31){
    if (y == 7){
      cascade[3].set(7-(x-24),0,true);
    }
    else{
      cascade[3].set(7-(x-24),y+1,true);
    }
   
  }
 
}

void setBlockOn(int x1, int x2, int y1, int y2)
{
      for(int x = x1; x<=x2; x++){
        for(int y = y1; y<=y2; y++){
          setPixelOn(x,y);
        }
      }
}

void setPixelOff(int x, int y)
{
  // x is between 0 and 32, y is between 0 and 7
  if (x <= 7){
    if (y == 7){
      cascade[0].set(7-x,0,false);
    }
    else{
      cascade[0].set(7-x,y+1,false);
    }

  }  

  else if (x <= 15){
    if (y == 7){
      cascade[1].set(7-(x-8),0,false);
    }
    else{
      cascade[1].set(7-(x-8),y+1,false);
    }
         
  }

  else if (x <= 23){
    if (y == 7){
      cascade[2].set(7-(x-16),0,false);
    }
    else{
      cascade[2].set(7-(x-16),y+1,false);
    }
   
  }

  else if (x <= 31){
    if (y == 7){
      cascade[3].set(7-(x-24),0,false);
    }
    else{
      cascade[3].set(7-(x-24),y+1,false);
    }
   
  }
 
}

void setBlockOff(int x1, int x2, int y1, int y2)
{
      for(int x = x1; x<=x2; x++){
        for(int y = y1; y<=y2; y++){
          setPixelOff(x,y);
        }
      }
}
