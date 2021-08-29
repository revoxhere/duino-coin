#!/usr/bin/env python3
"""
Duino-Coin Official AVR Miner v2.7 © MIT licensed
https://duinocoin.com
https://github.com/revoxhere/duino-coin
Duino-Coin Team & Community 2019-2021

Since 29.08.2021 this software is no longer open source
"""
import sys #line:9
from configparser import ConfigParser #line:10
from datetime import datetime #line:11
from json import load as jsonload #line:12
from locale import LC_ALL ,getdefaultlocale ,getlocale ,setlocale #line:13
from os import _exit ,execl ,mkdir #line:14
from os import name as osname #line:15
from os import path #line:16
from os import system as ossystem #line:17
from platform import machine as osprocessor #line:18
from pathlib import Path #line:19
from platform import system #line:20
from re import sub #line:21
from signal import SIGINT ,signal #line:22
from socket import socket #line:23
from subprocess import DEVNULL ,Popen ,check_call ,call #line:24
from threading import Thread as thrThread #line:25
from threading import Lock #line:26
from time import ctime ,sleep ,strptime ,time #line:27
from statistics import mean #line:28
from random import choice #line:29
import select #line:30
import pip #line:31
def install (O000OOOOOOOO00O0O ):#line:34
    try :#line:35
        pip .main (["install",O000OOOOOOOO00O0O ])#line:36
    except AttributeError :#line:37
        check_call ([sys .executable ,'-m','pip','install',O000OOOOOOOO00O0O ])#line:38
    call ([sys .executable ,__file__ ])#line:40
def now ():#line:43
    return datetime .now ()#line:45
try :#line:48
    from serial import Serial #line:50
    import serial .tools .list_ports #line:51
except ModuleNotFoundError :#line:52
    print (now ().strftime ('%H:%M:%S ')+'Pyserial is not installed. '+'Miner will try to install it. '+'If it fails, please manually install "pyserial" python3 package.'+'\nIf you can\'t install it, use the Minimal-PC_Miner.')#line:58
    install ('pyserial')#line:59
try :#line:61
    import requests #line:63
except ModuleNotFoundError :#line:64
    print (now ().strftime ('%H:%M:%S ')+'Requests is not installed. '+'Miner will try to install it. '+'If it fails, please manually install "requests" python3 package.'+'\nIf you can\'t install it, use the Minimal-PC_Miner.')#line:70
    install ('requests')#line:71
try :#line:73
    from colorama import Back ,Fore ,Style ,init #line:75
except ModuleNotFoundError :#line:76
    print (now ().strftime ('%H:%M:%S ')+'Colorama is not installed. '+'Miner will try to install it. '+'If it fails, please manually install "colorama" python3 package.'+'\nIf you can\'t install it, use the Minimal-PC_Miner.')#line:82
    install ('colorama')#line:83
try :#line:85
    from pypresence import Presence #line:87
except ModuleNotFoundError :#line:88
    print (now ().strftime ('%H:%M:%S ')+'Pypresence is not installed. '+'Miner will try to install it. '+'If it fails, please manually install "pypresence" python3 package.'+'\nIf you can\'t install it, use the Minimal-PC_Miner.')#line:94
    install ('pypresence')#line:95
MINER_VER ='2.7'#line:98
SOC_TIMEOUT =45 #line:99
PERIODIC_REPORT_TIME =60 #line:100
AVR_TIMEOUT =4 #line:101
BAUDRATE =115200 #line:102
RESOURCES_DIR ='AVRMiner_'+str (MINER_VER )+'_resources'#line:103
shares =[0 ,0 ]#line:104
hashrate_mean =[]#line:105
ping_mean =[]#line:106
diff =0 #line:107
shuffle_ports ="y"#line:108
donator_running =False #line:109
job =''#line:110
debug ='n'#line:111
discord_presence ='y'#line:112
rig_identifier ='None'#line:113
donation_level =0 #line:114
hashrate =0 #line:115
config =ConfigParser ()#line:116
thread_lock =Lock ()#line:117
mining_start_time =time ()#line:118
if not path .exists (RESOURCES_DIR ):#line:121
    mkdir (RESOURCES_DIR )#line:122
if not Path (RESOURCES_DIR +'/langs.json').is_file ():#line:125
    url =('https://raw.githubusercontent.com/'+'revoxhere/'+'duino-coin/master/Resources/'+'AVR_Miner_langs.json')#line:129
    r =requests .get (url )#line:130
    with open (RESOURCES_DIR +'/langs.json','wb')as f :#line:131
        f .write (r .content )#line:132
with open (RESOURCES_DIR +'/langs.json','r',encoding ='utf8')as lang_file :#line:135
    lang_file =jsonload (lang_file )#line:136
if system ()=='Darwin':#line:139
    if getlocale ()[0 ]is None :#line:140
        setlocale (LC_ALL ,'en_US.UTF-8')#line:141
