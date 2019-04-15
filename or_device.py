from netmiko import Netmiko, SSHDetect
from getpass import getpass
import logging
import socket
import sys, subprocess

def or_device():
    # Initialize device dictionary
    device = {
    'device_type': 'autodetect',
    'host': socket.gethostbyname(input('Host: ')),
    'username': input('Username: '),
    'password': getpass()
    }
    
    # Domain <> IP translation in order to use both for output later
    fqdm = socket.gethostbyaddr(device['host'])
    ip = socket.gethostbyname(device['host'])
    
    # Detects type of device via one-time SSH login
    def DeviceDetector(device_in):
        print('Detecting device type...')
        guesser = SSHDetect(**device_in)
        best_match = guesser.autodetect()
        if best_match == None: # <--------- This is cheating but ok for now
            best_match = 'cisco_xr' 
        device['password'] = getpass(prompt='Re-enter password for MFA reasons: ')
        print('Device type - ' + best_match)
        return best_match
    
    # Assigns detected device type to above dictionary
    device['device_type'] = DeviceDetector(device)
    
    print('-'*50 + '\nConnecting to {} ({})'.format(fqdm[0], ip))
    connection = Netmiko(**device)
    print('Connected\n' + '-'*50)
    print(connection.find_prompt())
    
    
    # New variable to copy over the device type from the device dictionary
    device_type = device['device_type']
    
    if device_type == 'cisco_ios':
        print("This is an IOS device")
        output = '*'*100 + '\n>> show uptime\n' + '*'*100 + '\n'
        output += connection.send_command('show version | i upt' + '\n')
        output += '\n' * 5 + '*'*100 + "\n>> show platform\n" + '*'*100 + '\n'
        output += connection.send_command('show platform')
        output += '\n' * 5 + '*'*100 + '\n>> show facility status minor\n' + '*'*100 + '\n'
        output += connection.send_command('show facility status minor')
        output += '\n' * 5 + '*'*100 + '\n>> show environment\n' + '*'*100 + '\n'
        output += connection.send_command('show environment')
        print(output)
        filename = 'device_or_' + fqdm[0]
        file = open(filename,'w')
        file.write(output)
        file.close()
        subprocess.call(['open', '-a', 'TextEdit', filename])
    elif device_type == 'cisco_xr':
        print('This is an XR device')
        output = '*'*100 + '\n>> show uptime\n' + '*'*100 + '\n'
        output += connection.send_command('show version | i upt' + '\n')
        output += '\n' * 5 + '*'*100 + "\n>> show platform\n" + '*'*100 + '\n'
        output += connection.send_command('show platform')
        output += '\n' * 5 + '*'*100 + '\n>> show hw-module fpd location all\n' + '*'*100 + '\n'
        output += connection.send_command('show hw-module fpd location all')
        output += '\n' * 5 + '*'*100 + '\n>> show environment\n' + '*'*100 + '\n'
        output += connection.send_command('show environment')
        print(output)
        filename = 'device_or_' + fqdm[0]
        file = open(filename,'w')
        file.write(output)
        file.close()
        subprocess.call(['open', '-a', 'TextEdit', filename])
    elif device_type == 'juniper_junos':
        print('This is a Juniper')
        output = '*'*100 + '\n>> show chassis routing-engine\n' + '*'*100 + '\n'
        output += connection.send_command('show chassis routing-engine')
        output += '\n' * 5 + '*'*100 + "\n>> show chassis environment\n" + '*'*100 + '\n'
        output += connection.send_command('show chassis environment')
        output += '\n' * 5 + '*'*100 + '\n>> show system alarms\n' + '*'*100 + '\n'
        output += connection.send_command('show system alarms')
        output += '\n' * 5 + '*'*100 + '\n>> show chassis fpc pic-status\n' + '*'*100 + '\n'
        output += connection.send_command('show chassis fpc pic-status')
        print(output)
        filename = 'device_or_' + fqdm[0]
        file = open(filename,'w')
        file.write(output)
        file.close()
        subprocess.call(['open', '-a', 'TextEdit', filename])
    else:
        print("Unknown device - " + device_type)


    connection.disconnect()
    print('-'*50 + '\nDisconnected from  {} ({})'.format(fqdm[0], ip) + '\n' + '-'*50)


