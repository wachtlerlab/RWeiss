import numpy as np
import serial
import time
import pygame
import csv
import os
from multiprocessing import Pool
import random

#Experiment settings
intensity = 1023
color = 'G'
startmin = 1     #[s], Zeit bis zum Start zwischen min/max
startmax = 1.5
time1 = .5       #[s], Zeit ohne Flicker
time2 = 1.7       #[s], Zeit in der der Flicker kommen kann (random)
time3 = .5       #[s], Zeit ohne Flicker
#Ablauf des Experiments: start -> time1 -> time2 (mit flicker) -> time3 -> wait for keyboard input
### LEFT: NEIN, RIGHT: JA

#Daten einlesen
exp_data = np.loadtxt("exp2.txt", delimiter=',')
exp_data = np.tile(exp_data, (10,1))
np.random.shuffle(exp_data)

#Port opening
port = serial.Serial('/dev/ttyACM0')
istring = 'I1\r'
off = 'X\r'
port.write('F10\r')
port.write('H200\r')
port.write('T500\r')
#port.write(off)
cstring = color + str(intensity) + '\r'
port.write('S\r')
#time.sleep(1)
#port.write(off)
port.write(cstring) #Color+Intensity an port
if color == 'G':
    port.write('R0\r')
    port.write('B0\r')
elif color == 'R':
    port.write('B0\r')
    port.write('G0\r')
elif color == 'B':
    port.write('R0\r')
    port.write('G0\r')
#port.write('X\r')

#Ablaufcheck
print exp_data
ablaufcheck = 1
while ablaufcheck:
    checkvar = raw_input("ok? [y/n]+Enter ")
    if checkvar != 'y':
        ablaufcheck = 1
        np.random.shuffle(exp_data)
        print exp_data
    else:
        ablaufcheck = 0
        
#Dateneingabe
name = raw_input("Testperson: ")
date = time.strftime("%c", time.localtime())

#Datenausgang
filename = '/home/student/Documents/robin/data/' + name + '_' + time.strftime("%d%m%y_%H%M") + '.csv'
exp_file = open(filename, "w")
writer = csv.writer(exp_file)
writer.writerow(['name', 'date', 'intensity', 'color', 't_start_interval', 'time1', 'time2', 'time3'])
writer.writerow([name, date, str(intensity), color, str(startmax-startmin), str(time1), str(time2), str(time3)])
writer.writerow(['Freq1', 'Freq2', 't_start', 't_flicker', 't_keypress', 'key_pressed', 'result'])
exp_file.close()
### Abspeichern ###
def exp_save():
    if l_pressed:
        key = 'n'
    if r_pressed:
        key = 'y'
    exp_file = open(filename, "a")
    writer = csv.writer(exp_file)
    writer.writerow([str(exp_data[i,0]), str(exp_data[i,1]), str(t_start), str(time1+t_flicker), str(exp_time), key, str(result)])
    exp_file.close()
    return 0;

#Durchlauf Ende
class nextloop(Exception): pass
def stop():
    #endtime = time.time()
    #exp_time = endtime - starttime
    exp_save()
    #port.write('X\r') #LED aus
    pygame.event.clear()
    raise nextloop()
    return;

#Pygame init
pygame.init()
screen = pygame.display.set_mode((2000,1500))
def beep(freq):
    os.system('play --no-show-progress --null --channels 1 synth %s sine %f' % ( .2, freq))
    return;
pool = Pool(4)

#Testablauf
for i in range(exp_data.shape[0]):
    try:
        starter = 0
        waittime = 0.2 + time.time()
        while time.time() < waittime:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    starter = 1
        freq1 = 'F' + str(exp_data[i,0]) + '\r'
        freq2 = 'H' + str(exp_data[i,1]) + '\r'
        t_flicker = random.randrange(int(10*time2))/10.
        tstring = 'T' + str(int((time1+t_flicker)*1000)) + '\r'
        port.write(freq1) #Frequenz1 an port
        port.write(freq2) #Frequenz2 an port
        port.write(tstring) #t_flicker an port
        timeout2 = time2 - t_flicker
        result = 0
        r_pressed = 0
        l_pressed = 0
        print 'press a key to start...'
        while starter == 0:  #Wartet bis Testperson bereit fuer naechsten Durchlauf
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    starter = 1
        t_start = random.randrange(int(10*startmin), int(10*startmax))/10.
        time.sleep(t_start)
        #print '\a' #beep
        port.write('S\r') #port start
        beeptime_a = time.time()
        #os.system('play --no-show-progress --null --channels 1 synth %s sine %f' % ( .2, 500))
        beep1 = pool.apply_async(beep, (500, ))
        starttime = time.time()
        #timeout = beeptime_a + time1 + t_flicker + timeout2 + time3
        timeout = starttime + time1 + t_flicker + timeout2 + time3
        while time.time() < timeout:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        l_pressed = 1
                        result = 0
                        if exp_data[i,0] == exp_data[i,1]:
                            result = 1
                        endtime = time.time()
                        exp_time = endtime - starttime
                        stop()
                    if event.key == pygame.K_RIGHT:
                        r_pressed = 1
                        result = 0
                        if exp_data[i,0] != exp_data[i,1]:
                            result = 1
                        endtime = time.time()
                        exp_time = endtime - starttime
                        stop()
        #port.write('X\r') #LED aus
        #print '\a' #beep
        #os.system('play --no-show-progress --null --channels 1 synth %s sine %f' % ( .2, 400))
        beep2 = pool.apply_async(beep, (400, ))
        while starter == 1:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        l_pressed = 1
                        result = 0
                        if exp_data[i,0] == exp_data[i,1]:
                            result = 1
                        exp_time = time.time() - starttime
                        exp_save()
                        pygame.event.clear()
                        starter = 0
                    if event.key == pygame.K_RIGHT:
                        r_pressed = 1
                        result = 0
                        if exp_data[i,0] != exp_data[i,1]:
                            result = 1
                        endtime = time.time()
                        exp_time = endtime - starttime
                        exp_save()
                        pygame.event.clear()
                        starter = 0
    except KeyboardInterrupt:
        pool.terminate()
    except nextloop:
        continue

pygame.quit()
