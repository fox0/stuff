# coding: utf-8
from socket import socket, AF_INET, SOCK_STREAM, SOCK_DGRAM
from thread import start_new_thread


HOST = "localhost"
PORT = 2343

SERVER_HOST = "<skip>"
SERVER_PORT = 55555

PROXY_HOST = "<skip>"
PROXY_PORT = 3128

BUF_SIZE = 8*1024


#~ TCP_ADDR = ("0.0.0.0", 2343)
#~ UDP_ADDR = ("<skip>", 2343)
#~ #UDP_ADDR = ("0.0.0.0", 2343)


control_port = None


def main():
    global control_port
    
    s = socket(AF_INET, SOCK_STREAM)
    s.bind((HOST, PORT))
    s.listen(10)
    print('%s:%s' % (HOST, PORT))
    print('server: %s:%s\n' % (SERVER_HOST, SERVER_PORT))
    
    control_port = socket(AF_INET, SOCK_DGRAM)  # UDP
    control_port.connect((SERVER_HOST, SERVER_PORT))
    
    ask('ping')
    ask('set host ' + PROXY_HOST)
    ask('set port ' + str(PROXY_PORT))

    while True:
        conn, addr = s.accept()
        start_new_thread(func_thread, (conn,))


def func_thread(conn):
    s = socket(AF_INET, SOCK_DGRAM)  # UDP
    s.connect((SERVER_HOST, int(ask('get'))))  # ValueError: invalid literal for int() with base 10: 'error: no settings'
    
    start_new_thread(send, (conn, s))
    send(s, conn)
    #conn.close()


def send(s_from, s_to):
    while True:
        data = s_from.recv(BUF_SIZE)  # socket.error: [Errno 111] Connection refused
        if not data:
            break
        s_to.send(data)  # socket.error: [Errno 32] Broken pipe
        #~ except error, (errno, msg):  # socket.error


def ask(string):
    global control_port
    res = ''
    print('> '+string)
    control_port.send(string)
    res = control_port.recv(BUF_SIZE)  # socket.error: [Errno 111] Connection refused
    print(res)
    return res


if __name__ == '__main__':
    main()    
