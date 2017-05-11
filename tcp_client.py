#!/usr/bin/env python

import socket


def tcpmessage(message):
    tpc_ip = 'localhost'
    tcp_port = 7770

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((tpc_ip, tcp_port))
    s.sendall(message)  # remember, this should terminate with a \n
    s.close()

def metacompose_start():
    tcpmessage("start"+"\n")

def metacompose_stop():
    tcpmessage("stop"+"\n")

def metacompose_change_composition( id ):
    tcpmessage("changeComposition,"+id+"\n")

def metacompose_change_mood( valence, arousal ):
    tcpmessage("setCoord,"+str(valence)+","+str(arousal)+"\n")