try :#line:144
    if not Path (RESOURCES_DIR +'/Miner_config.cfg').is_file ():#line:145
        locale =getdefaultlocale ()[0 ]#line:146
        if locale .startswith ('es'):#line:147
            lang ='spanish'#line:148
        elif locale .startswith ('sk'):#line:149
            lang ='slovak'#line:150
        elif locale .startswith ('ru'):#line:151
            lang ='russian'#line:152
        elif locale .startswith ('pl'):#line:153
            lang ='polish'#line:154
        elif locale .startswith ('fr'):#line:155
            lang ='french'#line:156
        elif locale .startswith ('tr'):#line:157
            lang ='turkish'#line:158
        elif locale .startswith ('pt'):#line:159
            lang ='portuguese'#line:160
        elif locale .startswith ('zh'):#line:161
            lang ='chinese_simplified'#line:162
        elif locale .startswith ('th'):#line:163
            lang ='thai'#line:164
        else :#line:165
            lang ='english'#line:166
    else :#line:167
        try :#line:168
            config .read (RESOURCES_DIR +'/Miner_config.cfg')#line:170
            lang =config ['Duino-Coin-AVR-Miner']['language']#line:171
        except Exception :#line:172
            lang ='english'#line:174
except :#line:175
    lang ='english'#line:176
def get_string (OOO000OO0OOO00O00 :str ):#line:179
    if OOO000OO0OOO00O00 in lang_file [lang ]:#line:181
        return lang_file [lang ][OOO000OO0OOO00O00 ]#line:182
    elif OOO000OO0OOO00O00 in lang_file ['english']:#line:183
        return lang_file ['english'][OOO000OO0OOO00O00 ]#line:184
    else :#line:185
        return ' String not found: '+OOO000OO0OOO00O00 #line:186
def get_prefix (OOO0OOO0O00O0O000 :int ):#line:189
    if int (OOO0OOO0O00O0O000 )>=1000000000 :#line:190
        OOO0OOO0O00O0O000 =str (round (OOO0OOO0O00O0O000 /1000000000 ))+"G"#line:191
    elif int (OOO0OOO0O00O0O000 )>=1000000 :#line:192
        OOO0OOO0O00O0O000 =str (round (OOO0OOO0O00O0O000 /1000000 ))+"M"#line:193
    elif int (OOO0OOO0O00O0O000 )>=1000 :#line:194
        OOO0OOO0O00O0O000 =str (round (OOO0OOO0O00O0O000 /1000 ))+"k"#line:195
    return str (OOO0OOO0O00O0O000 )#line:196
def debug_output (OOO00OO00OO0O0OOO :str ):#line:199
    if debug =='y':#line:201
        print (Style .RESET_ALL +now ().strftime (Style .DIM +'%H:%M:%S.%f ')+'DEBUG: '+str (OOO00OO00OO0O0OOO ))#line:206
def title (O000OOO0O000OO0OO :str ):#line:209
    if osname =='nt':#line:211
        ossystem ('title '+O000OOO0O000OO0OO )#line:213
    else :#line:214
        print ('\33]0;'+O000OOO0O000OO0OO +'\a',end ='')#line:216
        sys .stdout .flush ()#line:217
def handler (OOO0OOOOO0OOO0O00 ,O000000OO0O0O00O0 ):#line:220
    pretty_print ('sys0',get_string ('sigint_detected')+Style .NORMAL +Fore .RESET +get_string ('goodbye'),'warning')#line:228
    try :#line:229
        socket .close ()#line:231
    except Exception :#line:232
        pass #line:233
    _exit (0 )#line:234
