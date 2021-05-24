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
import re 

# Classes 
'''
This class Full_Dict do not do any check while adding something in. 
You must check before you make such moves. 
'''
class Full_Dict: 
    # Constant Parameters 
    __none_size = -10
    __none_dt = dt(1000,1,1,0,0,tzinfo=tz.utc)
    
    # Constructor
    def __init__(self, ini_folder): 
        "Initialize a Full_Dict which contains all configurations such as folder structure and file structure."
        self.__folder_struct = {} 
        self.__file_struct = {} 
        self.__ini_folder = ini_folder
        self.__Read_file_struct() 
        self.__Read_folder_struct()
        self.__Read_manam_struct()
        self.__logdir = ini_folder + '/object_log/'
        if not os.path.isdir(self.__logdir) :
            os.makedirs(self.__logdir) 
        self.__debug_log_data_check = ini_folder + '/debug_data_check.log'
        self.__debug_log_data_gen = ini_folder + '/debug_data_gen.log'
    
    # Main public function 
    # Generate data
    def Data_generate(self): 
        "Generate data according to your settings in folder_struct and file_struct."
        # Create folder structure if they didnt exist
        self.__Log_data_gen('Start to check if the folder structure exists... automatically build it if not') 
        path_list = self.__self_Path_generator()
        for path in path_list :
            if os.path.isdir(path) == False :
                os.makedirs(path)
            
        # Loop run: 
        # sleep every 0.5 seconds
        self.__sleep(0.5)
        # calculate the next and next next datetime for each file_struct and sort them into a queue
        # queue will be like [ [t1(1),fs1,fs2,fs3], [t1(2),fs1], [t2(2), fs2], [t3(2), fs3]  ]
        # queue is a list of lists, where the lists contains datetime as first element, file structures as following elements.
        # queue is sorted by datetime of every list.
        self.__Log_data_gen('Perparing queue where contains the following datetime to generate fake data...') 
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
        self.__Log_data_gen('Following datetime and corresponding file structures would be: ')
        for d in queue: 
            self.__Log_data_gen(d[0].strftime('%Y-%m-%d %H:%M:%S'))
            for tmp_i in range(1,len(d)):
                self.__Log_data_gen(d[tmp_i])
            self.__Log_data_gen() 
        # how long do we have to wait 
        while True: 
            await_time = queue[0][0] - dt.now(tz.utc) 
            self.__Log_data_gen('Going to sleep for ' + str(await_time.total_seconds()) + ' seconds...')
            self.__sleep(await_time.total_seconds())
            # Who uses these filenames? 
            tmp_ele = queue.pop(0) 
            tmp_dt = tmp_ele.pop(0)
            self.__Log_data_gen('Time up. Start to find who needs ', tmp_ele)
            for fs in tmp_ele : 
                tmp_fclist = self.__File_create(fs, tmp_dt)     # combination file list according to file structure 
                tmp_pathlist = []   # combination dir path list according to folder structure 
                for fsk in tmp_fsk.keys(): 
                    if fs in tmp_fsk[fsk]['filename structure']['content']: 
                        self.__Log_data_gen('Found in ' + fsk + ', ' + fs + ' is needed.' )
                        tmp_pathlist.extend(self.__Dir_path_generator(fsk, tmp_dt))
                tmp_fullpath_list = self.__Path_generator([tmp_pathlist, tmp_fclist])   # combination full path list for each file to be generated
                # Give their path files.
                self.__Log_data_gen('Start to generate files... ')
                self.__WriteFakeFile(tmp_fullpath_list) 
                self.__Log_data_gen('Files generated.')
                # Refresh queue
                self.__Log_data_gen('Start to refresh datetime queue...')
                now = dt.now(tz.utc)
                tmp_first = self.__Next_datetime(tmp_fs[fs]['generating datetime format']['content'][0], now) 
                tmp_second = self.__Next_datetime(tmp_fs[fs]['generating datetime format']['content'][0], tmp_first) 
                queue.append([tmp_second, fs])
                queue = self.__Queue_sort(queue)     
            self.__Log_data_gen('Following datetime and corresponding file structures would be: ')
            for d in queue: 
                self.__Log_data_gen(d[0].strftime('%Y-%m-%d %H:%M:%S'))
                for tmp_i in range(1,len(d)):
                    self.__Log_data_gen(d[tmp_i])
                self.__Log_data_gen() 
        return 
    
    # Private functions
    # Write Fake File 
    def __WriteFakeFile(self, fullpathlist) :
        "Generate fake files named in fullpathlist."
        for file in fullpathlist: 
            tmp_dir = os.path.dirname(file)
            if os.path.isdir(tmp_dir) == False :
                os.makedirs(tmp_dir)
            with open(file,mode='a',encoding='utf-8') as fa: 
                fa.write('file generated!')
        return 
    
    # File path generator
    def __Dir_path_generator(self, fsk_key, dt) :
        "For specific folder structure(fsk_key) and datetime(dt), return a specific list of dir path."
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
        "For specific file structure(fsk_key) and datetime(dt), return a specific list of filenames."
        # For convenience 
        tmp_fs = self.__file_struct[fs_key]
        # Calculate how many pattern and delimiter 
        num_pat = 0 
        for tmp_key in tmp_fs.keys() : 
            if 'pattern' in tmp_key or 'delimiter' in tmp_key : 
                num_pat = num_pat + 1  
        num_pat = int((num_pat - 1) /2 ) 
        gen_dt_format = tmp_fs['generating datetime format']['content'][0]
        gen_period = tmp_fs['generating period']['content']
        # generate path list 
        tmp_pathlist = [] 
        for i in range(1, num_pat +2):  
            tmp_pat_combi = self.__Combination_generate(tmp_fs['pattern ' + str(i)], dt, gen_dt_format, gen_period) 
            if i != num_pat + 1: 
                tmp_pat_combi = [j + tmp_fs['delimiter ' + str(i)]['content'][0] for j in tmp_pat_combi] 
            tmp_pathlist.append(tmp_pat_combi)
        return self.__Path_generator(tmp_pathlist, '')
            
    # Parse different type of content 
    def __Combination_generate(self, d, dt, gen_dt_format=None, gen_period=None): 
        "Generate a list of strings that accords to specific type of content."
        clist = []
        if d['type'] == '(string)':
            clist = d['content']
        elif d['type'] == '(sequence)':     # this sequence is especially for GK2A data
            tmp_manam = d['content'][0]
            tmp_product = d['content'][1]
            tmp_dir = self.__manam_struct[tmp_manam]['level 0']['content'][0]
            tmp_latest_manam_file = g.glob(tmp_dir + '/*.txt')
            tmp_latest_manam_file.sort(key=os.path.getmtime) 
            tmp_latest_manam_file = tmp_latest_manam_file[-1] 
            tmp_dict = self.__Manam2Dict(tmp_latest_manam_file, tmp_manam)
            tmp_hhmmss = dt.strftime('%H%M%S') 
            tmp_dict2 = tmp_dict['manam'][tmp_product]
            result = 'XXX'
            for tmp_key, tmp_value in tmp_dict2.items(): 
                if tmp_value['start_tm'] == tmp_hhmmss: 
                    result = tmp_key 
                    break 
            clist.append(result)
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
        "Translate the format to python-understandable."
        return dt_format.replace('YYYY', '%Y').replace('MM','%m').replace('DD','%d').replace('hh', '%H').replace('mm', '%M').replace('ss','%S')
    
    # Add 0 as prefix of numbers 
    def __Add_zeroprefix(self, n, amount): 
        "For specific usage. Ex: n=3, amount=8 then return 008"
        num_complement = n - len(str(amount))
        if num_complement == 0 : 
            return str(amount)
        else:
            return '0'+self.__Add_zeroprefix(n-1, amount) 
            
    # Sort queue in specific form: queue would be like [ [t1(1),fs1,fs2,fs3], [t1(2),fs1], [t2(2), fs2], [t3(2), fs3]  ]
    def __Queue_sort(self, queue) : 
        "Sort queue according to datetime. Ex: queue = [[t1(1),fs1],[t2(1),fs2],[t1(2),fs1],[t1(2),fs2]] -> [[t1(1),fs1],[t2(1),fs2],[t1(2),fs1,fs2]]"
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
    
    # Sort queue in specific form: queue would be like [ [t1_chk(1), [t1(1),fs1], [t2(1),fs2], [t3(1),fs3] ], [t1_chk(2),[t1(2),fs1] ], [t2_chk(2), [t2(2),fs2] ], [t3_chk(2), [t3(2), fs3] ]  ]
    def __Queue_sort2(self, queue) : 
        "Sort queue according to datetime. Ex: queue = [ [t1_chk(1), [t1(1),fs1], [t2(1),fs2], [t3(1),fs3] ], [t1_chk(2),[t1(2),fs1] ], [t2_chk(2), [t2(2),fs2] ], [t3_chk(2), [t3(2), fs3] ]  ]"
        tmp_queue = [] 
        queue.sort(key = lambda q: q[0])
        
        tmp_queue.append(queue.pop(0))
        while len(queue) != 0 : 
            tmp = queue.pop(0)  # [t1_chk(2),[t1(2),fs1] ]
            if tmp[0] == tmp_queue[-1][0] :
                tmp_queue[-1].append(tmp[1]) 
            else :
                tmp_queue.append(tmp)
        return tmp_queue
    
    # Calculate next datetime 
    def __Next_datetime(self, s, dt_now):
        "Turn normal format s 'YYYYMMDDhhmmss' to the closet next datetime object from dt_now."
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
    
    # auxiliary function 
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
        "p is like [[level 0 path],[level 1 path],[level 2 path]], then output will be the combinations of each elements in each list in p. For instance, if p is [['a','b'],['5','7']], then return ['a5',a7','b5','b7']."
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
        "Use folder_struct as input, return a list containing all possible paths."
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
        "Read in file structure setting ini file."
        # Read in ini file 
        self.__file_struct = self.__Read_ini(self.__ini_folder + '/file_struct.ini') 
        return 
    
    def __Read_folder_struct(self): 
        "Read in folder structure setting ini file."
        self.__folder_struct = self.__Read_ini(self.__ini_folder + '/folder_struct.ini')
        return 
    
    def __Read_manam_struct(self): 
        "Read in manam schedule setting ini file.(not necessary)"
        if os.path.isfile(self.__ini_folder + 'manam_setting.ini') == False : 
            print('(info) There is no manam ini file found.')
        else : 
            self.__manam_struct = self.__Read_ini(self.__ini_folder + '/manam_setting.ini') 
        return 
        
    # Sleep sec by sec
    def __sleep(self,seconds): 
        "Sleep second by second."
        time.sleep(seconds%1)
        for i in range(0,int(seconds)): 
            time.sleep(1) 
        return 
    
    # Read in ini-typed file with specific ini structure
    def __Read_ini(self,filename): 
        "Read in specific format ini file. The format is defined in Design.txt."
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
                    if tmp_type == '(string)' or tmp_type == '(datetime)' or tmp_type == '(filename structure)' or tmp_type == '(sequence)': 
                        for i in range(1,len(tmp_s)):
                            tmp_d[tmp_title][tmp_attr]['content'].append(tmp_s[i]) 
                    else : 
                        for i in range(1,len(tmp_s)):
                            tmp_d[tmp_title][tmp_attr]['content'].append(int(tmp_s[i])) 
                # update s
                s = fr.readline().strip('\n') 
        return tmp_d
    
    # Public function
    # for debug 
    def SHOW(self): 
        "This function will return self.__file_struct and self.__folder_struct, which is for debug use."
        return self.__manam_struct, self.__file_struct, self.__folder_struct 

