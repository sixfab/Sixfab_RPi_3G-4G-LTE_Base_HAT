#!/usr/bin/env python3

###
### TODO: Description about the script
###
###

#imports
from time import sleep
import serial

AT_PORT = "/dev/ttyUSB2"
NMEA_PORT = "/dev/ttyUSB1"
BAUD_RATE = 115200

at_ser = serial.Serial(AT_PORT,BAUD_RATE)
nmea_ser = serial.Serial(NMEA_PORT,BAUD_RATE)


def send_command(command):
    command = command + "\r\n"
    at_ser.write(command.encode())
    sleep(0.2) 

def turn_on_gps():
    if not at_ser.is_open:
        at_ser.open()
    else: 
        pass
    
    if at_ser.is_open:
        send_command("AT$GPSP=1")
        send_command("AT$GPSNMUN=2,0,0,0,0,1,0") # 2 activates unsolicited streaming 
        # Format: AT$GPSNMUM=<enable>,<GGA>,<GLL>,<GSA>,<GSV>,<RMC>,<VTG>    
        at_ser.close()

def turn_off_gps():
    if not at_ser.is_open:
        at_ser.open()
    else: 
        pass
    if at_ser.is_open:
        print("turning OFF GPS")
        send_command("AT$GPSP=0")
        at_ser.close()

def read_nmea():
    if not nmea_ser.is_open:
        nmea_ser.open()
    else:
        pass
    sleep(0.1)
    if nmea_ser.is_open:
        return nmea_ser.readline().decode('utf-8')
    
def parse_rmc(data):
    ##  Format: 
    ##  $GPRMC,hhmmss.ss,A,llll.ll,a,yyyyy.yy,a,x.x,x.x,ddmmyy,x.x,a*hh
    ##  Check for RMC details: http://aprs.gids.nl/nmea/#rmc 

    #print(data, end='') #prints raw data 
    sdata = data.split(',')
    if sdata[0] != "$GPRMC":
        print("NMEA Sentence is not RMC")
    else:
        if sdata[2] == 'V':
            print("No NMEA Data Available, Wait 5 sec before next try")
            sleep(5)
        else: #if sdata[2] == 'A':
            time = sdata[1][0:2] + ":" + sdata[1][2:4] + ":" + sdata[1][4:6] #  time hh:mm:ss
            validity = sdata[2]
            lat = pos_decode(sdata[3])          #latitude
            dir_lat = sdata[4]      #latitude direction N/S
            lon = pos_decode(sdata[5])          #longitute
            dir_lon = sdata[6]      #longitude direction E/W
            speed = sdata[7]        #Speed in knots
            tr_course = sdata[8]    #True course
            date = sdata[9][0:2] + "/" + sdata[9][2:4] + "/" + sdata[9][4:6] #date
            variation = sdata[10]   #variation
            checksum_dir = sdata[13].split('*')[0]
            checksum = sdata[13].split('*')[1]

            print('Time ' + time)
            print('Latitude ' + lat)
            print('Latitude Direction ' + dir_lat)
            print('Longitude ' + lon)
            print('Longitude Direction ' + dir_lon)
            print('Date: ' + date)       

def pos_decode(coord):
    #Converts DDMM.MMMMM -> DD deg MM.MMMMM min
    x = coord.split(".")
    DD = x[0][0:-2] #DD 
    MM = x[0][-2:]+'.' + x[1] # MM.MMMM

    return str(float(DD) + float(MM)/60)
    # returns DD.SSSSS 

def main():
    print("Turning on GPS")
    turn_on_gps()
    sleep(2)
    while True:
        parse_rmc(read_nmea())
        
        

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(e)
    finally: 
        turn_off_gps()
        if nmea_ser.is_open:
            nmea_ser.close()