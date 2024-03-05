#include "MatrixCascade.h"

String input = "";

//For string parsing
int comma_index, colon_index, question_index, excl_index, prev_colon, dash_index;
//Describe box location
int x1, x2, y1, y2;
int lightArray[32][8];

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
}

void loop()
{  
   //Serial.println(Serial.available());
   input = Serial.readStringUntil('\r');
   memset(lightArray,0,sizeof(lightArray));

   if(input.indexOf(',') != -1){
      //Initialize parsing variables
      comma_index = input.indexOf(',');
      colon_index = input.indexOf(':');
      question_index = input.indexOf('?');
      excl_index = input.indexOf('!');
      dash_index = input.indexOf('/');
      prev_colon = 0;

      //Loop through all sets of coordinates
      while(colon_index != -1 && colon_index < dash_index){         
          x1 = input.substring(prev_colon, comma_index).toInt();
          x2 = input.substring(comma_index + 1,question_index).toInt();
          y1 = input.substring(question_index + 1,excl_index).toInt();
          y2 = input.substring(excl_index + 1,colon_index).toInt();
          //Set mins and maxes for for loop
          int minX = min(x1,x2);
          int maxX = max(x1,x2);
          int minY = min(y1,y2);
          int maxY = max(y1,y2);
          minX = max(0, minX); //Catches weird bug where min x is like -24500
          maxX = min(31,maxX);  //Max possible x is 31, this statement needed bc pi sometimes sends 32
          minY = max(1,minY);   //Min possible y is 1(top row 0 always lit), this statement needed bc pi sometimes sends 0
          maxY = min(7, maxY);  //Max possible y is 7, this statement needed bc pi sometimes sends 8
          //Assign values to light array
          for(int i = minX; i<=maxX; i++){
            for(int j = minY; j<=maxY; j++){
              lightArray[i][j] = 1; 
            }
          }
          Serial.flush(); 
          //Update parsing variables
          prev_colon = colon_index + 1;
          colon_index = input.indexOf(':',prev_colon);
          comma_index = input.indexOf(',',prev_colon);
          question_index = input.indexOf('?',prev_colon);
          excl_index = input.indexOf('!',prev_colon);
      }
      prev_colon += 1; // Increment prev colon to skip the "/"
      while(colon_index != -1){         
          x1 = input.substring(prev_colon, comma_index).toInt();
          x2 = input.substring(comma_index + 1,question_index).toInt();
          y1 = input.substring(question_index + 1,excl_index).toInt();
          y2 = input.substring(excl_index + 1,colon_index).toInt();
          //Set mins and maxes for for loop
          int minX = min(x1,x2);
          int maxX = max(x1,x2);
          int minY = min(y1,y2);
          int maxY = max(y1,y2);
          minX = max(0, minX); //Catches weird bug where min x is like -24500
          maxX = min(31,maxX);  //Max possible x is 31, this statement needed bc pi sometimes sends 32
          minY = max(1,minY);   //Min possible y is 1(top row 0 always lit), this statement needed bc pi sometimes sends 0
          maxY = min(7, maxY);  //Max possible y is 7, this statement needed bc pi sometimes sends 8
          //Assign values to light array
          for(int i = minX; i<=maxX; i++){
            for(int j = minY; j<=maxY; j++){
              lightArray[i][j] = 0; 
            }
          }
          Serial.flush(); 
          //Update parsing variables
          prev_colon = colon_index + 1;
          colon_index = input.indexOf(':',prev_colon);
          comma_index = input.indexOf(',',prev_colon);
          question_index = input.indexOf('?',prev_colon);
          excl_index = input.indexOf('!',prev_colon);
        }
   }
   //Turn the lights on based on lighArray values
   for(int i = 0; i<=31; i++){
          for(int j = 1; j<=7; j++){
              if(lightArray[i][j] == 1){
                setPixelOn(i,j); 
              }
              else setPixelOff(i,j);
            }
    }        
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