#---
#   Following is for data check. 
#     there are 3 methods: 
#       - Keep-Checking 
#       V Check-Once each time 
#       - inotify
#---
    def Periodical_Check(self): 
        # Comment
        "Periodicall check each file structure accroding to their generating period and related parameters."
        
        # Parameters 
        start_multiple = 0      # how many multiple period of start check time from data time 
        stop_multiple = 0.8     # how many multople period of stop check time from data time 
        period_multiple = stop_multiple - start_multiple        
        
        # for convenience 
        tmp_fs = self.__file_struct
        tmp_fsk = self.__folder_struct    
        
        # Make a queue for file structures: [ [t1_chk(1), [t1(1),fs1], [t2(1),fs2], [t3(1),fs3] ], [t1_chk(2),[t1(2),fs1] ], [t2_chk(2), [t2(2),fs2] ], [t3_chk(2), [t3(2), fs3] ]  ]
        self.__Log_data_chk('(Initialize) Perparing queue where contains the following datetime to check data...') 
        chk_point_queue = []
        dt_now = dt.now(tz.utc) 
        for key in tmp_fs.keys() : 
            tmp_gdf = tmp_fs[key]['generating datetime format']['content'][0]
            tmp_gp = tmp_fs[key]['generating period']['content'] 
            tmp_last_dt1 = self.__N_next_datetime(tmp_gp, tmp_gdf, dt_now, n=0+start_multiple)
            tmp_first = self.__N_next_datetime(tmp_gp, tmp_gdf, tmp_last_dt1, n=period_multiple)
            tmp_last_dt2 = self.__N_next_datetime(tmp_gp, tmp_gdf, dt_now, n=1+start_multiple)
            tmp_second = self.__N_next_datetime(tmp_gp, tmp_gdf, tmp_last_dt2, n=period_multiple)
            chk_point_queue.append([tmp_first, [tmp_last_dt1, key]]) 
            chk_point_queue.append([tmp_second, [tmp_last_dt2, key]])
        chk_point_queue = self.__Queue_sort2(chk_point_queue)
        
        self.__Log_data_chk('(debug) queue:', chk_point_queue)
        
        self.__Log_data_chk('(Initialize) Following datetime and corresponding file structures would be: ')
        for d in chk_point_queue: 
            self.__Log_data_chk('At', d[0].strftime('%Y-%m-%d %H:%M:%S'), 'going to check:')
            for tmp_i in range(1,len(d)):
                self.__Log_data_chk(d[tmp_i][0].strftime('%Y%m%d_%H%M%S'), d[tmp_i][1])
            self.__Log_data_chk() 
            
        # Sleep to the first datetime in queue 
        tmp_ele = chk_point_queue.pop(0)  # list of file structures 
        tmp_chk_dt = tmp_ele.pop(0) # check datetime 
        tmp_file_dt = tmp_ele # file datetime 
        await_time_sec = ( tmp_chk_dt - dt.now(tz.utc) ).total_seconds()
        if await_time_sec < 0 : 
            await_time_sec = 0 
        self.__Log_data_chk('(Initialize) Going to sleep for', await_time_sec, 'seconds...')
        self.__sleep(await_time_sec) 
        
        # Main loop  
        while True: 
        # Check if someone(folder structure) needs the file structure(s) 
        # If yes -> do things, if no -> pass
            self.__Log_data_chk() 
            self.__Log_data_chk('(Info) Time up. Start to find who needs ', tmp_ele)
            tmp_fullpath_dict = {}      # this dict is designed to be like {fsk1(filesturcture key): {fs3: [fullpath list]}, fsk2: {fs1:[...],fs2:[...]},... }
            for fs_pair in tmp_ele : 
                fs = fs_pair[1] 
                tmp_file_dt0 = fs_pair[0]
                tmp_fsk_list = []       # for the use of confirming fs is needed and then generate fclist and pathlist for save resource of computer
                for fsk in tmp_fsk.keys(): 
                    if fs in tmp_fsk[fsk]['filename structure']['content']: 
                        self.__Log_data_chk('(Run) Found in ' + fsk + ', ' + fs + ' is needed.' )
                        tmp_fsk_list.append(fsk)
        # Update queue 
                        self.__Log_data_chk('(Info) Start to refresh datetime queue...')
                        tmp_gdf = tmp_fs[fs]['generating datetime format']['content'][0] 
                        tmp_gp = tmp_fs[fs]['generating period']['content'] 
                        tmp_file_dt = self.__N_next_datetime(tmp_gp, tmp_gdf, tmp_file_dt0, n=2+start_multiple)
                        tmp_chk_dt = self.__N_next_datetime(tmp_gp, tmp_gdf, tmp_file_dt, n=period_multiple)
                        chk_point_queue.append([tmp_chk_dt, [tmp_file_dt, fs]])
                        chk_point_queue = self.__Queue_sort2(chk_point_queue)
                        
                if tmp_fsk_list == [] : 
                    self.__Log_data_chk('(Info) ', fs,' is not needed. Skip.')
                    continue 
        # Combine folder structure and file structure to get the full path of target files, make them a list 
                else : 
                    tmp_pathlist = []   # combination dir path list according to folder structure 
                    tmp_fclist = self.__File_create(fs, tmp_file_dt0)     # combination file list according to file structure 
                    for fsk in tmp_fsk_list : 
                        tmp_pathlist = self.__Dir_path_generator(fsk, tmp_file_dt0)
                        if tmp_fullpath_dict.get(fsk) == None: 
                            tmp_fullpath_dict[fsk] = {} 
                        tmp_fullpath_dict[fsk][fs] = self.__Path_generator([tmp_pathlist, tmp_fclist])  # combination full path list for each file to be generated 
                        self.__Log_data_chk('(debug) First 7 fullpath list', fsk, fs, ':')
                        if len(tmp_fullpath_dict[fsk][fs]) >= 7 : 
                            tmp_index_max = 7 
                        else : 
                            tmp_index_max = len(tmp_fullpath_dict[fsk][fs])
                        for tmp_i in range(0,tmp_index_max):
                            self.__Log_data_chk('(debug)',tmp_fullpath_dict[fsk][fs][tmp_i])
        
        # Check every full path to get their status 
        ## See if it exists, its size, its mtime 
            status_dict = {} 
            for fsk in tmp_fullpath_dict.keys(): 
                status_dict[fsk] = {} 
                for fs in tmp_fullpath_dict[fsk].keys(): 
                    status_dict[fsk][fs] = {} 
                    for file in tmp_fullpath_dict[fsk][fs]: 
                        status_dict[fsk][fs][file] = self.__Record_status(file=file)
        
        # Decide logfile name, related to datetime 
            logfile = self.__logdir + dt.now(tz.utc).strftime('%Y%m%d_%H%M%S.object') 
            
        # Output them as an object 
            self.__Log_data_chk('(Info) Output to ' + logfile + ' now. ') 
            with open(file=logfile , mode='a') as fa : 
                fa.writelines(self.__Output_object_as_txt(status_dict)) 
            
        # Send them to next station 
            
            
        # Print queue info 
            self.__Log_data_chk('(debug) queue:', chk_point_queue)
            
            self.__Log_data_chk('(Info) Done updating queue. Following datetime and corresponding file structures would be: ')
            for d in chk_point_queue: 
                self.__Log_data_chk(d[0].strftime('%Y-%m-%d %H:%M:%S'))
                for tmp_i in range(1,len(d)):
                    self.__Log_data_chk(d[tmp_i][0].strftime('%Y%m%d_%H%M%S'), d[tmp_i][1])
                self.__Log_data_chk() 
                
        # Sleep to next datetime 
            tmp_ele = chk_point_queue.pop(0)  # list of file structures 
            tmp_chk_dt = tmp_ele.pop(0) # check datetime 
            tmp_file_dt = tmp_ele # file datetime 
            await_time_sec = ( tmp_chk_dt - dt.now(tz.utc) ).total_seconds() 
            if await_time_sec < 0: 
                await_time_sec = 0
            self.__Log_data_chk('(Info) Going to sleep for', await_time_sec, 'seconds...')
            self.__sleep(await_time_sec)
        
        return 

    # N-next datetime 
    def __N_next_datetime (self, period, s, dt_now, n=0):
        "If n=0, return the first datetime has the format s from dt_now. The range includes dt_now."
        tmp_delta = delta(hours=period[0],minutes=period[1],seconds=period[2])
        next_datetime = self.__Next_datetime(s,dt_now) 
        return next_datetime + (n-1) * tmp_delta  

    # Record status of a file 
    def __Record_status(self, file) :
        "Enter full path as file, return a dict. Ex: {'isfile': True, 'size': 123, 'mtime': dt(2020,3,14,5,8,6)}"
        isfile = os.path.isfile(file)
        if isfile == False : 
            size = self.__none_size
            mtime = self.__none_dt 
        else : 
            size = os.stat(file).st_size 
            mtime = dt.fromtimestamp(os.stat(file).st_mtime, tz=tz.utc) 
        return {'isfile': isfile, 'size': size, 'mtime': mtime}

    # Output a thing as an generalized text-formed object 
    def __Output_object_as_txt(self, d, level=0) : 
        # Use 
        "Output a thing as an generalized text-formed object, which has the form like ---<class 'int'>::28. --- means it is 3rd level in the dict, <class 'int'> its type, 28 its value."
        # Decide how many prefix '-' would this level have 
        this_level_prefix = ''
        for i in range(0,level): 
            this_level_prefix += '-'
        # If not dict, return 
        if type(d) != dict : 
            if type(d) == dt : 
                dd = d.strftime('%Y,%m,%d,%H,%M,%S,%f')
                return this_level_prefix + str(type(d)) + '::' + str(dd) + '\n'
            else : 
                return this_level_prefix + str(type(d)) + '::' + str(d) + '\n'
        # Recursive call 
        s = '' 
        for key in d.keys() : 
            s += this_level_prefix + str(type(key)) + '::' + str(key) +'\n'
            s += self.__Output_object_as_txt(d[key], level+1)
        return s 
        
    # Input an generalized text-formed object as a thing
    def __Input_txt_as_object(self, s): 
        # Use 
        "Input a generalized text-formed object, transform it into a dictinary "
        # Decide it is a dict or not (if only one single line -> not dict)
        tmp_s = s.split('\n')
        tmp_s.remove('')
        if len(tmp_s) == 1:     # it's not a dict 
            return self.__Str_translate(tmp_s[0])
        else:   # it's a dict and analyze the text-formed object 
            d = {} 
            value_list = []
            last_level = -1
            for i in range(0,len(tmp_s)):
                # decide which level, what value 
                tmp_str = tmp_s[i].split('::')
                level = tmp_str[0].count('-') 
                value = self.__Str_translate(tmp_s[i][level:]) 
                if level > last_level:      # collect hierarchical value 
                    value_list.append(value) 
                elif level < last_level : 
                    # fill them into d 
                    d = self.__List2Dict(value_list, d) 
                    # update value_list 
                    n = last_level - level + 1 
                    for tmp_n in range(0,n): 
                        value_list.pop()
                    value_list.append(value)
                last_level = level 
            # fill them into d finally 
            d = self.__List2Dict(value_list, d) 
        return d 
                
    # (auxiliary) Turn list value into dict key,value hierarchy 
    def __List2Dict(self, l, d):
        "len(l) must be no less than 2. Ex: l = [1,2,3] and d = {1:{3:4}}, then return {1:{2:3,3:4}}" 
        if len(l) == 2: 
            d[l[0]] = l[1] 
        else : 
            if d.get(l[0]) == None: 
                tmp_l = l.copy() 
                tmp_l.pop(0)
                tmp_d = {} 
                d[l[0]] = self.__List2Dict(tmp_l, tmp_d)
            else : 
                tmp_l = l.copy() 
                tmp_l.pop(0)
                tmp_d = d[l[0]]
                d[l[0]] = self.__List2Dict(tmp_l, tmp_d) 
        return d 
        
    # Analyze a text-formed string 
    def __Str_translate(self, s): 
        # Use 
        "Translate a generalized text-formed string into a corresponding object. Ex: <class 'int'>::589 will return int(589)."
        # All types supported is shown below 
        tmp_s = s.split('::') 
        if tmp_s[0] == "<class 'datetime.datetime'>" : 
            tmp_dt = tmp_s[1].split(',')
            tmp_dt = [int(i) for i in tmp_dt] 
            return dt(tmp_dt[0],tmp_dt[1],tmp_dt[2],tmp_dt[3],tmp_dt[4],tmp_dt[5],tmp_dt[6],tzinfo=tz.utc) 
        elif tmp_s[0] == "<class 'bool'>" : 
            if tmp_s[1] == 'True': 
                return True 
            elif tmp_s[1] == 'False' : 
                return False 
        elif tmp_s[0] == "<class 'int'>" : 
            return int(tmp_s[1])
        elif tmp_s[0] == "<class 'str'>" : 
            return tmp_s[1] 
        elif tmp_s[0] == "<class 'list'>" :     # not support recursive list like [1,2,3,[4],5,6]
            tmp_list = tmp_s[1].strip('[]') 
            tmp_list = tmp_list.split(',')
            tmp_llll = [] 
            for i in range(0,len(tmp_list)): 
                if tmp_list[i].startswith("'") and tmp_list[i].endswith("'"): # it's a string 
                    tmp_llll.append(tmp_list[i].strip("'")) 
                elif tmp_list[i] == 'True':     # it is a bool 
                    tmp_llll.append(True)
                elif tmp_list[i] == 'False': 
                    tmp_llll.append(False)
                else:   # it's a number 
                    tmp_llll.append(int(tmp_list[i]))
            return tmp_llll 
