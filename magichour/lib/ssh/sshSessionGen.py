import paramiko
from random import randint
from argparse import ArgumentParser
import sys
import datetime
import time


def main(argv):
    parser = ArgumentParser()
    parser.add_argument('-c', '--commands', dest='commands', required=True,
                        help='list of commands to select from')
    parser.add_argument('-d', '--delay', dest='delay', required=True,
                        help='upto seconds of wait before ssh \
                        session starts or completes')
    parser.add_argument('-a', '--address', dest='address', required=True,
                        help='address of machine to run ssh on')
    parser.add_argument('-s', '--session', dest='session', required=True,
                        help='minimum session length in seconds')
    parser.add_argument('-l', '--log', dest='logOutput', required=True,
                        help='file to log to')

    options = parser.parse_args()

    c = open(options.commands, 'r').readlines()
    commands = [command.strip().rstrip() for command in c]

    delay = int(options.delay)

    address = options.address

    sessionLength = int(options.session) + randint(0, delay)

    command = commands[randint(0, len(commands)-1)]

    outFile = open(options.logOutput, 'aw')


    time.sleep(randint(0,delay))
    outFile.write('Starting %s [%s]\n' % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), command))
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.load_system_host_keys()
    actualCommand = '%s;sleep %i;logout\n' % (command, sessionLength)
    #ssh.connect(address,key_filename='/Users/dgrossman/.ssh/id_rsa')
    ssh.connect(address)
    ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(actualCommand)
    for line in ssh_stdout.read().splitlines():
        outFile.write('%s\n'%line)
    outFile.write('Ending %s [%s]\n' % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), command))
    outFile.close()


if __name__ == '__main__':
    main(sys.argv[1:])
