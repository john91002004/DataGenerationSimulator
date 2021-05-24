# -*- coding: utf-8 -*-
"""
Created on Thu Mar 25 10:58:43 2021

@author: Arcobaleno
"""

import sat_class as sc

# Parameters 
error_log = './error.log'

# Main 
while True:
    try: 
        d = sc.Full_Dict('./')
        d.Periodical_Check() 
    except Exception as e: 
        # write error to log and restart whole program again 
        Log_err(str(e)) 

# Functions 
def Log_err(*s ,sep=' ', end='\n') : 
    "Print and log error messages."
    now_ts = dt.now(tz.utc).strftime('%Y-%m-%d %H:%M:%S')
    print('##[' + now_ts + ']## ',end = '')
    for i in range(0,len(s)): 
        print(s[i],sep=sep,end=end)
    with open(file=error_log, mode='a') as fa : 
        fa.write('##[' + now_ts + ']## ')
        for i in range(0,len(s)):
            fa.write(str(s[i]))
            if i != len(s) - 1: 
                fa.write(sep)
        fa.write(end)
    return 