###     General use     ####
    # Log and Print debug message 
    def __Log_data_chk(self, *s ,sep=' ', end='\n') : 
        "Print and log debug messages."
        now_ts = dt.now(tz.utc).strftime('%Y-%m-%d %H:%M:%S')
        print('##[' + now_ts + ']## ',end = '')
        for i in range(0,len(s)): 
            print(s[i],sep=sep,end=end)
        with open(file=self.__debug_log_data_check, mode='a') as fa : 
            fa.write('##[' + now_ts + ']## ')
            for i in range(0,len(s)):
                fa.write(str(s[i]))
                if i != len(s) - 1: 
                    fa.write(sep)
            fa.write(end)
        self.__Purge(self.__debug_log_data_check)
        return 
    def __Log_data_gen(self, *s ,sep=' ', end='\n') : 
        "Print and log debug messages."
        now_ts = dt.now(tz.utc).strftime('%Y-%m-%d %H:%M:%S')
        print('##[' + now_ts + ']## ',end = '')
        for i in range(0,len(s)): 
            print(s[i],sep=sep,end=end)
        with open(file=self.__debug_log_data_gen, mode='a') as fa : 
            fa.write('##[' + now_ts + ']## ')
            for i in range(0,len(s)):
                fa.write(str(s[i]))
                if i != len(s) - 1: 
                    fa.write(sep)
            fa.write(end)
        self.__Purge(self.__debug_log_data_gen)
        return 
        
    # Purge debug log
    def __Purge(self, file, max_size=10, max_file_num=10) : 
        "Once debug log file reaches max_size MB(default = 10MB), rename it to debug.log.(number).old"
		if os.stat(file).st_size > max_size*1024*1024: 
			for i in range(1, max_file_num):
				if os.path.isfile(file+'.'+str(max_file_num-i)+'.old') == True : 
					os.rename(file+'.'+str(max_file_num-i)+'.old', file+'.'+str(max_file_num-i+1)+'.old')
			os.rename(file, file+'.1.old')
        return 

