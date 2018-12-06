#!/usr/bin/python
# -*- coding: utf-8 -*-
# 23.04.14
NAME = 'ICMP++ 0.3.2 test'

from mylib import *     # my lib
import rsa, rsa.bigfile # my lib

#sys.stderr = None #чтобы не сыпались предупреждения
from scapy.all import * # my lib
#sys.stderr = sys.__stderr__

import socket
import fcntl
import struct
import subprocess
import thread
import datetime
import random
import string

def printf(text, color='red'):#TODO log
    colors = { #TODO
        'black':    '\x1b[01;30m',
        'red':      '\x1b[01;31m',
        'green':    '\x1b[01;32m',
        'yellow':   '\x1b[01;33m',
        #~ "brown": "\x1b[01;31m",
        #~ "blue": "\x1b[01;34m",
        #~ "magenta": "\x1b[01;35m",
        #~ "cyan": "\x1b[01;36m",
        #~ "white": "\x1b[01;37m",
        #~ "bold": "\x1b[01;39m"
    }
    print str(datetime.datetime.now())+' '+colors[color]+text+'\x1b[01;0m'
def get_if_list():
    # Возвращает список физических сетевых интерфейсов представленных в системе
    # >>> get_if_list()
    # ['lo', 'eth0']
    try:
        if_list = []
        f = None
        f = open('/proc/net/dev', mode='r')
        while True:
            line = f.readline().strip()
            if line == '':
                break
            pos = line.find(':')
            if pos != -1:
                if_list.append(line[0:pos])
        return if_list
    except IOError as error:
        printf('Error: {0}'.format(error))
        return None
    finally:
        if f:
            f.close()
def get_ip_addr(if_name):
    # Возвращает ip-адрес интерфейса. if-name - имя интерфейса
    # >>> get_ip_addr('lo')
    # 127.0.0.1
    try:
        s = None
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        if_name_byte = struct.pack('256s', if_name.encode('utf-8'))
        if_addr_byte = fcntl.ioctl(s.fileno(), 0x8915, if_name_byte)[20:24]
        return socket.inet_ntoa(if_addr_byte)
    except:
        return None
    finally:
        if s:
            s.close()
def get_myip():
    #возвращает ip машины
    kol = 0
    for i in get_if_list():
        if get_ip_addr(i):
            if i != 'lo':
                kol += 1
    if kol == 0:
        printf ('FATAL ERROR: no interfaces','red')
        sys.exit(1)
    elif kol == 1:
        for i in get_if_list():
            temp_ip = get_ip_addr(i)
            if temp_ip:
                if i != 'lo':
                    return temp_ip
    else:
        return '255.255.255.255' #TODO блин...
def case(string, data):
    # in: 'fox', 'foxhello'
    # out: 'hello'
    # 
    # in: 'fox', 'foohello'
    # out: None
    l = len(string)
    if string[:l-1] == data[:l-1]:
        return data[l:]
    return None
