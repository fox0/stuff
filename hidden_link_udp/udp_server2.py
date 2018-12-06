# coding: utf-8
from socket import socket, AF_INET, SOCK_STREAM, SOCK_DGRAM, error
from thread import start_new_thread
#from select import select


HOST = "0.0.0.0"
PORT = 55555

PORT2 = 50000  # begin range

BUF_SIZE = 8*1024

CMD = {}
SETTINGS = {}
ADDRESSES = {}  # 'сокет_udp': адрес_клиента


def main():
    udp_control_port = socket(AF_INET, SOCK_DGRAM)
    udp_control_port.bind((HOST, PORT))
    
    while True:
        data, addr = udp_control_port.recvfrom(BUF_SIZE)
        if not data:
            continue
        param = data.split()
        try:
            data = CMD[param[0]](param[1:])
        except KeyError:
            data = 'error: no cmd'
        udp_control_port.sendto(data, addr)
    

CMD['ping'] = lambda param: 'ok'
    

def cmd_set(param):
    global SETTINGS 
    try:
        SETTINGS[param[0]] = param[1]
    except IndexError:
        return 'error: no param'
    return 'ok'
CMD['set'] = cmd_set


def cmd_get(param):
    global PORT2, ADDRESSES
    tcp = socket(AF_INET, SOCK_STREAM)
    try:
        tcp.connect((SETTINGS['host'], int(SETTINGS['port'])))
    except KeyError:
        return 'error: no settings'
        
    udp = socket(AF_INET, SOCK_DGRAM)
    udp.bind((HOST, PORT2))
    ADDRESSES[udp] = None  # пока адрес неизвестен
    
    start_new_thread(udp_to_tcp, (udp, tcp))
    start_new_thread(tcp_to_udp, (udp, tcp))
    
    PORT2 += 1  # TODO if > 64K
    return str(PORT2-1)
CMD['get'] = cmd_get


def udp_to_tcp(udp, tcp):
    global ADDRESSES
    while True:
        data, addr = udp.recvfrom(BUF_SIZE)
        if not data:
            continue
        ADDRESSES[udp] = addr  # запоминаем
        tcp.send(data)  # socket.error: [Errno 9] Bad file descriptor


def tcp_to_udp(udp, tcp):
    while True:
        data = tcp.recv(BUF_SIZE)  # TODO select
        if not data:
            # здесь циклится
            continue
        udp.sendto(data, ADDRESSES[udp])


if __name__ == '__main__':
    main()
