#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import signal
import time
import sys
import atexit

class MyFile:
    #"""
    #файлоподобный объект
    #"""
    data = '' #TODO b''
    
    def write(this, data):
        this.data += data
        
    def read(this, blocksize=None):
        if blocksize:
            ret = this.data[:blocksize]
            this.data = this.data[blocksize:]
            return ret
        else:
            return this.data
            
class Daemon:
    #"""
    #A generic daemon class.
    #Usage: subclass the Daemon class and override the run() method
    #"""
    #http://www.jejik.com/articles/2007/02/a_simple_unix_linux_daemon_in_python/
    stdin = '/dev/null'
    stdout = '/home/logout.txt'#'/dev/null'
    stderr = '/home/logerr.txt'#'/dev/null'
    pidfile = '/tmp/mydaemon.pid'

    def daemonize(this):
        #"""
        #do the UNIX double-fork magic, see Stevens' "Advanced
        #Programming in the UNIX Environment" for details (ISBN 0201563177)
        #http://www.erlenstar.demon.co.uk/unix/faq_2.html#SEC16
        #"""
        try:
            pid = os.fork()
            if pid > 0:
                # exit first parent
                sys.exit(0)
        except OSError, e:
            sys.stderr.write("fork #1 failed: %d (%s)\n" % (e.errno, e.strerror))
            sys.exit(1)
        # decouple from parent environment
        os.chdir("/")
        os.setsid()
        os.umask(0)
        # do second fork
        try:
            pid = os.fork()
            if pid > 0:
                # exit from second parent
                sys.exit(0)
        except OSError, e:
            sys.stderr.write("fork #2 failed: %d (%s)\n" % (e.errno, e.strerror))
            sys.exit(1)
        # redirect standard file descriptors
        sys.stdout.flush()
        sys.stderr.flush()
        si = file(this.stdin, 'r')
        so = file(this.stdout, 'a+')
        se = file(this.stderr, 'a+', 0)
        os.dup2(si.fileno(), sys.stdin.fileno())
        os.dup2(so.fileno(), sys.stdout.fileno())
        os.dup2(se.fileno(), sys.stderr.fileno())
        # write pidfile
        atexit.register(this.delpid)
        pid = str(os.getpid())
        file(this.pidfile,'w+').write("%s\n" % pid)

    def delpid(this):
        os.remove(this.pidfile)

    def start(this):
        #"""
        #Start the daemon
        #"""
        # Check for a pidfile to see if the daemon already runs
        try:
            pf = file(this.pidfile,'r')
            pid = int(pf.read().strip())
            pf.close()
        except IOError:
            pid = None
        if pid:
            message = "Daemon already running?\n"
            sys.stderr.write(message)
            sys.exit(1)
        # Start the daemon
        this.daemonize()
        this.run()

    def stop(this):
        #"""
        #Stop the daemon
        #"""
        # Get the pid from the pidfile
        try:
            pf = file(this.pidfile,'r')
            pid = int(pf.read().strip())
            pf.close()
        except IOError:
            pid = None
        if not pid:
            message = "Daemon not running?\n"
            sys.stderr.write(message)
            return # not an error in a restart
        # Try killing the daemon process       
        try:
            while 1:
                os.kill(pid, signal.SIGTERM)
                time.sleep(0.1)
        except OSError, err:
            err = str(err)
            if err.find("No such process") > 0:
                if os.path.exists(this.pidfile):
                    os.remove(this.pidfile)
            else:
                print str(err)
                sys.exit(1)

    def restart(this):
        #"""
        #Restart the daemon
        #"""
        this.stop()
        this.start()

    def run(this):
        #"""
        #You should override this method when you subclass Daemon.
        #It will be called after the process has been
        #daemonized by start() or restart().
        #"""
        pass        

