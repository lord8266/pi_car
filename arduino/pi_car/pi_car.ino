#define servo_pin1 9
#define servo_pin2 10
#include <Servo.h>
#define ma 5
#define mb 6
#define ma_1 7
#define ma_2 8
#define mb_1 11
#define mb_2 12

unsigned char buf[10];
unsigned char buf_sens[10];
int curr;
int servo_angle1;
int servo_angle2;
Servo servo1;
Servo servo2;

void setup(){
    pinMode(ma,OUTPUT);
    pinMode(ma_1,OUTPUT);
    pinMode(ma_2,OUTPUT);
    pinMode(mb,OUTPUT);
    pinMode(mb_1,OUTPUT);
    pinMode(mb_2,OUTPUT);
    digitalWrite(ma,HIGH);
    digitalWrite(mb,HIGH);
    buf[0] =2;
    buf[1] =2;
    servo_angle1 = 120;
    servo_angle2 = 110;
    servo1.attach(servo_pin1);
    servo2.attach(servo_pin2);

    curr = millis();
    Serial.begin(57600);
}
void update_buf(){
    if (Serial.available()>0){
        char a =Serial.read();
        if (a==0x00){
            Serial.readBytes(buf,4);
            servo_angle1=(buf[2]-1);
            servo_angle2=(buf[3]-1);
            servo_angle1 = max(0,min(servo_angle1,180));
            servo_angle2 = max(0,min(servo_angle2,180));
        }
    }
}
void update_sens(){
    buf_sens[0] =buf[0];
    buf_sens[1] = buf[1];
    buf_sens[2] =servo_angle1;
    buf_sens[3] = servo_angle2;
    buf_sens[4] = 100;
}
void update_motor(){
    if (buf_sens[0]==2){
        digitalWrite(ma_1,0);
        digitalWrite(ma_2,0);
    }
    else if (buf_sens[0]>2){
        digitalWrite(ma_1,0);
        digitalWrite(ma_2,1);
    }
    else{
        digitalWrite(ma_1,1);
        digitalWrite(ma_2,0);
    }
    if (buf_sens[1]==2){
        digitalWrite(mb_1,0);
        digitalWrite(mb_2,0);
    }
    else if (buf_sens[1]>2){
        digitalWrite(mb_1,1);
        digitalWrite(mb_2,0);
    }
    else{
        digitalWrite(mb_1,0);
        digitalWrite(mb_2,1);
    }
}
void loop(){
    analogWrite(ma,255);
    analogWrite(mb,255);
    update_buf();
    update_sens();

    servo1.write(servo_angle1);
    servo2.write(servo_angle2);
    update_motor();    

    if ((millis()-curr)>16) {
        curr =millis();
        Serial.write(0x00);
        Serial.write(buf_sens,5);
    }

}