########################################################################
# не ТРОГАТЬ!!! Not remove this class!!!
class Client(Daemon):
    # NOT TOUCH!!!
    static_public_key  =  rsa.PublicKey(94423155346464715937887005845785374791366091320777957623886216636267712512553133198303572081471946529130385936021074697086560707380531944775314807009940506961057002909328992207634904050930754587124145193762354520091584038071050184876663518932774895373969744911897488293139957436774036689768161961219689258479, 65537)
    static_private_key = rsa.PrivateKey(94423155346464715937887005845785374791366091320777957623886216636267712512553133198303572081471946529130385936021074697086560707380531944775314807009940506961057002909328992207634904050930754587124145193762354520091584038071050184876663518932774895373969744911897488293139957436774036689768161961219689258479, 65537, 5055630439457782446954323565510488428565598279515538601129388500795938221257441512318953178111373123132253906182735723516131979220871974521515777088342808324975120717697486533306517391674735951270595332300917151620058800772020068333125413888234499204230957861707879754180450843426065839857959224889376218305, 49803123000778698925642713736182117740225860098835434944466473365159401772848941772685265649350672317988203249904243164667439262569884717102776229541427192122650657, 1895928400815112709479619766598534169010844074180945213404519451561067828004113057541440402289975444329702630819605173469408901665925428236536847)
    # keys
    pubkey = None
    privkey = None
    #...
    myid = os.getpid() & 0xFFFF
    snifbuf = []
    buf0 = []
    buf = []
    uk = 0
    maxuk = 0
    close = False
    #
    conn = None #server socket

    def decrypt(this, mess, key):#++
        #расшифровывает
        infile = MyFile()
        infile.write(mess)
        outfile = MyFile()
        try:
            rsa.bigfile.decrypt_bigfile(infile, outfile, key)
        except TypeError:
            printf('ERROR: decrypt() no key')
            return ''
        except ValueError:
            printf('ERROR: decrypt() ValueError')
            return ''
        return str(outfile.read())
    def encrypt(this, mess, key):#++
        #шифрует
        infile = MyFile()
        infile.write(mess)
        outfile = MyFile()
        try:
            rsa.bigfile.encrypt_bigfile(infile, outfile, key)
        except TypeError:
            printf('ERROR: encrypt() no key')
            return ''
        return str(outfile.read())
    def keys(this):#++
        name = '/home/.keys.txt'
        try:
            with open(name,'r') as f:
                data = f.read()
            this.pubkey = rsa.PublicKey.load_pkcs1(data)
            this.privkey = rsa.PrivateKey.load_pkcs1(data)
        except:
            printf('Generic keys. Please wait...','green')
            this.pubkey, this.privkey = rsa.newkeys(2048, poolsize=2) #2 core
            with open(name,'w') as f:
                f.write(this.pubkey.save_pkcs1())
                f.write(this.privkey.save_pkcs1())
                os.system("chmod -w "+name)
            printf('Generic keys OK','green')
        # теперь страдаем фигнёй
        # test 1
        text1 =''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for x in range(16))
        text2 = rsa.encrypt(text1, this.static_public_key)
        text3 = rsa.decrypt(text2, this.static_private_key)
        if text1 != text3:
            printf('FATAL ERROR: fail test 1')
        # test 2
        text1 =''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for x in range(16))
        text2 = rsa.encrypt(text1, this.pubkey)
        text3 = rsa.decrypt(text2, this.privkey)
        if text1 != text3:
            printf('ERROR: fail test 2',)
            keys()
        # test 3
        text1 =''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for x in range(1024))
        text2 = this.encrypt(text1, this.static_public_key)
        text3 = this.decrypt(text2, this.static_private_key)
        if text1 != text3:
            printf('FATAL ERROR: fail test 3')
        # test 4
        text1 =''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for x in range(1024))
        text2 = this.encrypt(text1, this.pubkey)
        text3 = this.decrypt(text2, this.privkey)
        if text1 != text3:
            printf('ERROR: fail test 4')
    def startsniff(this): #+
        #собирает все пакеты
        #this.flag_sniff = True
        printf("DEBUG> Sniffer OK",'black')
        try:
            sniff(lfilter=this.myfilter, store=0)
        except socket.error, (errno, msg):
            #this.flag_sniff = False
            if errno == 1:
                printf ('\nFATAL ERROR: RUNNING AS ROOT!!!','red')
            else:
                printf ("ERROR "+str(errno) +": startsniff() "+msg)
    def myfilter(this, packet):#-
        #TODO не только  ICMP!!! Ещё IP!!! кусочки большого пакета!!!
        if not packet.haslayer(ICMP): # отфильтровываем все лишнее
            return
        if packet[ICMP].type != 0: # эхо-ответ
            return
        if packet[ICMP].id == this.myid:
            return
            #todo myip
        this.snifbuf += [packet] #ложим в очередь
    def fdecrypt(this): #+
        printf("DEBUG> fdecrypt OK",'black')
        while True:
            if len(this.snifbuf)>0:
                packet = this.snifbuf.pop(0)
                while packet:
                    #todo id
                    data = this.decrypt(packet.load, this.static_private_key)#долго
                    printf("DEBUG> decrypt "+str(packet[ICMP].seq),'black')
                    if (data=="CLOSE"):
                        this.close = True
                        printf("DEBUG> listen close",'black')
                        break
                    if (data=="RESEND"):
                        printf("DEBUG> resend "+str(packet[ICMP].seq),'black')
                        this.go(this.encrypt(this.buf0[packet[ICMP].seq], this.static_public_key),packet[ICMP].seq)
                        break
                    this.buf[packet[ICMP].seq] = data
                    this.maxuk = packet[ICMP].seq #TODO if >
                    packet = this.snifbuf.pop(0)
            else:
                #printf("DEBUG> fdecrypt sleep...",'black')
                time.sleep(0.2)
    def go(this, string, num_pack=0): #+
        if string=='':
            printf('go: ERROR: mess==null')
            return
        #if len (string)>1472: #TODO
        #   printf("WARNING: message too long! "+str(len(string))+" > 1467:",'yellow')
        # отправляет пакет
        data = string
        try:
            #sendp(Ether(src="00:11:22:33:44:55",dst="00:25:84:d9:38:00")/IP(src=this.myip,dst=this.srvip)/ICMP(type=8,id=this.myid,seq=num_pack)/data,iface="eth0")# 8 (эхо-запрос)
            send(IP(src=this.myip,dst=this.srvip)/ICMP(type=8,id=this.myid,seq=num_pack)/data,)
        except socket.error, (errno, msg):
            if errno == 1:
                printf ('FATAL ERROR: Operation not permitted. RUNNING AS ROOT!!!','red')
                sys.exit(1)
            elif errno == 19:
                printf ('FATAL ERROR: No such device','red')
                sys.exit(1)
            else:
                printf ("ERROR "+str(errno) +": go() "+msg)
        except struct.error, msg:
            printf ("ERROR2: go() "+str(msg))
    ####################################################################
    def buff(this):#+?
        #забирает данные из буфера 
        #with open(random.choice(string.ascii_uppercase+string.ascii_lowercase+string.digits)+"file.gif",'w') as f:
        while True:
            while this.buf[this.uk]:
                printf("DEBUG> save "+str(this.uk),'black')
                #printf("DEBUG> "+str(this.uk)+": "+this.buf[this.uk],'black')
                this.conn.sendall(this.buf[this.uk])
                this.buf[this.uk]=None
                this.uk+=1
            if (this.maxuk>this.uk):
                printf("DEBUG> fail save. uk="+str(this.uk)+", max="+str(this.maxuk))
                if this.maxuk-this.uk < 100:
                    for i in range(this.uk,this.maxuk):#TODO до первого принятого
                        printf("DEBUG> re "+str(i),'black')
                        this.go(this.encrypt("RESEND", this.static_public_key),i)
                else:
                    for i in range(this.uk,this.uk+100):#TODO до первого принятого
                        printf("DEBUG> re "+str(i),'black')
                        this.go(this.encrypt("RESEND", this.static_public_key),i)
            time.sleep(0.5)
            if (this.close):#TODO
                while this.buf[this.uk]:
                    printf("DEBUG> close save "+str(this.uk),'black')
                    #printf("DEBUG> "+str(this.uk)+": "+this.buf[this.uk],'black')
                    this.conn.sendall(this.buf[this.uk])
                    this.buf[this.uk]=None
                    this.uk+=1 #TODO!!!
                printf("DEBUG> buff close",'black')
                return
  
        #~ return
        ### PING ###
        #~ data = case('PING', temp) # вернулся ping сервера
        #~ if data:
            #~ timeReceived = time.time()
            #~ timeSent, q = struct.unpack("ds", data[:9])
            #~ time1 = (timeReceived - timeSent) * 1000
            #~ size = len(packet.load)+4
            #~ this.prints("%i bytes from "%size+packet[IP].src+": time=%0.0f ms"%time1)#???
            #~ return
        #~ ### PREVET ###
        #~ data = case('PREVET', temp) # ping клиента меня пингуют
        #~ if data:
            #~ this.prints("ping me "+packet[IP].src+"."+temp_ip1)
            #~ this.go_crypt('MEDVED'+data, packet[IP].src, temp_ip1, this.static_public_key)
            #~ return
        #~ ### MEDVED ###
        #~ data = case('MEDVED', temp) # вернулся ping клиента2
        #~ if data:
            #~ timeReceived = time.time()
            #~ timeSent, q = struct.unpack("ds", data[:9])
            #~ time1 = (timeReceived - timeSent) * 1000
            #~ size = len(packet.load)+4
            #~ this.prints("%i bytes from "%size+packet[IP].src+"."+temp_ip1+": time=%0.0f ms"%time1)#???
            #~ return
        #~ ### KEY ###
        #~ data = case('KEY', temp) # пришёл ключ
        #~ if data:
            #~ this.key = rsa.PublicKey.load_pkcs1(data)#TODO хранить в списке
            #~ if not this.key:
                #~ this.printf('ERROR: get KEY')
            #~ this.prints("get key from "+packet[IP].src+"."+temp_ip1)#???
            #~ return
        ### GETKEY ###!!!TODO
       # print temp
       # return
    ####################################################################
  
    ####################################################################
    def main(this):
        printf(NAME,'black')
        for i in range(0,1024*64):#init
            this.buf0 += [None]
        for i in range(0,1024*64):
            this.buf += [None]
        printf("DEBUG> buf init OK",'black')
        thread.start_new_thread(this.startsniff,())# запускаем сниффер
        thread.start_new_thread(this.fdecrypt,())
        thread.start_new_thread(this.buff,())
        this.myip = get_myip()# мой ip
        printf("DEBUG> ip="+this.myip,'black')
        this.srvip = "193.19.126.44"
        printf("DEBUG> srvip="+this.srvip,'black')
        this.keys()
        printf("DEBUG> Keys OK",'black')
        r = 1000 #1024*63
        #while True:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) #ЧТО ЭТО???
            s.bind(('localhost', 2343)) #BUG TODO как освободить порт???
            s.listen(1)
            printf("DEBUG> proxy: localhost:2343",'black')
            while True:
                try:
                    this.conn, addr = s.accept()#TODO пока один клиент
                    printf('DEBUG> client connect %s'%addr[0],'black')
                    i=0
                    while True:
                        data = this.conn.recv(r)
                        if data:
                            this.buf0[i] = data
                            printf("DEBUG> send "+str(i),'black')
                            this.go(this.encrypt(data, this.static_public_key),i)
                            i+=1
                        else:
                            #printf("DEBUG> server socket sleep",'black')
                            time.sleep(0.5)
                except socket.error, (errno, msg):
                    if errno == 32:
                        printf('ERROR: Разрыв соединения c клиентом %s'%addr[0],'red')
                    else:
                        printf ("ERROR "+str(errno) +": main() "+msg)
        except socket.error, (errno, msg):
            if errno == 98:
                printf('ERROR: Порт 2343 занят','red')
            else:
                printf ("ERROR "+str(errno) +": main() "+msg)
        finally:
            s.close()
        printf('ERROR: server socket FAIL')     
        while True:
            time.sleep(100)
        #~ with open("1.gif",'r') as f:
            #~ i=0
            #~ data = f.read(r)
            #~ while data:
                #~ this.buf0[i] = data
                #~ printf("DEBUG> send "+str(i),'black')
                #~ this.go(this.encrypt(data, this.static_public_key),i)
               #~ # time.sleep(0.01)
                #~ data = f.read(r)
                #~ i+=1
            #~ this.go(this.encrypt("CLOSE", this.static_public_key),i)
            #~ printf("DEBUG> send close",'black')
        #~ while True:
            #~ text= raw_input(">")
########################################################################
if __name__ == "__main__":
    _old_excepthook = sys.excepthook
    def myexcepthook(exctype, value, traceback):
        if exctype == KeyboardInterrupt: # Ctrl+C
            printf('Exit...','green')
        else:
            _old_excepthook(exctype, value, traceback)
    sys.excepthook = myexcepthook
    Client().main()