signal (SIGINT ,handler )#line:238
def load_config ():#line:241
    global username #line:243
    global donation_level #line:244
    global avrport #line:245
    global debug #line:246
    global rig_identifier #line:247
    global discord_presence #line:248
    global shuffle_ports #line:249
    global SOC_TIMEOUT #line:250
    global AVR_TIMEOUT #line:251
    global PERIODIC_REPORT_TIME #line:252
    if not Path (str (RESOURCES_DIR )+'/Miner_config.cfg').is_file ():#line:255
        print (Style .BRIGHT +get_string ('basic_config_tool')+RESOURCES_DIR +get_string ('edit_config_file_warning'))#line:260
        print (Style .RESET_ALL +get_string ('dont_have_account')+Fore .YELLOW +get_string ('wallet')+Fore .RESET +get_string ('register_warning'))#line:268
        username =input (Style .RESET_ALL +Fore .YELLOW +get_string ('ask_username')+Fore .RESET +Style .BRIGHT )#line:275
        print (Style .RESET_ALL +Fore .YELLOW +get_string ('ports_message'))#line:279
        OOOO00O0OOOO0OO0O =serial .tools .list_ports .comports (include_links =True )#line:280
        for OOOO00OOOOO00O000 in OOOO00O0OOOO0OO0O :#line:281
            print (Style .RESET_ALL +Style .BRIGHT +Fore .RESET +'  '+str (OOOO00OOOOO00O000 ))#line:286
        print (Style .RESET_ALL +Fore .YELLOW +get_string ('ports_notice'))#line:289
        O0OO00OO0O0O00OO0 =[]#line:291
        for OOOO00OOOOO00O000 in OOOO00O0OOOO0OO0O :#line:292
            O0OO00OO0O0O00OO0 .append (OOOO00OOOOO00O000 .device )#line:293
        avrport =''#line:295
        while True :#line:296
            O00O0000OO00000OO =input (Style .RESET_ALL +Fore .YELLOW +get_string ('ask_avrport')+Fore .RESET +Style .BRIGHT )#line:302
            if O00O0000OO00000OO in O0OO00OO0O0O00OO0 :#line:304
                avrport +=O00O0000OO00000OO #line:305
                O0O00000000O00OO0 =input (Style .RESET_ALL +Fore .YELLOW +get_string ('ask_anotherport')+Fore .RESET +Style .BRIGHT )#line:311
                if O0O00000000O00OO0 =='y'or O0O00000000O00OO0 =='Y':#line:313
                    avrport +=','#line:314
                else :#line:315
                    break #line:316
            else :#line:317
                print (Style .RESET_ALL +Fore .RED +'Please enter a valid COM port from the list above')#line:320
        rig_identifier =input (Style .RESET_ALL +Fore .YELLOW +get_string ('ask_rig_identifier')+Fore .RESET +Style .BRIGHT )#line:327
        if rig_identifier =='y'or rig_identifier =='Y':#line:328
            rig_identifier =input (Style .RESET_ALL +Fore .YELLOW +get_string ('ask_rig_name')+Fore .RESET +Style .BRIGHT )#line:334
        else :#line:335
            rig_identifier ='None'#line:336
        donation_level ='0'#line:338
        donation_level =sub (r'\D','',donation_level )#line:348
        if donation_level =='':#line:349
            donation_level =1 #line:350
        if float (donation_level )>int (5 ):#line:351
            donation_level =5 #line:352
        if float (donation_level )<int (0 ):#line:353
            donation_level =0 #line:354
        config ['Duino-Coin-AVR-Miner']={'username':username ,'avrport':avrport ,'donate':donation_level ,'language':lang ,'identifier':rig_identifier ,'debug':'n',"soc_timeout":45 ,"avr_timeout":4 ,"discord_presence":"y","periodic_report":60 ,"shuffle_ports":"y"}#line:369
        with open (str (RESOURCES_DIR )+'/Miner_config.cfg','w')as O00O0O00OOO00OO0O :#line:373
            config .write (O00O0O00OOO00OO0O )#line:374
        avrport =avrport .split (',')#line:376
        print (Style .RESET_ALL +get_string ('config_saved'))#line:377
    else :#line:379
        config .read (str (RESOURCES_DIR )+'/Miner_config.cfg')#line:380
        username =config ['Duino-Coin-AVR-Miner']['username']#line:381
        avrport =config ['Duino-Coin-AVR-Miner']['avrport']#line:382
        avrport =avrport .replace (" ","").split (',')#line:383
        donation_level =config ['Duino-Coin-AVR-Miner']['donate']#line:384
        debug =config ['Duino-Coin-AVR-Miner']['debug']#line:385
        rig_identifier =config ['Duino-Coin-AVR-Miner']['identifier']#line:386
        SOC_TIMEOUT =int (config ["Duino-Coin-AVR-Miner"]["soc_timeout"])#line:387
        AVR_TIMEOUT =float (config ["Duino-Coin-AVR-Miner"]["avr_timeout"])#line:388
        discord_presence =config ["Duino-Coin-AVR-Miner"]["discord_presence"]#line:389
        shuffle_ports =config ["Duino-Coin-AVR-Miner"]["shuffle_ports"]#line:390
        PERIODIC_REPORT_TIME =int (config ["Duino-Coin-AVR-Miner"]["periodic_report"])#line:392
def greeting ():#line:395
    global greeting #line:397
    print (Style .RESET_ALL )#line:398
    O000OOOOO000000OO =strptime (ctime (time ())).tm_hour #line:400
    if O000OOOOO000000OO <12 :#line:402
        greeting =get_string ('greeting_morning')#line:403
    elif O000OOOOO000000OO ==12 :#line:404
        greeting =get_string ('greeting_noon')#line:405
    elif O000OOOOO000000OO >12 and O000OOOOO000000OO <18 :#line:406
        greeting =get_string ('greeting_afternoon')#line:407
    elif O000OOOOO000000OO >=18 :#line:408
        greeting =get_string ('greeting_evening')#line:409
    else :#line:410
        greeting =get_string ('greeting_back')#line:411
    print (Style .DIM +Fore .MAGENTA +' ‖ '+Fore .YELLOW +Style .BRIGHT +get_string ('banner')+Style .RESET_ALL +Fore .MAGENTA +' (v'+str (MINER_VER )+') '+Fore .RESET +'2019-2021')#line:427
    print (Style .DIM +Fore .MAGENTA +' ‖ '+Style .NORMAL +Fore .MAGENTA +'https://github.com/revoxhere/duino-coin')#line:435
    if lang !="english":#line:437
        print (Style .DIM +Fore .MAGENTA +" ‖ "+Style .NORMAL +Fore .RESET +lang .capitalize ()+" translation: "+Fore .MAGENTA +get_string ("translation_autor"))#line:447
    print (Style .DIM +Fore .MAGENTA +' ‖ '+Style .NORMAL +Fore .RESET +get_string ('avr_on_port')+Style .BRIGHT +Fore .YELLOW +' '.join (avrport ))#line:458
    print (Style .DIM +Fore .MAGENTA +' ‖ '+Style .NORMAL +Fore .RESET +get_string ('algorithm')+Style .BRIGHT +Fore .YELLOW +'DUCO-S1A ⚙ AVR diff')#line:480
    if rig_identifier !="None":#line:482
        print (Style .DIM +Fore .MAGENTA +' ‖ '+Style .NORMAL +Fore .RESET +get_string ('rig_identifier')+Style .BRIGHT +Fore .YELLOW +rig_identifier )#line:492
    print (Style .DIM +Fore .MAGENTA +' ‖ '+Style .NORMAL +Fore .RESET +str (greeting )+', '+Style .BRIGHT +Fore .YELLOW +str (username )+'!\n')#line:505