### Analyze manam schedule ###
    # Read manam schedule and Output a dictionary 
    def __Manam2Dict(self, manam_file, manam_type="GK2A") : 
        "Analyze manam schedule and return a dictionary."
        if manam_type == 'GK2A':
            d = {'manam': {} , 'Update': {}, 'calibration': {} } 
            s_tmp_flag = False 
            c_tmp_flag = False 
            # Meta descriptions (1st paragraph)
            with open (file=manam_file, mode='r', encoding='utf-8') as fr: 
                s = fr.readline()
                while (s != '') :
                    s = s.strip()   # remove tail and head empty 
                    # set case 1
                    if s.startswith('TIME(UTC)') : 
                        s_tmp_flag = True   
                        s = fr.readline()
                        continue 
                    # end case 1 and case 2 
                    elif s == '' : 
                        s_tmp_flag = False
                        c_tmp_flag = False 
                    # set case 2 
                    elif s.startswith('GAIN'): 
                        c_tmp_flag = True 
                        s = fr.readline()
                        continue 
                    
                    # case 0 : update datetime 
                    if s.startswith('UPDATE') :
                        d['Update'] = tmp = s.split(' ')[1]
                    # case 1 : extract all manam info out 
                    # Ex: d[manam] = {RR: {001:{start:000306, end: 000319, dissemination: True} } ...}
                    elif s_tmp_flag == True : 
                        tmp = s.split('\t')  
                        tmp = self.__Remove_empty_element(tmp)
                        tmp1 = tmp[0].split('-')
                        start_tm = tmp1[0]
                        end_tm = tmp1[1]
                        tmp2 = self.__Str_seperate(tmp[1])
                        product_name = tmp2[0]
                        sequence = tmp2[1]
                        dissemination = tmp[-1]
                        if d['manam'].get(product_name) == None : 
                            d['manam'][product_name] = {} 
                        if d['manam'][product_name].get(sequence) == None: 
                            d['manam'][product_name][sequence] = {} 
                        d['manam'][product_name][sequence] = {'start_tm': start_tm, 'end_tm': end_tm, 'dissemination': dissemination}
                    # case 2 : extract all calibration info out 
                    # Ex: d[calibration] = {channel: {1,2,3,4,5,6,...} }
                    elif c_tmp_flag == True : 
                        tmp = s.split('\t')
                        d['calibration'][tmp[0]] = tmp[1:]
                    s = fr.readline()
        elif manam_type == 'Himawari-8' : 
            pass 
        elif manam_type == 'FY2F' or manam_type == 'FY2G' or manam_type == 'FY2H': 
            pass
        return d 
        
    # Remove excessive empty or space 
    def __Remove_empty_element(self, l): 
        "Remove empty elements '' and ' ' from target list. "
        while '' in l: 
            l.remove('')
        while ' ' in l:
            l.remove(' ')
        return l 
        
    # Seperate digit alphabet
    def __Str_seperate(self, s, pattern_str='([a-zA-Z]+)([0-9]+)'): 
        "Seperate s with specific pattern. Ex: pattern_str = '([a-zA-Z]+)([0-9]+)' and s = 'jiqo903', return ['jiqo', '903'] list."
        m = re.compile(pattern_str)
        return list(m.match(s).groups()) 
        
        
        
        
        



















