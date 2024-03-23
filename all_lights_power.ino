#include "MatrixCascade.h"

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
  cascade.setIntensity(30);
  for(int i = 0; i<=30; i+=2){
    for(int j = 0; j <= 7; j+=1){
      setPixelOn(i,j);
      setPixelOn(i+1,j);
      delay(2000);
    }
  }
}

void loop() {
  // put your main code here, to run repeatedly:

}

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
