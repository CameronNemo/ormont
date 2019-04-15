import ipaddress
from netmiko import Netmiko, SSHDetect
from getpass import getpass
import logging
import socket
import sys, subprocess
from ciscoconfparse import CiscoConfParse
import datetime

# Record IP that will start the process
seed_ip = input('Enter one of the point to point IPs on the circuit: ')

# Enter user IP into ipaddress module as an 'interface', assumed a /31 ptp subnet
ip1_interface = ipaddress.ip_interface(seed_ip + '/31')

# Find subnet, define variable
subnet = ip1_interface.network

ip1 = subnet[0]
ip2 = subnet[1]

username = input('Backdoor username: ')
password = getpass('Backdoor password: ')

# Device counter that will be used in the for loop
x = 1

for ip in subnet.hosts():


    # Initializes device dictionary
    device = {
    'device_type': 'autodetect',
    'host': str(ip),
    'username': username,
    'password': password,
    'verbose': True
    }
    
    # Domain <> IP translation in order to use both for output later
    fqdm = socket.gethostbyaddr(str(ip))
    ip_add = socket.gethostbyname(str(ip))
    
    # Detects type of device via one-time SSH login
    def DeviceDetector(device_in):
        print('\n\n\n\nDetecting device type for device {}...'.format(x))
        guesser = SSHDetect(**device_in)
        best_match = guesser.autodetect()
        if best_match == None: # <--------- This is cheating but ok for now
            best_match = 'cisco_xr'
        print('Device type - ' + best_match)
        return best_match
    
    # Assigns detected device type to above dictionary
    device['device_type'] = DeviceDetector(device)
    print('-'*50 + '\nConnecting to {} ({})'.format(fqdm[0], ip))
    
    # Connects to the device
    connection = Netmiko(**device)
    print('Connected\n' + '-'*50)
   

    # New variable to copy over the device type from the device dictionary
    device_type = device['device_type']
   
    if device_type == 'cisco_ios':
        print("This is an IOS device")
        

        # Start output variable to store results in
        output = str(datetime.datetime.now()) + '\n\n\n'
        
        # Determines the opposite IP to ping to using the for loop variable ip       
        if ip == ip1:
            print('Pinging from {} to {}'.format(ip, ip2))
            output += connection.send_command('ping {} source {} df-bit size 9000 repeat 50'.format(ip2, ip))
        elif ip == ip2:
            print('Pinging from {} to {}'.format(ip, ip1))
            output += connection.send_command('ping {} source {} df-bit size 9000 repeat 50'.format(ip1, ip))
        else:
            print('Error')

        # Grab arp entry to find interface based on IP
        arp_int = connection.send_command('show arp | i ' + str(ip))
        interface_list = arp_int.split()
        interface = interface_list[-1]
       
        # Rest of the show commands
        output += '\n'*2
        output += 'show clns neighbor ' + interface + ' detail'
        output += connection.send_command('show clns neighbor ' + interface + ' detail')

        output += '\n'*2
        output += 'show interface ' + interface
        output += connection.send_command('show interface ' + interface)
        
        # Print contents of output
        print(output)

        # Create a file to store output into
        filename = 'device_or_' + fqdm[0] + '.txt'
        file = open(filename,'w')
        file.write(output)
        file.close()
        subprocess.call(['open', '-a', 'TextEdit', filename])



    elif device_type == 'cisco_xr':
        print('This is an XR device')

        # Start output variable to store results in
        output = str(datetime.datetime.now()) + '\n\n\n'
        
        # Determines the opposite IP to ping to using the for loop variable ip       
        if ip == ip1:
            print('Pinging from {} to {}'.format(ip, ip2))
            output += connection.send_command('ping {} source {} df-bit size 9000 repeat 50'.format(ip2, ip))
        elif ip == ip2:
            print('Pinging from {} to {}'.format(ip, ip1))
            output += connection.send_command('ping {} source {} df-bit size 9000 repeat 50'.format(ip1, ip))
        else:
            print('Error')

        # Grab arp entry to find interface based on IP
        arp_int = connection.send_command('show arp | i ' + str(ip))
        interface_list = arp_int.split()
        interface = interface_list[-1]
       
        # Rest of the show commands
        output += '\n'*2
        output += 'show isis neighbor ' + interface + ' detail'
        output += connection.send_command('show isis neighbor ' + interface + ' detail')

        output += '\n'*2
        output += 'show interface ' + interface
        output += connection.send_command('show interface ' + interface)
        
        output += '\n'*2
        output += 'show controller ' + interface + ' phy'
        output += connection.send_command('show controller ' + interface + ' phy')
        
        output += '\n'*2
        output += 'show controller ' + interface + ' stats | i “drop|error”'
        output += connection.send_command('show controller ' + interface + ' stats | i "drop|error"')

        # Print contents of output
        print(output)

        # Create a file to store output into
        filename = 'device_or_' + fqdm[0] + '.txt'
        file = open(filename,'w')
        file.write(output)
        file.close()
        subprocess.call(['open', '-a', 'TextEdit', filename])

    elif device_type == 'juniper_junos':


        # Start output variable to store results in
        output = str(datetime.datetime.now()) + '\n\n\n'

        # Grab interface description, find interface entry based on IP
        int_terse = connection.send_command('show interfaces terse | m ' + str(ip))
        interface_list = int_terse.split()
        print(interface_list)
        log_interface = interface_list[1]
        interface = log_interface[:-2]


        # Determines the opposite IP to ping to using the for loop variable ip       
        if ip == ip1:
            print('Pinging from {} to {}'.format(ip, ip2))
            output += connection.send_command('ping {} source {} rapid do-not-fragment size 8972 count 50'.format(ip2, ip))
        elif ip == ip2:
            print('Pinging from {} to {}'.format(ip, ip1))
            output += connection.send_command('ping {} source {} rapid do-not-fragment size 8972 count 50'.format(ip1, ip))
        else:
            print('Error')


        # Rest of the show commands
        output += '\n'*2
        output += 'show isis adjacency detail'
        output += connection.send_command('show isis adjacency detail')


        # Rest of the show commands
        output += '\n'*2
        output += 'show interface ' + interface + ' extensive'
        output += connection.send_command('show interface ' + interface + ' extensive')

        # Print contents of output
        print(output)

        # Create a file to store output into
        filename = 'device_or_' + fqdm[0] + '.txt'
        file = open(filename,'w')
        file.write(output)
        file.close()
        subprocess.call(['open', '-a', 'TextEdit', filename])

    else:
        print("Unknown device - " + device_type)
    x += 1
    connection.disconnect()
