#!/bin/bash

#kill worker
ps axf | grep worker_peter.py | grep -v grep | awk '{print "kill -15 " $1}' | sh
ps axf | grep worker_example.py | grep -v grep | awk '{print "kill -15 " $1}' | sh
ps axf | grep worker_example_2.py | grep -v grep | awk '{print "kill -15 " $1}' | sh
#kill master
ps axf | grep master_server_golden.py | grep -v grep | awk '{print "kill -15 " $1}' | sh
ps axf | grep master_server_example.py | grep -v grep | awk '{print "kill -15 " $1}' | sh