def init_rich_presence ():#line:508
    global RPC #line:510
    try :#line:511
        RPC =Presence (808056068113563701 )#line:512
        RPC .connect ()#line:513
        debug_output ('Discord rich presence initialized')#line:514
    except Exception :#line:515
        pass #line:517
def update_rich_presence ():#line:520
    OO00OOO0O0O00O000 =int (time ())#line:522
    while True :#line:523
        try :#line:524
            RPC .update (details ='Hashrate: '+str (round (hashrate ))+' H/s',start =OO00OOO0O0O00O000 ,state ='Acc. shares: '+str (shares [0 ])+'/'+str (shares [0 ]+shares [1 ]),large_image ='ducol',large_text ='Duino-Coin, '+'a coin that can be mined with almost everything, '+'including AVR boards',buttons =[{'label':'Learn more','url':'https://duinocoin.com'},{'label':'Discord Server','url':'https://discord.gg/k48Ht5y'}])#line:540
        except Exception :#line:541
            pass #line:543
        sleep (15 )#line:545
def pretty_print (OO0O0O0O0O0O0O000 ,OOOOOO00OOOO0O0OO ,OO00OO000O0O0OOOO ):#line:548
    if OO0O0O0O0O0O0O000 .startswith ('net'):#line:551
        O0000OOO00OO0O000 =Back .BLUE #line:552
    elif OO0O0O0O0O0O0O000 .startswith ('usb'):#line:553
        O0000OOO00OO0O000 =Back .MAGENTA #line:554
    else :#line:555
        O0000OOO00OO0O000 =Back .GREEN #line:556
    if OO00OO000O0O0OOOO =='success':#line:559
        OO00O0O0OO00OO000 =Fore .GREEN #line:560
    elif OO00OO000O0O0OOOO =='warning':#line:561
        OO00O0O0OO00OO000 =Fore .YELLOW #line:562
    else :#line:563
        OO00O0O0OO00OO000 =Fore .RED #line:564
    with thread_lock :#line:566
        print (Style .RESET_ALL +Fore .WHITE +now ().strftime (Style .DIM +'%H:%M:%S ')+Style .BRIGHT +O0000OOO00OO0O000 +' '+OO0O0O0O0O0O0O000 +' '+Back .RESET +OO00O0O0OO00OO000 +Style .BRIGHT +OOOOOO00OOOO0O0OO +Style .NORMAL +Fore .RESET )#line:580
