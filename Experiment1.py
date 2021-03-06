import numpy as np
import serial
import time
import pygame
import csv
import random

#Experiment settings
intensity = 254
color = 'G'
startmin = .5     #[s], Zeit bis zum Start in min/max
startmax = 1
time1 = .3       #[s], Zeit ohne Flicker
time2 = 1.7       #[s], Zeit in der der Flicker kommen kann (random)
time3 = .3       #[s], Zeit ohne Flicker
#Ablauf des Experiments: start -> time1 -> time2 (mit flicker) -> time3 -> wait for keyboard input
### LEFT: JA, RIGHT: NEIN

#Daten einlesen
exp_data = np.loadtxt("exp1.txt", delimiter=',')
np.random.shuffle(exp_data)
if exp_data[0,0] == exp_data[0,1]:
    np.random.shuffle(exp_data)
else: pass

#Ablaufcheck
print exp_data
ablaufcheck = 1
while ablaufcheck:
    checkvar = raw_input("ok? [y/n]+Enter ")
    if checkvar != 'y':
        ablaufcheck = 1
        np.random.shuffle(exp_data)
        if exp_data[0,0] == exp_data[0,1]:
            np.random.shuffle(exp_data)
        else: pass
        print exp_data
    else:
        ablaufcheck = 0
        
#Dateneingabe
name = raw_input("Testperson: ")
date = time.strftime("%c", time.localtime())
istring = 'I1\r'
ioff = color + '0\r'
cstring = color + str(intensity) + '\r'

#Datenausgang
filename = name + '.csv'
exp_file = open(filename, "w")
writer = csv.writer(exp_file)
writer.writerow(['name', 'date', 'intensity', 'color', 't_start_interval', 'time1', 'time2', 'time3'])
writer.writerow([name, date, str(intensity), color, str(startmax-startmin), str(time1), str(time2), str(time3)])
writer.writerow(['Freq1', 'Freq2', 't_start', 't_flicker', 't_keypress', 'key_pressed', 'result'])
exp_file.close()
### Abspeichern ###
def exp_save():
    if l_pressed:
        key = 'y'
    if r_pressed:
        key = 'n'
    exp_file = open(filename, "a")
    writer = csv.writer(exp_file)
    writer.writerow([str(exp_data[i,0]), str(exp_data[i,1]), str(t_start), str(time1+t_flicker), str(exp_time), key, str(result)])
    exp_file.close()
    return 0;

#Port opening
port = serial.Serial('/dev/ttyACM0')
port.write('R0\r')
port.write('G0\r')
port.write('B0\r')

#Durchlauf Ende
class nextloop(Exception): pass
def stop():
    #endtime = time.time()
    #exp_time = endtime - starttime
    exp_save()
    port.write(ioff) #LED aus
    pygame.event.clear()
    raise nextloop()
    return;

#Pygame init
pygame.init()
screen = pygame.display.set_mode((10,10))

#Testablauf
for i in range(exp_data.shape[0]):
    try:
        print 'press a key to start...'
        starter = 0
        result = 0
        r_pressed = 0
        l_pressed = 0
        while starter == 0:  #Wartet bis Testperson bereit fuer naechsten Durchlauf
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    starter = 1
        t_start = random.randrange(int(10*startmin), int(10*startmax))/10.
        time.sleep(t_start)
        freq1 = 'F' + str(exp_data[i,0]) + '\r'
	#freq1 = 'F20\r'
        port.write(freq1) #Freq1 an port
        port.write(cstring) #LED an
        print '\a'
        starttime = time.time()
        ### ABSCHNITT 1 ###
        timeout1 = time.time() + time1
        while time.time() < timeout1:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        l_pressed = 1
                        endtime = time.time()
                        exp_time = endtime - starttime
                        stop()
                    if event.key == pygame.K_RIGHT:
                        r_pressed = 1
                        endtime = time.time()
                        exp_time = endtime - starttime
                        stop()
        ### ABSCHNITT 2 ###
        t_flicker = random.randrange(int(10*time2))/10.
        timeout2 = time.time() + t_flicker
        while time.time() < timeout2:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        l_pressed = 1
                        endtime = time.time()
                        exp_time = endtime - starttime
                        stop()
                    if event.key == pygame.K_RIGHT:
                        r_pressed = 1
                        endtime = time.time()
                        exp_time = endtime - starttime
                        stop()
        timeout2a = time.time() + (1.7 - t_flicker)
        freq2 = 'F' + str(exp_data[i,1]) + '\r'
	#freq2 = 'F40\r'
        port.write(freq2) #Freq2 an port
        while time.time() < timeout2a:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        l_pressed = 1
                        if freq1 != freq2:
                            result = 1
                        endtime = time.time()
                        exp_time = endtime - starttime
                        stop()
                    if event.key == pygame.K_RIGHT:
                        r_pressed = 1
                        if freq1 == freq2:
                            result = 1
                        endtime = time.time()
                        exp_time = endtime - starttime
                        stop()
        ###ABSCHNITT 3 ###
        timeout3 = time.time() + time3
        while time.time() < timeout3:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        l_pressed = 1
                        if freq1 != freq2:
                            result = 1
                        endtime = time.time()
                        exp_time = endtime - starttime
                        stop()
                    if event.key == pygame.K_RIGHT:
                        r_pressed = 1
                        if freq1 == freq2:
                            result = 1
                        endtime = time.time()
                        exp_time = endtime - starttime
                        stop()
        port.write(ioff) #LED aus
        print '\a'
        while starter == 1:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        l_pressed = 1
                        if freq1 != freq2:
                            result = 1
                        exp_time = time.time() - starttime
                        exp_save()
                        pygame.event.clear()
                        starter = 0
                    if event.key == pygame.K_RIGHT:
                        r_pressed = 1
                        if freq1 == freq2:
                            result = 1
                        endtime = time.time()
                        exp_time = endtime - starttime
                        exp_save()
                        pygame.event.clear()
                        starter = 0
    except nextloop:
        continue

pygame.quit()
