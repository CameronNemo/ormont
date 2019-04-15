#!/usr/bin/env python3

from netmiko import Netmiko, SSHDetect
from getpass import getpass
import logging
import socket
import sys
import or_device

# # Logging for netmiko session
# logging.basicConfig(filename='test.log', level=logging.DEBUG)
# logger = logging.getLogger("netmiko")

def mainMenu():
    selection = input('\n\nSelect the type of Ops readiness to be performed:\n1) CLR\n2) Device\n3) Quit\n\n>> ')
    if selection == '1':
        print('\nUnder construction')
        mainMenu()
    elif selection == '2':
        or_device.or_device()
        mainMenu()
    elif selection == '3':
        sys.exit()
    else:
        print('\nSelection not recognized, please enter the digit exactly')
        mainMenu()

mainMenu()
