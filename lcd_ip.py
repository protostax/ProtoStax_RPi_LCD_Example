# ***************************************************
#   ProtoStax Raspberry Pi LCD Example 
#   using Raspberry Pi B+, ProtoStax Enclosure for Raspberry Pi B+/4B, ProtoStax LCD Kit V2
#   --> https://www.protostax.com/collections/all/products/protostax-for-raspberry-pi-b
#   --> https://www.protostax.com/collections/all/products/protostax-lcd-kit-v2
#
#   Use a 16x2 Character I2C LCD w/ your Raspberry Pi & ProtoStax Enclosure to
#   display information like IP address, date/time & much more!
#
#   This displays the Date and Time on the first line, and the second line of
#   the 16x2 display shows the IP address and hostname of the Raspberry Pi
#   in a scrolling fashion (to accommodate the character count being longer than 16 characters)
#
#   Written by Sridhar Rajagopal for ProtoStax.
#
#
#   BSD license. All text above must be included in any redistribution


#   LCD Text Scrolling based on blog post by Danilo Bargen, the creator of the RPLCD library used
#   in this example
#   See - https://blog.dbrgn.ch/2014/4/20/scrolling-text-with-rplcd/


import socket
import logging
import signal

from time import sleep
from datetime import datetime
from RPLCD.i2c import CharLCD

lcd = CharLCD('PCF8574', 0x27, port=1, auto_linebreaks=False)
lcd.clear()

# Function to get the ip address and hostname
# of the Raspberry Pi, if it exists
# If the interface is down, it returns an empty string tuple
# Otherwise, it returns a tuple of (ip_adress, hostname)
def get_ip_address_and_hostname():
 ip_address = '';
 hostname = '';
 try:
     s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
     s.connect(("8.8.8.8",80))
     ip_address = s.getsockname()[0]
     hostname = socket.gethostname()
 except:
     ip_address = ''
     hostname = ''
 finally: 
     s.close()
 return ip_address, hostname

# Used for LCD text scrolling
framebuffer = [
    '',
    '',
]

# Function to write the specified number of columns to the LCD screen
# from the frame buffer
def write_to_lcd(lcd, framebuffer, num_cols):
    """Write the framebuffer out to the specified LCD."""
    lcd.home()
    for row in framebuffer:
        lcd.write_string(row.ljust(num_cols)[:num_cols])
        lcd.write_string('\r\n')

# Function to loop the given string row on the LCD screen with the
# specified time delay
def loop_string(string, lcd, framebuffer, row, num_cols, delay=0.2):
    padding = ' ' * num_cols
    s = padding + string + padding
    for i in range(len(s) - num_cols + 1):
        framebuffer[row] = s[i:i+num_cols]
        write_to_lcd(lcd, framebuffer, num_cols)
        sleep(delay)

# Function to handle received signals (such as SIGTERM on shutdown)
# It clears the LCD screen and turns off the backlight
def receiveSignal(signalNumber, frame):
    logging.info("Stopping LCD IP service")
    lcd.clear()
    lcd.backlight_enabled = False
    raise SystemExit('Exiting')

# The "main" function. It wakes up every 10 seconds, gets the
# latest date/time and ip address/hostname, and displays those
# on the LCD screen. It also handles any keyboard interrupts
# by doing cleanup - clear the LCD screen and turn off the backlight
def main():
    global framebuffer
    try:
        while True:
            lcd_line_1 = datetime.now().strftime('%b %d  %H:%M:%S')
            ip_address, hostname = get_ip_address_and_hostname()
            lcd_line_2 = "IP: " + ip_address + ", " + hostname
            lcd.clear()
            print(f'{lcd_line_1}\r\n{lcd_line_2}')
            # lcd.write_string(lcd_line_1)
            framebuffer[0] = lcd_line_1
            loop_string(lcd_line_2,lcd,framebuffer,1,16)
            lcd.home()
            sleep(10)
    except KeyboardInterrupt:  
        logging.info("Stopping LCD IP service")
        lcd.clear()
        lcd.backlight_enabled = False 

if __name__ == '__main__':
    signal.signal(signal.SIGTERM, receiveSignal)
    main()