def mine_avr (O0OOOO00OOO00OOO0 ,O0O0O00O00OO0O0O0 ):#line:583
    global hashrate #line:584
    O00000O0O00000000 = "000"
    OO00OO0OO0O00O00O =time ()#line:586
    OOO0OOOO0OO0OOOO0 =0 #line:587
    OOO0OOO0OOO00OO00 =0 #line:588
    while True :#line:589
        try :#line:590
            while True :#line:591
                try :#line:592
                    debug_output ('Connecting to '+str (NODE_ADDRESS +":"+str (NODE_PORT )))#line:595
                    O0O000O00000O0O00 =socket ()#line:596
                    O0O000O00000O0O00 .connect ((str (NODE_ADDRESS ),int (NODE_PORT )))#line:597
                    O0O000O00000O0O00 .settimeout (SOC_TIMEOUT )#line:598
                    O00O0O000OO000O00 =O0O000O00000O0O00 .recv (100 ).decode ()#line:599
                    if O0O0O00O00OO0O0O0 ==0 :#line:601
                        if float (O00O0O000OO000O00 )<=float (MINER_VER ):#line:602
                            pretty_print ('net0',get_string ('connected')+Style .NORMAL +Fore .RESET +get_string ('connected_server')+str (O00O0O000OO000O00 )+")",'success')#line:611
                        else :#line:612
                            pretty_print ('sys0',' Miner is outdated (v'+MINER_VER +') -'+get_string ('server_is_on_version')+O00O0O000OO000O00 +Style .NORMAL +Fore .RESET +get_string ('update_warning'),'warning')#line:623
                            sleep (10 )#line:624
                        O0O000O00000O0O00 .send (bytes ("MOTD",encoding ="ascii"))#line:626
                        O000OO00O0O000O00 =O0O000O00000O0O00 .recv (1024 ).decode ().rstrip ("\n")#line:627
                        if "\n"in O000OO00O0O000O00 :#line:629
                            O000OO00O0O000O00 =O000OO00O0O000O00 .replace ("\n","\n\t\t")#line:630
                        pretty_print ("net"+str (O0O0O00O00OO0O0O0 )," MOTD: "+Fore .RESET +Style .NORMAL +str (O000OO00O0O000O00 ),"success")#line:637
                    O00000O0O00000000 = O00000O0O00000000 + "ZZ,"
                    break #line:638
                except Exception as OOOOOOOOOOO0OO0O0 :#line:639
                    pretty_print ('net0',get_string ('connecting_error')+Style .NORMAL +' ('+str (OOOOOOOOOOO0OO0O0 )+')','error')#line:647
                    debug_output ('Connection error: '+str (OOOOOOOOOOO0OO0O0 ))#line:648
                    sleep (10 )#line:649
            pretty_print ('sys'+str (''.join (filter (str .isdigit ,O0OOOO00OOO00OOO0 ))),get_string ('mining_start')+Style .NORMAL +Fore .RESET +get_string ('mining_algorithm')+str (O0OOOO00OOO00OOO0 )+')','success')#line:660
            while True :#line:662
                debug_output (O0OOOO00OOO00OOO0 +': requested job from the server')#line:664
                O0O000O00000O0O00 .sendall (bytes (str (O00000O0O00000000 ) +str (username ),encoding ='ascii'))#line:670
                OO00OOO0OO0O00OOO =O0O000O00000O0O00 .recv (128 ).decode ().rstrip ("\n")#line:673
                OO00OOO0OO0O00OOO =OO00OOO0OO0O00OOO .split (",")#line:674
                try :#line:677
                    O0O0OO0OO0OO0000O =int (OO00OOO0OO0O00OOO [2 ])#line:678
                    debug_output (str (''.join (filter (str .isdigit ,O0OOOO00OOO00OOO0 )))+"Correct job received")#line:680
                except :#line:681
                    pretty_print ("usb"+str (''.join (filter (str .isdigit ,O0OOOO00OOO00OOO0 )))," Node message: "+OO00OOO0OO0O00OOO [1 ],"warning")#line:686
                    sleep (3 )#line:687
                while True :#line:689
                    while True :#line:690
                        try :#line:691
                            OO0OOO0O0OOO0O00O .close ()#line:692
                        except :#line:693
                            pass #line:694
                        try :#line:696
                            OO0OOO0O0OOO0O00O =Serial (O0OOOO00OOO00OOO0 ,baudrate =int (BAUDRATE ),timeout =float (AVR_TIMEOUT ))#line:699
                            break #line:700
                        except Exception as OOOOOOOOOOO0OO0O0 :#line:701
                            pretty_print ('usb'+str (''.join (filter (str .isdigit ,O0OOOO00OOO00OOO0 ))),get_string ('board_connection_error')+str (O0OOOO00OOO00OOO0 )+get_string ('board_connection_error2')+Style .NORMAL +Fore .RESET +' (port connection err: '+str (OOOOOOOOOOO0OO0O0 )+')','error')#line:713
                            sleep (10 )#line:714
                    while True :#line:716
                        OOOO0000OO0O000O0 =0 #line:717
                        while True :#line:718
                            if OOOO0000OO0O000O0 >=3 :#line:719
                                break #line:720
                            try :#line:722
                                debug_output (O0OOOO00OOO00OOO0 +': sending job to AVR')#line:723
                                OO0OOO0O0OOO0O00O .write (bytes (str (OO00OOO0OO0O00OOO [0 ]+','+OO00OOO0OO0O00OOO [1 ]+','+OO00OOO0OO0O00OOO [2 ]+','),encoding ='ascii'))#line:730
                                debug_output (O0OOOO00OOO00OOO0 +': reading result from AVR')#line:732
                                O0O0000O0OO0OO0OO =OO0OOO0O0OOO0O00O .read_until (b'\n').decode ().strip ()#line:733
                                OO0OOO0O0OOO0O00O .flush ()#line:734
                                if "\x00"in O0O0000O0OO0OO0OO or not O0O0000O0OO0OO0OO :#line:736
                                    raise Exception ("Empty data received")#line:737
                                O0O0000O0OO0OO0OO =O0O0000O0OO0OO0OO .split (',')#line:743
                                try :#line:745
                                    if O0O0000O0OO0OO0OO [0 ]and O0O0000O0OO0OO0OO [1 ]:#line:746
                                        break #line:747
                                except Exception as OOOOOOOOOOO0OO0O0 :#line:748
                                    debug_output (O0OOOO00OOO00OOO0 +': retrying reading data: '+str (OOOOOOOOOOO0OO0O0 ))#line:752
                                    OOOO0000OO0O000O0 +=1 #line:753
                            except Exception as OOOOOOOOOOO0OO0O0 :#line:754
                                debug_output (O0OOOO00OOO00OOO0 +': retrying sending data: '+str (OOOOOOOOOOO0OO0O0 ))#line:758
                                OOOO0000OO0O000O0 +=1 #line:759
                        try :#line:761
                            OO0O00O0OO00OOO00 =round (int (O0O0000O0OO0OO0OO [1 ],2 )/1000000 ,3 )#line:763
                            if OO0O00O0OO00OOO00 <1 :#line:764
                                OO0O00O0OO00OOO00 =str (int (OO0O00O0OO00OOO00 *1000 ))+"ms"#line:766
                            else :#line:767
                                OO0O00O0OO00OOO00 =str (round (OO0O00O0OO00OOO00 ,2 ))+"s"#line:768
                            OOO0OO0O00OOO000O =round (int (O0O0000O0OO0OO0OO [0 ],2 )*1000000 /int (O0O0000O0OO0OO0OO [1 ],2 ),2 )#line:771
                            hashrate_mean .append (OOO0OO0O00OOO000O )#line:772
                            hashrate =mean (hashrate_mean [-5 :])#line:774
                            break #line:800
                        except Exception as OOOOOOOOOOO0OO0O0 :#line:801
                            pretty_print ('usb'+str (''.join (filter (str .isdigit ,O0OOOO00OOO00OOO0 ))),get_string ('mining_avr_connection_error')+Style .NORMAL +Fore .RESET +' (error reading result from the board: '+str (OOOOOOOOOOO0OO0O0 )+', please check connection '+'and port setting)','warning')#line:812
                            debug_output (O0OOOO00OOO00OOO0 +': error splitting data: '+str (OOOOOOOOOOO0OO0O0 ))#line:814
                            sleep (1 )#line:815
                    try :#line:817
                        O0O000O00000O0O00 .sendall (bytes (str (O0O0000O0OO0OO0OO [0 ])+','+str (OOO0OO0O00OOO000O )+',Official AVR Miner v'+str (MINER_VER )+','+str (rig_identifier )+','+str (O0O0000O0OO0OO0OO [2 ]),encoding ='ascii'))#line:830
                    except Exception as OOOOOOOOOOO0OO0O0 :#line:831
                        pretty_print ('net'+str (''.join (filter (str .isdigit ,O0OOOO00OOO00OOO0 ))),get_string ('connecting_error')+Style .NORMAL +Fore .RESET +' ('+str (OOOOOOOOOOO0OO0O0 )+')','error')#line:841
                        debug_output (O0OOOO00OOO00OOO0 +': connection error: '+str (OOOOOOOOOOO0OO0O0 ))#line:842
                        sleep (5 )#line:843
                        break #line:844
                    while True :#line:846
                        try :#line:847
                            O00000OO0OOO00OOO =now ()#line:848
                            O0O00OOO000O0O0OO =O0O000O00000O0O00 .recv (64 ).decode ().rstrip ('\n')#line:849
                            OO0OO0OOO0O00O000 =now ()#line:850
                            O000O00O0OO000000 =(OO0OO0OOO0O00O000 -O00000OO0OOO00OOO ).microseconds #line:853
                            ping_mean .append (round (O000O00O0OO000000 /1000 ))#line:854
                            OO0OO000OO00O0O00 =mean (ping_mean [-10 :])#line:855
                            debug_output (O0OOOO00OOO00OOO0 +': feedback: '+str (O0O00OOO000O0O0OO )+' with ping: '+str (OO0OO000OO00O0O00 ))#line:859
                            break #line:860
                        except Exception as OOOOOOOOOOO0OO0O0 :#line:861
                            pretty_print ('net'+str (''.join (filter (str .isdigit ,O0OOOO00OOO00OOO0 ))),get_string ('connecting_error')+Style .NORMAL +Fore .RESET +' (err parsing response: '+str (OOOOOOOOOOO0OO0O0 )+')','error')#line:871
                            debug_output (O0OOOO00OOO00OOO0 +': error parsing response: '+str (OOOOOOOOOOO0OO0O0 ))#line:873
                            sleep (5 )#line:874
                            break #line:875
                    O0O0OO0OO0OO0000O =get_prefix (O0O0OO0OO0OO0000O )#line:877
                    if O0O00OOO000O0O0OO =='GOOD':#line:878
                        shares [0 ]+=1 #line:880
                        title (get_string ('duco_avr_miner')+str (MINER_VER )+') - '+str (shares [0 ])+'/'+str (shares [0 ]+shares [1 ])+get_string ('accepted_shares'))#line:888
                        with thread_lock :#line:889
                            print (Style .RESET_ALL +Fore .WHITE +now ().strftime (Style .DIM +'%H:%M:%S ')+Style .BRIGHT +Back .MAGENTA +Fore .RESET +' usb'+str (''.join (filter (str .isdigit ,O0OOOO00OOO00OOO0 )))+' '+Back .RESET +Fore .GREEN +' ⛏'+get_string ('accepted')+Fore .RESET +str (int (shares [0 ]))+'/'+str (int (shares [0 ]+shares [1 ]))+Fore .YELLOW +' ('+str (int ((shares [0 ]/(shares [0 ]+shares [1 ])*100 )))+'%)'+Style .NORMAL +Fore .RESET +' ∙ '+Fore .BLUE +Style .BRIGHT +str (round (hashrate ))+' H/s'+Style .NORMAL +' ('+OO0O00O0OO00OOO00 +')'+Fore .RESET +' ⚙ diff '+str (O0O0OO0OO0OO0000O )+' ∙ '+Fore .CYAN +'ping '+str ('%02.0f'%int (OO0OO000OO00O0O00 ))+'ms')#line:931
                    elif O0O00OOO000O0O0OO =='BLOCK':#line:933
                        shares [0 ]+=1 #line:935
                        title (get_string ('duco_avr_miner')+str (MINER_VER )+') - '+str (shares [0 ])+'/'+str (shares [0 ]+shares [1 ])+get_string ('accepted_shares'))#line:943
                        with thread_lock :#line:944
                            print (Style .RESET_ALL +Fore .WHITE +now ().strftime (Style .DIM +'%H:%M:%S ')+Style .BRIGHT +Back .MAGENTA +Fore .RESET +' usb'+str (''.join (filter (str .isdigit ,O0OOOO00OOO00OOO0 )))+' '+Back .RESET +Fore .CYAN +' ⛏'+get_string ('block_found')+Fore .RESET +str (int (shares [0 ]))+'/'+str (int (shares [0 ]+shares [1 ]))+Fore .YELLOW +' ('+str (int ((shares [0 ]/(shares [0 ]+shares [1 ])*100 )))+'%)'+Style .NORMAL +Fore .RESET +' ∙ '+Fore .BLUE +Style .BRIGHT +str (round (hashrate ))+' H/s'+Style .NORMAL +' ('+OO0O00O0OO00OOO00 +')'+Fore .RESET +' ⚙ diff '+str (O0O0OO0OO0OO0000O )+' ∙ '+Fore .CYAN +'ping '+str ('%02.0f'%int (OO0OO000OO00O0O00 ))+'ms')#line:986
                    else :#line:988
                        shares [1 ]+=1 #line:990
                        title (get_string ('duco_avr_miner')+str (MINER_VER )+') - '+str (shares [0 ])+'/'+str (shares [0 ]+shares [1 ])+get_string ('accepted_shares'))#line:998
                        with thread_lock :#line:999
                            print (Style .RESET_ALL +Fore .WHITE +now ().strftime (Style .DIM +'%H:%M:%S ')+Style .BRIGHT +Back .MAGENTA +Fore .RESET +' usb'+str (''.join (filter (str .isdigit ,O0OOOO00OOO00OOO0 )))+' '+Back .RESET +Fore .RED +' ✗'+get_string ('rejected')+Fore .RESET +str (int (shares [0 ]))+'/'+str (int (shares [0 ]+shares [1 ]))+Fore .YELLOW +' ('+str (int ((shares [0 ]/(shares [0 ]+shares [1 ])*100 )))+'%)'+Style .NORMAL +Fore .RESET +' ∙ '+Fore .BLUE +Style .BRIGHT +str (round (hashrate ))+' H/s'+Style .NORMAL +' ('+OO0O00O0OO00OOO00 +')'+Fore .RESET +' ⚙ diff '+str (O0O0OO0OO0OO0000O )+' ∙ '+Fore .CYAN +'ping '+str ('%02.0f'%int (OO0OO000OO00O0O00 ))+'ms')#line:1041
                    O0OO00O000O0OOO0O =time ()#line:1043
                    OO000O0OOO00OO00O =O0OO00O000O0OOO0O -OO00OO0OO0O00O00O #line:1044
                    if (O0O0O00O00OO0O0O0 ==0 and OO000O0OOO00OO00O >=PERIODIC_REPORT_TIME ):#line:1046
                        OOO0OOOO0OO0OOOO0 =shares [0 ]-OOO0OOO0OOO00OO00 #line:1047
                        OO0000O000000OO00 =calculate_uptime (mining_start_time )#line:1048
                        periodic_report (OO00OO0OO0O00O00O ,O0OO00O000O0OOO0O ,OOO0OOOO0OO0OOOO0 ,hashrate ,OO0000O000000OO00 )#line:1054
                        OO00OO0OO0O00O00O =time ()#line:1055
                        OOO0OOO0OOO00OO00 =shares [0 ]#line:1056
                    sleep (1 )#line:1058
                    break #line:1059
        except Exception as OOOOOOOOOOO0OO0O0 :#line:1061
            pretty_print ('net0',get_string ('connecting_error')+Style .NORMAL +' (main loop err: '+str (OOOOOOOOOOO0OO0O0 )+')','error')#line:1069
            debug_output ('Main loop error: '+str (OOOOOOOOOOO0OO0O0 ))#line:1070
