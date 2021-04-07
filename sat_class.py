# -*- coding: utf-8 -*-
"""
Created on Thu Mar 25 10:58:43 2021

@author: Arcobaleno
"""

import glob as g 
import os 
from datetime import datetime as dt
from datetime import timezone as tz
from datetime import timedelta as delta 
import time 

# Classes 
'''
This class Full_Dict do not do any check while adding something in. 
You must check before you make such moves. 
'''
class Full_Dict: 
    # Initialize a dict
    def __init__(self, ini_folder): 
        self.__folder_struct = {} 
        self.__file_struct = {} 
        self.__ini_folder = ini_folder
        self.__Read_file_struct() 
        self.__Read_folder_struct()
    
    def Data_generate(self): 
        # Create folder structure if they didnt exist
        print('Start to check if the folder structure exists... automatically build it if not') 
        path_list = self.__self_Path_generator()
        for path in path_list :
            if os.path.isdir(path) == False :
                os.makedirs(path)
            
        # Loop run: 
        # sleep every 0.5 seconds
        self.__sleep(0.5)
        # calculate the next and next next datetime for each file_struct and sort them into a queue
        queue = [] 
        now = dt.now(tz.utc)
        tmp_fs = self.__file_struct
        tmp_fsk = self.__folder_struct
        for s in tmp_fs.keys(): 
            tmp_first = self.__Next_datetime(tmp_fs[s]['generating datetime format']['content'][0], now) 
            tmp_second = self.__Next_datetime(tmp_fs[s]['generating datetime format']['content'][0], tmp_first) 
            queue.append([tmp_first,s])
            queue.append([tmp_second,s]) 
        queue = self.__Queue_sort(queue) 
        print('Following datetime would be: ')
        for d in queue: 
            print(d[0].strftime('%Y-%m-%d %H:%M:%S'))
        # how long do we have to wait 
        while True: 
            await_time = queue[0][0] - dt.now(tz.utc) 
            print('Going to sleep for ' + str(await_time.total_seconds()) + ' seconds...')
            self.__sleep(await_time.total_seconds())
            # Who uses these filenames? 
            tmp_ele = queue.pop(0) 
            tmp_dt = tmp_ele.pop(0)
            print('Start to find who needs ', tmp_ele)
            for fs in tmp_ele : 
                tmp_fclist = self.__File_create(fs, tmp_dt) 
                tmp_pathlist = []
                for fsk in tmp_fsk.keys(): 
                    if fs in tmp_fsk[fsk]['filename structure']['content']: 
                        print('Found in ' + fsk + ', ' + fs + ' is needed.' )
                        tmp_pathlist.extend(self.__File_path_generator(fsk, tmp_dt))
                tmp_fullpath_list = self.__Path_generator([tmp_pathlist, tmp_fclist])
                # Give their path files.
                print('Start to generate files... ')
                self.__WriteFakeFile(tmp_fullpath_list) 
                print('Files generated.')
                # Refresh queue
                print('Start to refresh datetime queue...')
                now = dt.now(tz.utc)
                tmp_first = self.__Next_datetime(tmp_fs[fs]['generating datetime format']['content'][0], now) 
                tmp_second = self.__Next_datetime(tmp_fs[fs]['generating datetime format']['content'][0], tmp_first) 
                queue.append([tmp_second, fs])
                queue = self.__Queue_sort(queue)     
            print('Following datetime would be: ')
            for d in queue: 
                print(d[0].strftime('%Y-%m-%d %H:%M:%S'))     
        return 
    
    # Write Fake File 
    def __WriteFakeFile(self, fullpathlist) : 
        for file in fullpathlist: 
            tmp_dir = os.path.dirname(file)
            if os.path.isdir(tmp_dir) == False :
                os.makedirs(tmp_dir)
            with open(file,mode='a',encoding='utf-8') as fa: 
                fa.write('file generated!')
        return 
    
    # File path generator
    def __File_path_generator(self, fsk_key, dt) :
        tmp_fsk = self.__folder_struct
        tmp_path_list = [] 
        for i in range(0,len(tmp_fsk[fsk_key]) - 1) : 
            if tmp_fsk[fsk_key]['level ' + str(i)]['type'] == '(datetime)' : 
                tmp_dt = dt.strftime(self.__Normalize_datetimeformat(tmp_fsk[fsk_key]['level ' + str(i)]['content'][0]))
                tmp_path_list.append([tmp_dt])
            else : 
                tmp_path_list.append(tmp_fsk[fsk_key]['level ' + str(i)]['content']) 
        return self.__Path_generator(tmp_path_list)
    
    # File creator
    def __File_create(self, fs_key, dt):  
        tmp_fs = self.__file_struct[fs_key]
        num_pat = int(( len(tmp_fs) - 2 )/2 ) 
        gen_dt_format = tmp_fs['generating datetime format']['content'][0]
        gen_period = tmp_fs['generating period']['content']
        # generate path list 
        tmp_pathlist = [] 
        for i in range(1, num_pat +1):  
            tmp_pat_combi = self.__Combination_generate(tmp_fs['pattern ' + str(i)], dt, gen_dt_format, gen_period) 
            if i != num_pat :
                tmp_pat_combi = [j + tmp_fs['delimiter ' + str(i)]['content'][0] for j in tmp_pat_combi] 
            tmp_pathlist.append(tmp_pat_combi)
        return self.__Path_generator(tmp_pathlist, '')
            
    # Parse different type of content 
    def __Combination_generate(self, d, dt, gen_dt_format=None, gen_period=None): 
        clist = []
        if d['type'] == '(string)':
            clist = d['content']
        elif d['type'] == '(sequence)':     # this sequence is especially for H8 data
            tmp_str = self.__Add_zeroprefix(6, gen_dt_format.strip('YMDhms')) 
            tmp_hour = int(tmp_str[0:2])
            tmp_min = int(tmp_str[2:4])
            tmp_sec = int(tmp_str[4:6]) 
            tmp_delta1 = delta(minutes=tmp_min, seconds=tmp_sec) 
            tmp_delta_dt = delta(hours=dt.hour, minutes=dt.minute, seconds=dt.second) 
            tmp_delta_11 = tmp_delta_dt - tmp_delta1 
            tmp_delta2 = delta(hours=gen_period[0],minutes=gen_period[1], seconds=gen_period[2]) 
            tmp_seq =  int(tmp_delta_11/tmp_delta2)  + int(d['content'][1])
            clist.append(self.__Add_zeroprefix(d['content'][0], tmp_seq)) 
        elif d['type'] == '(datetime)':
            clist.append(dt.strftime(self.__Normalize_datetimeformat(d['content'][0])))
        elif d['type'] == '(number)':
            tmp_dc = d['content']
            tmp_num = [] 
            clist = []
            for i in range(tmp_dc[1],tmp_dc[2]+1, tmp_dc[3]): 
                tmp_num.append(i) 
            clist = [self.__Add_zeroprefix(tmp_dc[0], i) for i in tmp_num] 
        return clist 
    
    # YYYYMMDDhhmmss -> %y%m%d%H%M%S
    def __Normalize_datetimeformat(self,dt_format): 
        return dt_format.replace('YYYY', '%Y').replace('MM','%m').replace('DD','%d').replace('hh', '%H').replace('mm', '%M').replace('ss','%S')
    
    # Add 0 as prefix of numbers 
    def __Add_zeroprefix(self, n, amount): 
        num_complement = n - len(str(amount))
        if num_complement == 0 : 
            return str(amount)
        else:
            return '0'+self.__Add_zeroprefix(n-1, amount) 
            
    # Sort queue in specific form: queue would be like [ [t1(1),fs1,fs2,fs3], [t1(2),fs1], [t2(2), fs2], [t3(2), fs3]  ]
    def __Queue_sort(self, queue) : 
        tmp_queue = [] 
        queue.sort(key = lambda queue: queue[0])
        
        tmp_queue.append(queue.pop(0))
        while len(queue) != 0 : 
            tmp = queue.pop(0)  # [t1, fs1] 
            if tmp[0] == tmp_queue[-1][0] :
                tmp_queue[-1].append(tmp[1]) 
            else :
                tmp_queue.append(tmp)
        return tmp_queue
    
    # Calculate next datetime 
    def __Next_datetime(self, s, dt_now):
        if len(s) == 14:    # normal format YYYYMMDDhhmmss, no support for fixed length larger than 5 
            fixed = s.strip('YMDhms')
            len_fixed = len(fixed)
            now_str = dt_now.strftime('%Y%m%d%H%M%S')
            tmp_str = now_str[0:-len_fixed] + fixed 
            tmp_dt = dt.strptime(tmp_str, '%Y%m%d%H%M%S').replace(tzinfo=tz.utc)
            if tmp_dt > dt_now : 
                return tmp_dt 
            else :  
                return tmp_dt + delta(seconds=self.__timedelta_add(len_fixed))
        else:   # we presume fixed part will cover at least one s in YYYYMMDDhhmms's' 
            fixed = s.strip('YMDhms') 
            len_fixed = len(fixed)
            now_str = dt.now.strptime('%Y%m%d%H%M%S')
            tmp_str = now_str[0:-len_fixed] + fixed 
            tmp_str = tmp_str[0:14]
            tmp_dt = dt.strptime(tmp_str, '%Y%m%d%H%M%S') 
            if tmp_dt > dt_now : 
                return tmp_dt 
            else :  
                return tmp_dt + delta(seconds=self.__timedelta_add(len_fixed))
     
    def __timedelta_add(self, vars): 
        return {
            0 : 1, 
            1 : 10, 
            2 : 60, 
            3 : 600, 
            4 : 3600, 
            5 : 36000
            }.get(vars)
    
    # Generate recursive combination 
    def __Path_generator(self, p, delimiter='/'):    # p is like [[level 0 path],[level 1 path],[level 2 path]] 
        path_list = [] 
        tmp_p = p.copy() 
        if len(tmp_p) == 1:
            return tmp_p[0]
        else : 
            tmp_root = tmp_p[0] 
            tmp_p.pop(0)
            for i in tmp_root: 
                for j in self.__Path_generator(tmp_p, delimiter):
                    path_list.append(i + delimiter + j)
        return path_list
    
    def __self_Path_generator(self): 
        path_list = [] 
        tmp_s = self.__folder_struct
        for k in tmp_s.keys() : 
            tmp_list = [] 
            tmp_datetime_flag = False 
            tmp_len = len(tmp_s[k]) - 1
            # make sure to which level is fixed 
            for i in range(0, tmp_len) : 
                if tmp_s[k]['level ' + str(i)]['type'] == '(datetime)': 
                    tmp_datetime_flag = True
                    break 
            tmp_level_cnt = i 
            if tmp_datetime_flag == True: 
                for i in range(0, tmp_level_cnt): 
                    tmp_list.append(tmp_s[k]['level ' + str(i)]['content'])    
            else :
                for i in range(0, tmp_level_cnt + 1):
                    tmp_list.append(tmp_s[k]['level ' + str(i)]['content']) 
            path_list.extend(self.__Path_generator(tmp_list))
        return path_list 
    
    # Read ini files
    def __Read_file_struct(self): 
        # Read in ini file 
        self.__file_struct = self.__Read_ini(self.__ini_folder + '/file_struct.ini')
        # analyze content 
        
        return 
    
    def __Read_folder_struct(self): 
        self.__folder_struct = self.__Read_ini(self.__ini_folder + '/folder_struct.ini')
        return 
    
    # Format conversion 
    def __datetime_format_convert(self,strftime):
        return 
        
    
    # Sleep sec by sec
    def __sleep(self,seconds): 
        time.sleep(seconds%1)
        for i in range(0,int(seconds)): 
            time.sleep(1) 
        return 
    
    # Read in ini-typed file with specific ini structure
    def __Read_ini(self,filename): 
        tmp_d = {} 
        with open(filename, mode='r') as fr : 
            s = fr.readline().strip('\n') 
            while s != '': 
                # title 
                if s.startswith('[') and s.endswith(']'):
                    s = s.strip('[]')
                    tmp_d[s] = {} 
                    tmp_title = s
                # attribute
                else : 
                    s = s.split(':',1) 
                    tmp_attr = s[0] 
                    tmp_s = s[1].split(',')
                    tmp_type = tmp_s[0]
                    tmp_d[tmp_title][tmp_attr] = {'type': tmp_type, 'content':[]}
                    if tmp_type == '(string)' or tmp_type == '(datetime)' or tmp_type == '(filename structure)': 
                        for i in range(1,len(tmp_s)):
                            tmp_d[tmp_title][tmp_attr]['content'].append(tmp_s[i]) 
                    else : 
                        for i in range(1,len(tmp_s)):
                            tmp_d[tmp_title][tmp_attr]['content'].append(int(tmp_s[i])) 
                # update s
                s = fr.readline().strip('\n') 
        return tmp_d
    
    # for debug 
    def SHOW(self): 
        return self.__file_struct, self.__folder_struct 






