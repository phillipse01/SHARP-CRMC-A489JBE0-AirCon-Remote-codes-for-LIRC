# SHARP-CRMC-A489JBE0-AirCon-Remote-codes-for-LIRC

This repository centers around the SHARP CRMC-A489JBE0 airconditioner remote and integrating it with LIRC. 

These scripts create raw lirc codes and decode mode2 input from the remote. I also didnt bother with any of the timing functionality - see below.

## encode.py
Given parameters, generate raw codes that can be put into LIRC configuration files. (you can also irrecord -a the final file to make it non-raw)

Example usage:
```
python3 encode.py --mode 1 --temp 26 --power 2 --swing
```

## decode.py
Decodes output of mode2 to binary to help decipher the remote codes. Example usage:
```
mode2 --driver default --device /dev/lirc-rx | python3 -u ./decode.py
```
Output resembles:
```
0 000 111 101 101 110 111 011 111 111 110 1*
0 001 000 010 010 001 000 100 000 000 001 0|
0 000 111 101 101 110 111 011 111 111 110 1* 
```
(above example - heat off 26 degrees)

## Decoded IR codes explination

SHARP CRMC-A489JBE0

mode2 output key  
gap (pulse) = 435  
short (space) = 1620  
long (space) = 3700  
margin (space) = 150  

seperator (space) = 20000

IR codes are encoded into space length - short 0 long 1


Here is the typical output of the AC remote (turn on to mode:fan speed slow):

```
A   B  C   D    E F   G H   I     J    K   L  
000 01 111 1110 1 011 1 110 11111 1111 110 *  
000 10 000 0001 0 100 0 001 00000 0000 001 |  
000 01 111 1110 1 011 1 110 11111 1111 110 *  

000 01 111 1101 1 011 1 110 11111 1111 110 |  
000 10 000 0010 0 100 0 001 00000 0000 001 |  
000 01 111 1101 1 011 1 110 11111 1111 110 |  
```

Each line is the same, used to verify transmission the second line is XOR'd of the first and last.  
For the sake of simplicity, I focus on the first (and also last) lines.  
I also didnt bother with the timer of the remote, so there are a few "unknowns"  

I also split up one time commands from codes.  
* Commands are sent only depending what button is pushed  
* Codes are sent for every key push  


Each section broken down

A:  
* Buffer - start space 000

B:  
* Unkown - always 01

C:  
* Temp Auto / dehumidifier code
* 101 = highest
* 110 = higher
* 111 = normal (for other modes)
* 010 = lower
* 001 = lowest
D:  
* Temp Val code (cool, heat)
* 1111 = Auto mode only
* 1110 = 18 (fan and dehumidifier modes)
* 1101 = 19
* 1100 = 20
* 1011 = 21
* 1010 = 22
* 1001 = 23
* 1000 = 24
* 0111 = 25
* 0110 = 26
* 0101 = 27
* 0100 = 28
* 0011 = 29
* 0010 = 30
* 0001 = 31
* 0000 = 32

E:  
* Unkown - always 1

F:  
* Mode code
* 111 = auto
* 110 = heat
* 101 = cool
* 100 = dehumidify
* 011 = fan

G:  
* Unkown - always 1

H:  
* Fan Speed code
* 010 = Fast
* 100 = Medium
* 110 = Slow
* 111 = Auto (not for fan mode)

I:  
* Unkwon - always 11111 - possibly timer

J:  
* Swing command (only works with update settings)
* 0001 = Change swing mode
* 1111 = do not change swing mode

K:  
* Power command
* 110 = Turn On
* 101 = Turn Off
* 100 = Update settings (stay on)

L:  
* Seperator - 20,000 ms space