def periodic_report (O00OO0O000O000O00 ,OO0O0O00OOOOOO0O0 ,O0O0OO0O0O0000000 ,OOO00OOO000OOO0O0 ,OOOOO0O0OO00O00OO ):#line:1077
    O00OO0000O000O000 =round (OO0O0O00OOOOOO0O0 -O00OO0O000O000O00 )#line:1078
    pretty_print ("sys0"," "+get_string ('periodic_mining_report')+Fore .RESET +Style .NORMAL +get_string ('report_period')+str (O00OO0000O000O000 )+get_string ('report_time')+get_string ('report_body1')+str (O0O0OO0O0O0000000 )+get_string ('report_body2')+str (round (O0O0OO0O0O0000000 /O00OO0000O000O000 ,1 ))+get_string ('report_body3')+get_string ('report_body4')+str (int (OOO00OOO000OOO0O0 ))+" H/s"+get_string ('report_body5')+str (int (OOO00OOO000OOO0O0 *O00OO0000O000O000 ))+get_string ('report_body6')+get_string ('total_mining_time')+str (OOOOO0O0OO00O00OO ),"success")#line:1098
def calculate_uptime (OOOOOOOOOO000OOO0 ):#line:1101
    O00O0O00O0O0OOOO0 =time ()-OOOOOOOOOO000OOO0 #line:1102
    if O00O0O00O0O0OOOO0 <=59 :#line:1103
        return str (round (O00O0O00O0O0OOOO0 ))+get_string ('uptime_seconds')#line:1104
    elif O00O0O00O0O0OOOO0 ==60 :#line:1105
        return str (round (O00O0O00O0O0OOOO0 //60 ))+get_string ('uptime_minute')#line:1106
    elif O00O0O00O0O0OOOO0 >=60 :#line:1107
        return str (round (O00O0O00O0O0OOOO0 //60 ))+get_string ('uptime_minutes')#line:1108
    elif O00O0O00O0O0OOOO0 ==3600 :#line:1109
        return str (round (O00O0O00O0O0OOOO0 //3600 ))+get_string ('uptime_hour')#line:1110
    elif O00O0O00O0O0OOOO0 >=3600 :#line:1111
        return str (round (O00O0O00O0O0OOOO0 //3600 ))+get_string ('uptime_hours')#line:1112
def fetch_pools ():#line:1115
    while True :#line:1116
        pretty_print ("net0"," "+get_string ("connection_search")+"...","warning")#line:1121
        try :#line:1123
            OO00O0O00OO000OO0 =requests .get ("https://server.duinocoin.com/getPool").json ()#line:1126
            OOOOOO0000O0000OO ="51.158.182.90"#line:1128
            OOO0000O0OO0O00OO =6000 #line:1129
            return OOOOOO0000O0000OO ,OOO0000O0OO0O00OO #line:1131
        except Exception as OO0OOO0O000OOO00O :#line:1132
            pretty_print ("net0"," Error retrieving mining node: "+str (OO0OOO0O000OOO00O )+", retrying in 15s","error")#line:1137
            sleep (15 )#line:1138
if __name__ =='__main__':#line:1141
    if osname =="nt":#line:1142
        ossystem ("chcp 65001")#line:1144
        init (autoreset =True ,convert =True )#line:1146
    else :#line:1147
        init (autoreset =True )#line:1148
    title (get_string ('duco_avr_miner')+str (MINER_VER )+')')#line:1150
    try :#line:1152
        load_config ()#line:1154
        debug_output ('Config file loaded')#line:1155
    except Exception as e :#line:1156
        pretty_print ('sys0',get_string ('load_config_error')+RESOURCES_DIR +get_string ('load_config_error_warning')+Style .NORMAL +Fore .RESET +' ('+str (e )+')','error')#line:1167
        debug_output ('Error reading configfile: '+str (e ))#line:1168
        sleep (10 )#line:1169
        _exit (1 )#line:1170
    try :#line:1172
        greeting ()#line:1174
        debug_output ('greeting displayed')#line:1175
    except Exception as e :#line:1176
        debug_output ('Error displaying greeting message: '+str (e ))#line:1177
    try :#line:1179
        NODE_ADDRESS ,NODE_PORT =fetch_pools ()#line:1180
    except Exception as e :#line:1181
        print (e )#line:1182
        NODE_ADDRESS ="server.duinocoin.com"#line:1183
        NODE_PORT =2813 #line:1184
        debug_output ("Using default server port and address")#line:1185
    try :#line:1187
        threadid =0 #line:1189
        for port in avrport :#line:1190
            thrThread (target =mine_avr ,args =(port ,threadid )).start ()#line:1193
            threadid +=1 #line:1194
    except Exception as e :#line:1195
        debug_output ('Error launching AVR thread(s): '+str (e ))#line:1196
    if discord_presence =="y":#line:1198
        try :#line:1199
            init_rich_presence ()#line:1201
            thrThread (target =update_rich_presence ).start ()#line:1203
        except Exception as e :#line:1204
            debug_output ('Error launching Discord RPC thread: '+str (e ))
