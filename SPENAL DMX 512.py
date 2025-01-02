#libs
from tkinter import ttk, messagebox, filedialog, colorchooser
from tkinter import *
import pandas as pd
import numpy as np
import colorsys
import librosa
import time
import sys
import os
import warnings
warnings.filterwarnings('ignore')
pd.options.mode.chained_assignment=None
os.environ['PYGAME_HIDE_SUPPORT_PROMPT']='hide'
import pygame
##################################################################################################################################################################################
class GUI:
    ##################################################################################################################################################################################
    def __init__(self):
        try:
            self.icon = 'SPENAL DMX 512 Analysis.ico'
            if not hasattr(sys, 'frozen'):
                self.icon = os.path.join(os.path.dirname(__file__), self.icon) 
            else:  
                self.icon = os.path.join(sys.prefix, self.icon)
            self.name='SPENAL DMX Analysis'
            self.ex='DMA'
            self.colors={'Root': self.RGB((0,32,80)),
                           'Music Bar': self.RGB((0,173,238)),
                           'Control Bar': self.RGB((223,226,232)),
                           'Options': self.RGB((255, 242, 117)),
                           'Group Form': self.RGB((177,214,240)),
                           'Element Form': self.RGB((153, 154, 198)),
                           'Buttons': self.RGB((177,214,240)),
                           'LED': self.RGB((127,203,40)),
                           'Valve': self.RGB((210,71,38)),
                           'Pump': self.RGB((250,188,9)),
                           'Green': self.RGB((127,203,40)),
                           'Red': self.RGB((210,71,38)),}
            self.channels=1
            self.last_selected_ch=1
            self.led_from=[1]
            self.led_to=[2]
            self.pump_from=[1]
            self.pump_to=[2]
            self.valve_from=[1]
            self.valve_to=[2]
            self.packet_time=50
            pygame.mixer.init()
            self.play=False
            self.load=False
            self.audio_length=0
            self.last_pos=0
            self.music_address='Please upload an audio.'
            self.music_pos=0
            self.result_address=os.getcwd()+'\OUTPUT'
            if not os.path.isdir(self.result_address):
                os.mkdir(self.result_address)
            self.mode=['First to Last 1','First to Last 2','First to Last 3', 'First to Last 4','First to Last 5','First to Last Sum',
                       'Last to First 1','Last to First 2','Last to First 3','Last to First 4','Last to First 5','Last to First Sum',
                       'Random Shuffle 1','Random Shuffle 2','Random Shuffle 3','Random Shuffle 4','Random Shuffle 5','Random Shuffle R',
                       'Middle to Sides','Sides to Middle','All Together','Chance','Custom']
            self.pump_range=pd.DataFrame(columns=['From Time', 'To Time', 'From Range', 'To Range'])
            self.control_groups=pd.DataFrame(columns=['ID', 'Position', 'Sort', 'Shuffle'])
            self.control_groups.loc[0]=['Pump',0,-np.inf,'21-All Together']
            self.control_elements=pd.DataFrame(columns=['Type','ID', 'Position', 'Sort', 'Channel', 'Group'])
            self.shuffle_total_groups=2
            self.custom={}
            self.custom_color=[(0,0,0),(255,0,0),(0,255,0),(0,0,255),(255,255,0),(255,0,255),(0,255,255)]
            self.root=Tk()
            self.root.title(self.name)
            self.root.iconbitmap(self.icon)
            self.root.state('zoomed')
            self.APP(start=True)         
        except Exception as e:
            print('GUI INIT: ', e)
        return
    ##################################################################################################################################################################################
    def RGB(self, rgb):
        try:
            color='#000000'
            color='#%02x%02x%02x' % rgb
        except Exception as e:
            messagebox.showerror(title='RGB', message='Error in RGB to HEX convertor.', parent=self.root, icon='error')
        return color
    ##################################################################################################################################################################################
    def NEW(self):
        try:
            pygame.mixer.music.stop()
            pygame.mixer.stop()
            pygame.mixer.quit()
            pygame.mixer.init()
            self.play=False
            self.load=False
            self.audio_length=0
            self.last_pos=0
            self.music_address='Please upload an audio.'
            self.music_pos=0
            self.channels=1
            self.last_selected_ch=1
            self.led_from=[1]
            self.led_to=[2]
            self.pump_from=[1]
            self.pump_to=[2]
            self.valve_from=[1]
            self.valve_to=[2]
            self.packet_time=50
            self.result_address=os.getcwd()+'\OUTPUT'
            if not os.path.isdir(self.result_address):
                os.mkdir(self.result_address)
            self.pump_range=pd.DataFrame(columns=['From Time', 'To Time', 'From Range', 'To Range'])
            self.control_groups=pd.DataFrame(columns=['ID', 'Position', 'Sort', 'Shuffle'])
            self.control_groups.loc[0]=['Pump',0,-np.inf,'21-All Together']
            self.control_elements=pd.DataFrame(columns=['Type','ID', 'Position', 'Sort', 'Channel', 'Group'])
            self.shuffle_total_groups=2
            self.custom={}
            self.custom_color=[(0,0,0),(255,0,0),(0,255,0),(0,0,255),(255,255,0),(255,0,255),(0,255,255)]
            self.APP(start=True)    
        except Exception as e:
            messagebox.showerror(title='NEW', message='The app failed to create a new project.', parent=self.root, icon='error')
        return
    ##################################################################################################################################################################################
    def OPTIONS(self):
        ### OPTIONS helpers
        def CHANNEL_COMBOBOX_CHANGE(event):
            try:
                result=CHECK_RANGE(self.last_selected_ch-1)                
                if result:
                    ch=int(combobox_channel.get())
                    self.last_selected_ch=ch
                    entry_led_from.delete(0, END)
                    entry_led_from.insert(0, self.led_from[ch-1])
                    entry_led_to.delete(0, END)
                    entry_led_to.insert(0, self.led_to[ch-1]-1)
                    entry_pump_from.delete(0, END)
                    entry_pump_from.insert(0, self.pump_from[ch-1])
                    entry_pump_to.delete(0, END)
                    entry_pump_to.insert(0, self.pump_to[ch-1]-1)
                    entry_valve_from.delete(0, END)
                    entry_valve_from.insert(0, self.valve_from[ch-1])
                    entry_valve_to.delete(0, END)
                    entry_valve_to.insert(0, self.valve_to[ch-1]-1)
                else:
                    combobox_channel.set(self.last_selected_ch)
            except Exception as e:
                messagebox.showerror(title='OPTIONS CHANNEL_COMBOBOX_CHANGE', message='Cannot change channel range.', parent=self.root, icon='error')
            return
        ### OPTIONS helpers
        def PUMP_RANGE():
            try:
                self.pump_range.to_excel('pump_range_buffer.xlsx',index=False)
                response=False
                while not response:
                    os.system('start "excel" "{}\\pump_range_buffer.xlsx"'.format(os.getcwd()))
                    response=messagebox.askyesno(title='EXCEL SAVE WARNING', message='Did you fill and save pump_range_buffer.xlsx?\n Be sure to save and close the excel file.', parent=self.root, icon='warning')
                self.pump_range=pd.read_excel('pump_range_buffer.xlsx')
                os.remove('pump_range_buffer.xlsx')
            except Exception as e:
                messagebox.showerror(title='OPTIONS PUMP_RANGE', message='Pump range could not be set.', parent=self.root, icon='error')
            return
        ### OPTIONS helpers
        def SET():
            try:
                channels=entry_channels.get()
                packet_time=entry_packet_time.get()
                try:
                    ch=int(combobox_channel.get())
                    self.last_selected_ch=ch
                    result=CHECK_RANGE(self.last_selected_ch-1)
                    if result:
                        e1=0
                        if 0<int(channels):
                            e1 += 1
                            self.channels = int(channels)
                        else:
                            raise Exception('Channels should be an integer greater than 0.')
                        if (10 <= int(packet_time) <= 100):
                            self.packet_time=int(packet_time)
                            e1 += 1
                        else:
                            raise Exception('Please insert a valid Packet Time between 10 ms to 100 ms.')
                        window.destroy()
                        self.last_selected_ch=1
                        self.APP(start=False)
                except Exception as ee:
                    if e1 == 0:
                        ee='Channels should be an integer greater than 0.'
                    elif e1 == 1:
                        ee='Packet Time is not an integer'
                    messagebox.showerror(title='OPTIONS SET', message=ee, parent=self.root, icon='error')
            except Exception as e:
                messagebox.showerror(title='OPTIONS SET', message='Setting failed.', parent=self.root, icon='error')
            return
        ### OPTIONS helpers
        def CHECK_RANGE(ch):
            try:
                result=False
                led_from=entry_led_from.get()
                led_to=entry_led_to.get()
                pump_from=entry_pump_from.get()
                pump_to=entry_pump_to.get()
                valve_from=entry_valve_from.get()
                valve_to=entry_valve_to.get()
                try:
                    e1=0
                    if (1 <= int(led_from) <= 512):
                        e1 += 1
                    else:
                        raise Exception('LED start byte range is out of range.')
                    if (1 <= int(led_to) <= 512):
                        e1 += 1
                    else:
                        raise Exception('LED end byte range is out of range.')
                    if (1 <= int(pump_from) <= 512):
                        e1 += 1
                    else:
                        raise Exception('Pump start byte range is out of range.')
                    if (1 <= int(pump_to) <= 512):
                        e1 += 1
                    else:
                        raise Exception('Pump end byte range is out of range.')
                    if (1 <= int(valve_from) <= 512):
                        e1 += 1
                    else:
                        raise Exception('Valve start byte range is out of range.')
                    if (1 <= int(valve_to) <= 512):
                        e1 += 1
                    else:
                        raise Exception('Valve end byte range is out of range.')
                    if int(led_to)+1 < int(led_from):
                        raise Exception('LED end byte is lower than start byte.')
                    if int(pump_to)+1 < int(pump_from):
                        raise Exception('Pump end byte is lower than start byte.')
                    if int(valve_to)+1 < int(valve_from):
                        raise Exception('Valve end byte is lower than start byte.')
                    if ((int(led_to)-int(led_from)+1) % 3 != 0) and (int(led_from) != int(led_to)):
                        raise Exception('LED byte range is not divided by 3.')
                    buff=pd.DataFrame({'Type':['LED','Pump','Valve'],'From':[int(led_from),int(pump_from),int(valve_from)], 'To':[int(led_to)+1,int(pump_to)+1, int(valve_to)+1]})
                    buff=buff.sort_values(by=['To','From']).reset_index(drop=True)
                    if buff['From'].min() != 1:
                        raise Exception('Ranges do not start from 1')
                    elif len(set(buff['From'].to_list())) == 1:
                        raise Exception('There is no space for any element in channel {}.'.format(ch+1))
                    for i in range(2):
                        if buff['From'][i+1] < buff['To'][i]:
                            raise Exception('{} range is not after {} range.'.format(buff['Type'][i+1], buff['Type'][i]))
                    self.led_from[ch]=int(led_from)
                    self.led_to[ch]=int(led_to)+1
                    self.pump_from[ch]=int(pump_from)
                    self.pump_to[ch]=int(pump_to)+1
                    self.valve_from[ch]=int(valve_from)
                    self.valve_to[ch]=int(valve_to)+1
                    result=True
                except Exception as ee:
                    if e1 == 0:
                        ee='LED start byte range is not an integer between 1 and 512.'
                    elif e1 == 1:
                        ee='LED end byte range is not an integer between 1 and 512.'
                    elif e1 == 2:
                        ee='Pump start byte range is not an integer between 1 and 512.'
                    elif e1 == 3:
                        ee='Pump end byte range is not an integer between 1 and 512.'
                    elif e1 == 4:
                        ee='Valve start byte range is not an integer between 1 and 512.'
                    elif e1 == 5:
                        ee='Valve end byte range is not an integer between 1 and 512.'
                    messagebox.showerror(title='OPTIONS CHECK_RANGE', message=ee, parent=self.root, icon='error')
            except Exception as e:
                messagebox.showerror(title='OPTIONS CHECK_RANGE', message='Range checking failed.', parent=self.root, icon='error')
            return result
        ### OPTIONS helpers
        def MODIFY():
            try:
                num_channels=int(entry_channels.get())
                if num_channels <= self.channels:
                    self.led_from=self.led_from[:num_channels]
                    self.led_to=self.led_to[:num_channels]
                    self.pump_from=self.pump_from[:num_channels]
                    self.pump_to=self.pump_to[:num_channels]
                    self.valve_from=self.valve_from[:num_channels]
                    self.valve_to=self.valve_to[:num_channels]
                else:
                    for i in range(num_channels-self.channels):
                        self.led_from.append(1)
                        self.led_to.append(2)
                        self.pump_from.append(1)
                        self.pump_to.append(2)
                        self.valve_from.append(1)
                        self.valve_to.append(2)
                self.channels=num_channels
                combobox_channel['values'] = list(range(1,self.channels+1))
            except Exception as e:
                messagebox.showerror(title='OPTIONS MODIFY', message='Cannot modify number of channels.', parent=self.root, icon='error')
            return
        ### OPTIONS helpers
        try:
            window=Toplevel(bd=10, bg=self.colors['Options'])
            window.title('Options')
            window.resizable(0, 0)
            window.grab_set()
            window.geometry('+%d+%d' % (0, 0))
            window.iconbitmap(self.icon)
            ypad=2
            #col1
            col1=Label(master=window, bg=self.colors['Options'])
            col1.grid(row=0,column=0)            
            labelframe_channels=LabelFrame(master=col1, text='Channels', labelanchor=NW, bg=self.colors['Options'])
            labelframe_channels.pack(fill=BOTH, expand=True)
            Label(master=labelframe_channels, bg=self.colors['Options']).pack(side=LEFT, fill=BOTH, expand=True)
            entry_channels=Entry(master=labelframe_channels, justify=CENTER, width=10)
            entry_channels.insert(0, self.channels)
            entry_channels.pack(side=LEFT, pady=ypad)
            Label(master=labelframe_channels, bg=self.colors['Options']).pack(side=LEFT, fill=BOTH, expand=True)
            button_channels=Button(master=labelframe_channels, text='Modify', width=10, bg=self.colors['Buttons'], command=MODIFY)
            button_channels.pack(side=LEFT, pady=ypad+2)
            Label(master=labelframe_channels, bg=self.colors['Options']).pack(side=LEFT, fill=BOTH, expand=True)
            Label(master=col1, bg=self.colors['Options']).pack()
            labelframe_ranges=LabelFrame(master=col1, text='Ranges', labelanchor=NW, bg=self.colors['Options'])
            labelframe_ranges.pack(fill=BOTH, expand=True)
            combobox_channel = ttk.Combobox(master=labelframe_ranges, justify=CENTER)
            combobox_channel['values'] = list(range(1,self.channels+1))
            combobox_channel.set(1)
            combobox_channel['state'] = 'readonly'
            combobox_channel.pack(pady=ypad)
            combobox_channel.bind('<<ComboboxSelected>>',CHANNEL_COMBOBOX_CHANGE)
            l1=Label(master=labelframe_ranges, bg=self.colors['Options'])
            l1.pack()
            entry_led_from=Entry(master=l1, justify=CENTER, width=10)
            entry_led_from.pack(side=LEFT, fill=BOTH, expand=True, pady=ypad)
            entry_led_from.insert(0, self.led_from[0])
            Label(master=l1, text=' \u27A1   LED   \u27A1 ', bg=self.colors['Options']).pack(side=LEFT, fill=BOTH, expand=True, pady=ypad)
            entry_led_to=Entry(master=l1, justify=CENTER, width=10)
            entry_led_to.pack(side=LEFT, fill=BOTH, expand=True, pady=ypad)
            entry_led_to.insert(0, self.led_to[0]-1)
            l2=Label(master=labelframe_ranges, bg=self.colors['Options'])
            l2.pack()
            entry_pump_from=Entry(master=l2, justify=CENTER, width=10)
            entry_pump_from.pack(side=LEFT, fill=BOTH, expand=True, pady=ypad)
            entry_pump_from.insert(0, self.pump_from[0])
            Label(master=l2, text=' \u27A1 Pump \u27A1 ', bg=self.colors['Options']).pack(side=LEFT, fill=BOTH, expand=True, pady=ypad)
            entry_pump_to=Entry(master=l2, justify=CENTER, width=10)
            entry_pump_to.pack(side=LEFT, fill=BOTH, expand=True, pady=ypad)
            entry_pump_to.insert(0, self.pump_to[0]-1)
            l3=Label(master=labelframe_ranges, bg=self.colors['Options'])
            l3.pack()
            entry_valve_from=Entry(master=l3, justify=CENTER, width=10)
            entry_valve_from.pack(side=LEFT, fill=BOTH, expand=True, pady=ypad)
            entry_valve_from.insert(0, self.valve_from[0])
            Label(master=l3, text=' \u27A1  Valve  \u27A1 ', bg=self.colors['Options']).pack(side=LEFT, fill=BOTH, expand=True, pady=ypad)
            entry_valve_to=Entry(master=l3, justify=CENTER, width=10)
            entry_valve_to.pack(side=LEFT, fill=BOTH, expand=True, pady=ypad)
            entry_valve_to.insert(0, self.valve_to[0]-1)
            Label(master=col1, bg=self.colors['Options']).pack()
            labelframe_packet_time=LabelFrame(master=col1, text='Packet Time (ms)', labelanchor=NW, bg=self.colors['Options'])
            labelframe_packet_time.pack(fill=BOTH, expand=True)
            text_help='*Note: Group custom "Frame" column should be a common multiple of the Packet Time.'
            size=41
            Label(master=labelframe_packet_time,text='\n'.join([text_help[i:i+size] for i in range(0,len(text_help),size)]), bg=self.colors['Options'], justify=LEFT).pack(fill=BOTH,expand=True)
            entry_packet_time=Entry(master=labelframe_packet_time, justify=CENTER, width=10)
            entry_packet_time.pack(pady=ypad)
            entry_packet_time.insert(0, self.packet_time)
            Label(master=col1, bg=self.colors['Options']).pack()
            labelframe_pump=LabelFrame(master=col1, text='Pump Range', labelanchor=NW, bg=self.colors['Options'])
            labelframe_pump.pack(fill=BOTH, expand=True)
            button_pump=Button(master=labelframe_pump, text='      Edit Pump Range      ', height=1, bg=self.colors['Buttons'], command=PUMP_RANGE)
            button_pump.pack(ipady=ypad, pady=ypad+2)
            button_set=Button(master=window, text='Set', width=15, bg=self.colors['Buttons'], command=SET)
            button_set.grid(row=1,column=0,columnspan=1,pady=10)
        except Exception as e:
            messagebox.showerror(title='OPTIONS', message='Options are not available.', parent=self.root, icon='error')
        return
    ##################################################################################################################################################################################
    def DIVISION(self, merge_address=None):
        ### DIVISION helpers
        def START():                        
            try:
                num_bytes=513
                div=entry_div.get()
                div=[[int(ch) for ch in item.split('-')] for item in div.split(',')]
                if sum([len(item) for item in div])/len(div)!=2:
                    raise Exception('Orders are not valid.')
                for i in range(len(div)):
                    final=[]
                    for j in range(len(data['metadata'][0])):
                        sub_final=[]
                        for ch in range(div[i][0],div[i][1]+1):
                            buff=[0]*num_bytes
                            buff[data['range'][ch-1][0]:data['range'][ch-1][1]]=data['metadata'][ch-1].iloc[j,0:data['border'][ch-1][0]].to_list()
                            valve_buff=np.array_split(data['metadata'][ch-1].iloc[j,data['border'][ch-1][0]:data['border'][ch-1][1]].to_list(), int(data['range'][ch-1][3]-data['range'][ch-1][2]))
                            valve_buff=[int(''.join(str(x) for x in list(chunk.astype(int))[::-1]),2) for chunk in valve_buff]
                            buff[data['range'][ch-1][2]:data['range'][ch-1][3]]=valve_buff
                            buff[data['range'][ch-1][4]:data['range'][ch-1][5]]=data['metadata'][ch-1].iloc[j,data['border'][ch-1][1]:data['border'][ch-1][2]].to_list()
                            sub_final.extend(buff[1:])
                        final.append(sub_final)
                    #s=pd.DataFrame(final)
                    #s.to_excel('1.xlsx')
                    final=bytearray(list(np.array(final).flatten()))                           
                    with open(os.path.dirname(merge_address)+'\\channel_{}_{}.DMX'.format(div[i][0],div[i][1]), 'wb') as res_file:
                        res_file.write(final)
                window.destroy()
                messagebox.showinfo(title='Completed', message='Division has completed successfully. For seeing the results go to:\n{}'.format(os.path.dirname(merge_address)), parent=self.root, icon='info') 
            except Exception as e:
                messagebox.showerror(title='DIVISION START', message='Cannot divide data with the given order.', parent=self.root, icon='error')
        ### DIVISION helpers
        try:
            if not merge_address:
                merge_address=filedialog.askopenfilename()
            if merge_address:
                try:
                    data=pd.read_pickle(merge_address)
                    if list(data.columns) == ['metadata','border','range']:
                        window=Toplevel(bd=10, bg=self.colors['Options'])
                        window.title('Division')
                        window.resizable(0, 0)
                        window.grab_set()
                        window.geometry('+%d+%d' % (0, 0))
                        window.iconbitmap(self.icon)
                        Label(master=window, text='{} channels have been detected in the selected file. How to divide the channels?'.format(len(data)), bg=self.colors['Options']).pack()
                        Label(master=window, text='', bg=self.colors['Options']).pack()
                        Label(master=window, text='*Note: For example the selected database has 7 channels if you insert "1-2,3-3,4-7"\n the output would be three files which first file contains channels 1 and 2 and the second file contains channel 3 and the third file contains channel 4 to 7.', bg=self.colors['Options']).pack()
                        Label(master=window, text='', bg=self.colors['Options']).pack()
                        entry_div=Entry(master=window, justify=CENTER, width=100)
                        entry_div.pack()
                        Label(master=window, text='', bg=self.colors['Options']).pack()
                        button_start=Button(master=window, text='Start', bg='DarkSeaGreen1', width=18,command=START)
                        button_start.pack()
                    else:
                        messagebox.showerror(title=self.name, message='The selected database is not in the correct format.', parent=self.root, icon='error')
                except Exception as ee:
                    messagebox.showerror(title=self.name, message='Please select a valid database.', parent=self.root, icon='error')
        except Exception as e:
            messagebox.showerror(title='DIVISION', message='Division is broken.', parent=self.root, icon='error')
        return
    ##################################################################################################################################################################################
    def CUSTOMS(self):
        ### CUSTOM helpers
        def MODE_HELP():
            try:
                text='''First to Last 1: From the first element of the group to the last element goes one by one with the step of 1.\n
First to Last 2: From the first element of the group to the last element goes one by one with the step of 2.\n
First to Last 3: From the first element of the group to the last element goes one by one with the step of 3.\n
First to Last 4: From the first element of the group to the last element goes one by one with the step of 4.\n
First to Last 5: From the first element of the group to the last element goes one by one with the step of 5.\n
First to Last Sum: From the first element of the group to the last element starts turning on.\n
Last to First 1: From the last element of the group to the first element goes one by one with the step of 1.\n
Last to First 2: From the last element of the group to the first element goes one by one with the step of 2.\n
Last to First 3: From the last element of the group to the first element goes one by one with the step of 3.\n
Last to First 4: From the last element of the group to the first element goes one by one with the step of 4.\n
Last to First 5: From the last element of the group to the first element goes one by one with the step of 5.\n
Last to First Sum: From the last element of the group to the first element starts turning on.\n
Random Shuffle 1: Turning on 1 random elements in each step.\n
Random Shuffle 2: Turning on 2 random elements in each step.\n
Random Shuffle 3: Turning on 3 random elements in each step.\n
Random Shuffle 4: Turning on 4 random elements in each step.\n
Random Shuffle 5: Turning on 5 random elements in each step.\n
Random Shuffle R: Turning on R random elements in each step which R is the random number from zero to number of elements in the group.\n
Middle to Sides: Turning on elements from middle of the group to the sides.\n
Sides to Middle: Turning on elements from sides of the group to the middle.\n
All Together: Turning on all elements of the group. You can create empty frame by setting LED and Valve values to zero.\n
Chance: Choosing random mode from modes above.'''
                messagebox.showinfo(title='Shuffle Modes', message=text, parent=self.root, icon='info')
            except Exception as e:
                messagebox.showerror(title='MODE_HELP', message='Cannot show help for modes.', parent=self.root, icon='error')
            return
        ### CUSTOM helpers
        def EDIT_COLOR(event=None, index=0, action='EDIT'):
            try:
                if action=='EDIT':
                    color_code = colorchooser.askcolor(title ='Choose color')
                    if color_code[0]:
                        if index!=-1:
                            self.custom_color[index]=color_code[0]
                        else:
                            self.custom_color.append(color_code[0])
                elif action=='DELETE':
                    self.custom_color.pop(index)
                for child in container.winfo_children():
                    child.destroy()
                canvas=Canvas(master=container, bg=self.colors['Options'])
                canvas.place(relx=0.05, rely=0.05, relwidth=0.80, relheight=0.80)
                yscrollbar_total=ttk.Scrollbar(master=container, orient=VERTICAL, command=canvas.yview)
                yscrollbar_total.place(relx=0.85, rely=0.05, relwidth=0.10, relheight=0.80)
                canvas.configure(yscrollcommand=yscrollbar_total.set, highlightbackground=self.colors['Options'], highlightcolor=self.colors['Options'])
                for i in range(len(self.custom_color)):
                    fg=tuple([255-c for c in self.custom_color[i]])               
                    b_color=Button(master=l2,text=i,width=12, fg=self.RGB(fg), bg=self.RGB(self.custom_color[i]),activebackground=self.RGB(self.custom_color[i]),font=('Times',12,'bold'),command=lambda event=None, index=i, action='EDIT':EDIT_COLOR(event, index,action))
                    b_color.bind('<Button-3>', lambda event, index=i, action='DELETE':EDIT_COLOR(event, index,action))
                    canvas.create_window(0, 40*i, anchor=N, window=b_color)
                canvas.bind('<Configure>', canvas.configure(scrollregion=canvas.bbox('all')))
            except Exception as e:
                messagebox.showerror(title='CUSTOMS', message='Cannot edit a new color.', parent=self.root, icon='error')
            return
        ### CUSTOM helpers
        try:
            window=Toplevel(bd=10, bg=self.colors['Options'])
            window.title('Custom')
            window.resizable(0, 0)
            window.grab_set()
            window.geometry('+%d+%d' % (0, 0))
            window.iconbitmap(self.icon)
            l1=LabelFrame(master=window,text='Shuffle Modes',labelanchor=NW,bd=3, bg=self.colors['Options'])
            l1.pack(side=LEFT,fill=BOTH,expand=True,padx=10,pady=10)
            for i in range(len(self.mode)-1):
                l_tag=Label(master=l1,text=' {} - '.format(i),bg=self.colors['Options'])
                l_mode=Label(master=l1,text=self.mode[i],bg=self.colors['Options'])
                l_tag.grid(row=i,column=0,padx=7)
                l_mode.grid(row=i,column=1,padx=7)
            btn_help=Button(master=l1,text=' ? ', bg=self.colors['Red'],activebackground=self.colors['Red'],font=('Times',12,'bold'),command=MODE_HELP)
            btn_help.grid(row=len(self.mode),column=0,columnspan=2, pady=5)
            l2=LabelFrame(master=window,text='Custom Colors',labelanchor=NW,bd=3, bg=self.colors['Options'])
            l2.pack(side=RIGHT,fill=BOTH,expand=True,padx=10,pady=10)
            container=Label(master=l2,bg=self.colors['Options'],width=23)
            container.pack(fill=BOTH,expand=True)
            canvas=Canvas(master=container, bg=self.colors['Options'])
            canvas.place(relx=0.05, rely=0.05, relwidth=0.80, relheight=0.80)
            yscrollbar_total=ttk.Scrollbar(master=container, orient=VERTICAL, command=canvas.yview)
            yscrollbar_total.place(relx=0.85, rely=0.05, relwidth=0.10, relheight=0.80)
            canvas.configure(yscrollcommand=yscrollbar_total.set, highlightbackground=self.colors['Options'], highlightcolor=self.colors['Options'])
            for i in range(len(self.custom_color)):
                fg=tuple([255-c for c in self.custom_color[i]])
                b_color=Button(master=l2,text=i,width=12, fg=self.RGB(fg), bg=self.RGB(self.custom_color[i]),activebackground=self.RGB(self.custom_color[i]),font=('Times',12,'bold'),command=lambda event=None, index=i, action='EDIT':EDIT_COLOR(event, index,action))
                b_color.bind('<Button-3>', lambda event, index=i, action='DELETE':EDIT_COLOR(event, index,action))
                canvas.create_window(0, 40*i, anchor=N, window=b_color)
            canvas.bind('<Configure>', canvas.configure(scrollregion=canvas.bbox('all')))
            b_add=Button(master=l2,text='ADD',width=15, bg=self.colors['Red'],activebackground=self.colors['Red'],font=('Times',12,'bold'),command=lambda event=None, index=-1, action='EDIT':EDIT_COLOR(event, index,action))
            b_add.pack(pady=25)
        except Exception as e:
            messagebox.showerror(title='CUSTOMS', message='The Custom section is broken.', parent=self.root, icon='error')
        return
    ##################################################################################################################################################################################
    def HELP(self):
        try:
            messagebox.showinfo(title=self.name, message='Have a good day!\nPlease contact "Reza Eghbali" for more details.\n\U0001F310 Website: www.spenal.com\n\U0001F4E7 Gmail: rezaeghbali1989@gmail.com\n\u260E\uFE0F Phone: (+98) 9128179783', parent=self.root, icon='info')
        except Exception as e:
            messagebox.showerror(title='HELP', message='The Help section is not available.', parent=self.root, icon='error')
        return
    ##################################################################################################################################################################################
    def SAVE(self):
        try:
            stamp=int(time.time())
            vars_file=pd.DataFrame({'Vars':[[self.channels,self.led_from,self.led_to,self.pump_from,self.pump_to,self.valve_from,self.valve_to,self.packet_time,self.custom_color,self.shuffle_total_groups]],'Pump Range':[self.pump_range],'Custom':[self.custom],'Groups':[self.control_groups],'Elements':[self.control_elements]})
            vars_file.to_pickle('OUTPUT\\vars_{}.{}'.format(stamp, self.ex))
            messagebox.showinfo(title='SAVE', message='variables saved successfully in "OUTPUT" folder with stamp of {}.'.format(stamp), parent=self.root, icon='info')
        except Exception as e:
            messagebox.showerror(title='SAVE', message='Cannot save the variables.', parent=self.root, icon='error')
        return
    ##################################################################################################################################################################################
    def IMPORT(self):
        try:
            import_address=filedialog.askopenfilename()
            if import_address:
                try:
                    data=pd.read_pickle(import_address)
                    if list(data.columns) == ['Vars', 'Pump Range','Custom', 'Groups', 'Elements']:
                        self.channels, self.led_from, self.led_to, self.pump_from, self.pump_to, self.valve_from, self.valve_to, self.packet_time, self.custom_color, self.shuffle_total_groups=data['Vars'][0]
                        self.pump_range=data['Pump Range'][0]
                        self.custom=data['Custom'][0]
                        self.control_groups=data['Groups'][0]
                        self.control_elements=data['Elements'][0]
                        self.APP(start=False)
                    else:
                        messagebox.showerror(title='IMPORT', message='The selected database is not in the correct format.', parent=self.root, icon='error')
                except Exception as ee:
                    messagebox.showerror(title='IMPORT', message='Please select a valid database.', parent=self.root, icon='error')
        except Exception as e:
            messagebox.showerror(title='IMPORT', message='Import is not available.', parent=self.root, icon='error')
        return
    ##################################################################################################################################################################################
    def EXIT(self):
        try:
            pygame.mixer.music.stop()
            pygame.mixer.stop()
            pygame.mixer.quit()
            self.root.quit()
            self.root.destroy()
        except Exception as e:
            messagebox.showerror(title='EXIT', message='The app failed to exit.', parent=self.root, icon='error')
        return
    ##################################################################################################################################################################################
    def EXPORT(self):
        ### EXPORT helpers
        def MAP(map_count):
            ### MAP helpers
            def SORT_ELEMENTS(group_num,order_map,order_channel,order_shuffle,map_count):
                try:
                    group_elements=self.control_elements[(self.control_elements['Group']==group_num)].copy()
                    shuffle=self.control_groups['Shuffle'][self.control_groups['ID']==group_num].iloc[-1]
                    if shuffle=='Custom':
                        array_custom=self.custom[group_num]['Shuffle'].astype(int).to_list()
                        shuffle=self.mode[array_custom[map_count%len(array_custom)]]
                    if shuffle=='Chance':
                        shuffle=np.random.choice(list(set(self.mode[:-1])-set(['Chance'])))
                    if 0 < len(group_elements):
                        if  shuffle == 'First to Last 1':
                            led_elements=group_elements[group_elements['Type']=='LED'].sort_values(by=['Sort'], ascending=True).reset_index(drop=True)
                            valve_elements=group_elements[group_elements['Type']=='Valve'].sort_values(by=['Sort'], ascending=True).reset_index(drop=True)
                            for k in range(0,max(len(led_elements),len(valve_elements))):
                                order_map.append(led_elements['ID'].loc[k:k].to_list()+valve_elements['ID'].loc[k:k].to_list())
                                order_channel.append(led_elements['Channel'].loc[k:k].to_list()+valve_elements['Channel'].loc[k:k].to_list())
                                order_shuffle.append(shuffle)
                        elif  shuffle == 'First to Last 2':
                            led_elements=group_elements[group_elements['Type']=='LED'].sort_values(by=['Sort'], ascending=True).reset_index(drop=True)
                            valve_elements=group_elements[group_elements['Type']=='Valve'].sort_values(by=['Sort'], ascending=True).reset_index(drop=True)
                            for k in range(0,max(len(led_elements),len(valve_elements))):
                                order_map.append(led_elements['ID'].loc[k-1:k].to_list()+valve_elements['ID'].loc[k-1:k].to_list())
                                order_channel.append(led_elements['Channel'].loc[k-1:k].to_list()+valve_elements['Channel'].loc[k-1:k].to_list())
                                order_shuffle.append(shuffle)
                        elif  shuffle == 'First to Last 3':
                            led_elements=group_elements[group_elements['Type']=='LED'].sort_values(by=['Sort'], ascending=True).reset_index(drop=True)
                            valve_elements=group_elements[group_elements['Type']=='Valve'].sort_values(by=['Sort'], ascending=True).reset_index(drop=True)
                            for k in range(0,max(len(led_elements),len(valve_elements))):
                                order_map.append(led_elements['ID'].loc[k-2:k].to_list()+valve_elements['ID'].loc[k-2:k].to_list())
                                order_channel.append(led_elements['Channel'].loc[k-2:k].to_list()+valve_elements['Channel'].loc[k-2:k].to_list())
                                order_shuffle.append(shuffle)
                        elif  shuffle == 'First to Last 4':
                            led_elements=group_elements[group_elements['Type']=='LED'].sort_values(by=['Sort'], ascending=True).reset_index(drop=True)
                            valve_elements=group_elements[group_elements['Type']=='Valve'].sort_values(by=['Sort'], ascending=True).reset_index(drop=True)
                            for k in range(0,max(len(led_elements),len(valve_elements))):
                                order_map.append(led_elements['ID'].loc[k-3:k].to_list()+valve_elements['ID'].loc[k-3:k].to_list())
                                order_channel.append(led_elements['Channel'].loc[k-3:k].to_list()+valve_elements['Channel'].loc[k-3:k].to_list())
                                order_shuffle.append(shuffle)
                        elif  shuffle == 'First to Last 5':
                            led_elements=group_elements[group_elements['Type']=='LED'].sort_values(by=['Sort'], ascending=True).reset_index(drop=True)
                            valve_elements=group_elements[group_elements['Type']=='Valve'].sort_values(by=['Sort'], ascending=True).reset_index(drop=True)
                            for k in range(0,max(len(led_elements),len(valve_elements))):
                                order_map.append(led_elements['ID'].loc[k-4:k].to_list()+valve_elements['ID'].loc[k-4:k].to_list())
                                order_channel.append(led_elements['Channel'].loc[k-4:k].to_list()+valve_elements['Channel'].loc[k-4:k].to_list())
                                order_shuffle.append(shuffle)
                        elif  shuffle == 'First to Last Sum':
                            led_elements=group_elements[group_elements['Type']=='LED'].sort_values(by=['Sort'], ascending=True).reset_index(drop=True)
                            valve_elements=group_elements[group_elements['Type']=='Valve'].sort_values(by=['Sort'], ascending=True).reset_index(drop=True)
                            for k in range(0,max(len(led_elements),len(valve_elements))):
                                order_map.append(led_elements['ID'].loc[:k].to_list()+valve_elements['ID'].loc[:k].to_list())
                                order_channel.append(led_elements['Channel'].loc[:k].to_list()+valve_elements['Channel'].loc[:k].to_list())
                                order_shuffle.append(shuffle)
                        elif shuffle == 'Last to First 1':
                            led_elements=group_elements[group_elements['Type']=='LED'].sort_values(by=['Sort'], ascending=False).reset_index(drop=True)
                            valve_elements=group_elements[group_elements['Type']=='Valve'].sort_values(by=['Sort'], ascending=False).reset_index(drop=True)
                            length=len(led_elements['ID'])
                            for k in range(max(len(led_elements),len(valve_elements)),0,-1):
                                order_map.append(led_elements['ID'].loc[length-k:length-k].to_list()+valve_elements['ID'].loc[length-k:length-k].to_list())
                                order_channel.append(led_elements['Channel'].loc[length-k:length-k].to_list()+valve_elements['Channel'].loc[length-k:length-k].to_list())
                                order_shuffle.append(shuffle)
                        elif shuffle == 'Last to First 2':
                            led_elements=group_elements[group_elements['Type']=='LED'].sort_values(by=['Sort'], ascending=False).reset_index(drop=True)
                            valve_elements=group_elements[group_elements['Type']=='Valve'].sort_values(by=['Sort'], ascending=False).reset_index(drop=True)
                            length=len(led_elements['ID'])
                            for k in range(max(len(led_elements),len(valve_elements)),0,-1):
                                order_map.append(led_elements['ID'].loc[length-(k+1):length-k].to_list()+valve_elements['ID'].loc[length-(k+1):length-k].to_list())
                                order_channel.append(led_elements['Channel'].loc[length-(k+1):length-k].to_list()+valve_elements['Channel'].loc[length-(k+1):length-k].to_list())
                                order_shuffle.append(shuffle)
                        elif shuffle == 'Last to First 3':
                            led_elements=group_elements[group_elements['Type']=='LED'].sort_values(by=['Sort'], ascending=False).reset_index(drop=True)
                            valve_elements=group_elements[group_elements['Type']=='Valve'].sort_values(by=['Sort'], ascending=False).reset_index(drop=True)
                            length=len(led_elements['ID'])
                            for k in range(max(len(led_elements),len(valve_elements)),0,-1):
                                order_map.append(led_elements['ID'].loc[length-(k+2):length-k].to_list()+valve_elements['ID'].loc[length-(k+2):length-k].to_list())
                                order_channel.append(led_elements['Channel'].loc[length-(k+2):length-k].to_list()+valve_elements['Channel'].loc[length-(k+2):length-k].to_list())
                                order_shuffle.append(shuffle)
                        elif shuffle == 'Last to First 4':
                            led_elements=group_elements[group_elements['Type']=='LED'].sort_values(by=['Sort'], ascending=False).reset_index(drop=True)
                            valve_elements=group_elements[group_elements['Type']=='Valve'].sort_values(by=['Sort'], ascending=False).reset_index(drop=True)
                            length=len(led_elements['ID'])
                            for k in range(max(len(led_elements),len(valve_elements)),0,-1):
                                order_map.append(led_elements['ID'].loc[length-(k+3):length-k].to_list()+valve_elements['ID'].loc[length-(k+3):length-k].to_list())
                                order_channel.append(led_elements['Channel'].loc[length-(k+3):length-k].to_list()+valve_elements['Channel'].loc[length-(k+3):length-k].to_list())
                                order_shuffle.append(shuffle)
                        elif shuffle == 'Last to First 5':
                            led_elements=group_elements[group_elements['Type']=='LED'].sort_values(by=['Sort'], ascending=False).reset_index(drop=True)
                            valve_elements=group_elements[group_elements['Type']=='Valve'].sort_values(by=['Sort'], ascending=False).reset_index(drop=True)
                            length=len(led_elements['ID'])
                            for k in range(max(len(led_elements),len(valve_elements)),0,-1):
                                order_map.append(led_elements['ID'].loc[length-(k+4):length-k].to_list()+valve_elements['ID'].loc[length-(k+4):length-k].to_list())
                                order_channel.append(led_elements['Channel'].loc[length-(k+4):length-k].to_list()+valve_elements['Channel'].loc[length-(k+4):length-k].to_list())
                                order_shuffle.append(shuffle)
                        elif shuffle == 'Last to First Sum':
                            led_elements=group_elements[group_elements['Type']=='LED'].sort_values(by=['Sort'], ascending=False).reset_index(drop=True)
                            valve_elements=group_elements[group_elements['Type']=='Valve'].sort_values(by=['Sort'], ascending=False).reset_index(drop=True)
                            length=len(led_elements['ID'])
                            for k in range(max(len(led_elements),len(valve_elements)),0,-1):
                                order_map.append([led_elements['ID'].loc[:length-k],valve_elements['ID'].loc[:length-k]])
                                order_channel.append([led_elements['Channel'].loc[:length-k],valve_elements['Channel'].loc[:length-k]])
                                order_shuffle.append(shuffle)
                        elif shuffle == 'Random Shuffle 1':
                            selection=np.random.permutation(len(group_elements[group_elements['Type']=='LED']))
                            led_elements=group_elements[group_elements['Type']=='LED'].reset_index(drop=True).loc[selection].reset_index(drop=True)
                            valve_elements=group_elements[group_elements['Type']=='Valve'].reset_index(drop=True).loc[selection].reset_index(drop=True)
                            for k in range(0,max(len(led_elements),len(valve_elements))):
                                order_map.append(led_elements['ID'].loc[k:k].to_list()+valve_elements['ID'].loc[k:k].to_list())
                                order_channel.append(led_elements['Channel'].loc[k:k].to_list()+valve_elements['Channel'].loc[k:k].to_list())
                                order_shuffle.append(shuffle)
                        elif shuffle == 'Random Shuffle 2':
                            selection=np.random.permutation(len(group_elements[group_elements['Type']=='LED']))
                            led_elements=group_elements[group_elements['Type']=='LED'].reset_index(drop=True).loc[selection].reset_index(drop=True)
                            valve_elements=group_elements[group_elements['Type']=='Valve'].reset_index(drop=True).loc[selection].reset_index(drop=True)
                            for k in range(0,max(len(led_elements),len(valve_elements))):
                                order_map.append(led_elements['ID'].loc[k-1:k].to_list()+valve_elements['ID'].loc[k-1:k].to_list())
                                order_channel.append(led_elements['Channel'].loc[k-1:k].to_list()+valve_elements['Channel'].loc[k-1:k].to_list())
                                order_shuffle.append(shuffle)
                        elif shuffle == 'Random Shuffle 3':
                            selection=np.random.permutation(len(group_elements[group_elements['Type']=='LED']))
                            led_elements=group_elements[group_elements['Type']=='LED'].reset_index(drop=True).loc[selection].reset_index(drop=True)
                            valve_elements=group_elements[group_elements['Type']=='Valve'].reset_index(drop=True).loc[selection].reset_index(drop=True)
                            for k in range(0,max(len(led_elements),len(valve_elements))):
                                order_map.append(led_elements['ID'].loc[k-2:k].to_list()+valve_elements['ID'].loc[k-2:k].to_list())
                                order_channel.append(led_elements['Channel'].loc[k-2:k].to_list()+valve_elements['Channel'].loc[k-2:k].to_list())
                                order_shuffle.append(shuffle)
                        elif shuffle == 'Random Shuffle 4':
                            selection=np.random.permutation(len(group_elements[group_elements['Type']=='LED']))
                            led_elements=group_elements[group_elements['Type']=='LED'].reset_index(drop=True).loc[selection].reset_index(drop=True)
                            valve_elements=group_elements[group_elements['Type']=='Valve'].reset_index(drop=True).loc[selection].reset_index(drop=True)
                            for k in range(0,max(len(led_elements),len(valve_elements))):
                                order_map.append(led_elements['ID'].loc[k-3:k].to_list()+valve_elements['ID'].loc[k-3:k].to_list())
                                order_channel.append(led_elements['Channel'].loc[k-3:k].to_list()+valve_elements['Channel'].loc[k-3:k].to_list())
                                order_shuffle.append(shuffle)
                        elif shuffle == 'Random Shuffle 5':
                            selection=np.random.permutation(len(group_elements[group_elements['Type']=='LED']))
                            led_elements=group_elements[group_elements['Type']=='LED'].reset_index(drop=True).loc[selection].reset_index(drop=True)
                            valve_elements=group_elements[group_elements['Type']=='Valve'].reset_index(drop=True).loc[selection].reset_index(drop=True)
                            for k in range(0,max(len(led_elements),len(valve_elements))):
                                order_map.append(led_elements['ID'].loc[k-4:k].to_list()+valve_elements['ID'].loc[k-4:k].to_list())
                                order_channel.append(led_elements['Channel'].loc[k-4:k].to_list()+valve_elements['Channel'].loc[k-4:k].to_list())
                                order_shuffle.append(shuffle)
                        elif shuffle == 'Random Shuffle R':
                            selection=np.random.permutation(len(group_elements[group_elements['Type']=='LED']))
                            r=np.random.randint(0,len(group_elements[group_elements['Type']=='LED']))
                            led_elements=group_elements[group_elements['Type']=='LED'].reset_index(drop=True).loc[selection].reset_index(drop=True)
                            valve_elements=group_elements[group_elements['Type']=='Valve'].reset_index(drop=True).loc[selection].reset_index(drop=True)
                            for k in range(0,max(len(led_elements),len(valve_elements))):
                                order_map.append(led_elements['ID'].loc[k-r:k].to_list()+valve_elements['ID'].loc[k-r:k].to_list())
                                order_channel.append(led_elements['Channel'].loc[k-r:k].to_list()+valve_elements['Channel'].loc[k-r:k].to_list())
                                order_shuffle.append(shuffle)
                        elif shuffle == 'Middle to Sides':
                            led_elements=group_elements[group_elements['Type']=='LED'].reset_index(drop=True)
                            valve_elements=group_elements[group_elements['Type']=='Valve'].reset_index(drop=True)
                            if len(led_elements)%2==0:
                                mid1=len(led_elements)//2-1
                                mid2=len(led_elements)//2
                            else:
                                mid1=len(led_elements)//2
                                mid2=len(led_elements)//2
                            for k in range(0,mid1+1):
                                order_map.append([led_elements['ID'].loc[mid1-k],led_elements['ID'].loc[mid2+k],valve_elements['ID'].loc[mid1-k],valve_elements['ID'].loc[mid2+k]])
                                order_channel.append([led_elements['Channel'].loc[mid1-k],led_elements['Channel'].loc[mid2+k],valve_elements['Channel'].loc[mid1-k],valve_elements['Channel'].loc[mid2+k]])
                                order_shuffle.append(shuffle)
                        elif shuffle == 'Sides to Middle':
                            led_elements=group_elements[group_elements['Type']=='LED'].reset_index(drop=True)
                            valve_elements=group_elements[group_elements['Type']=='Valve'].reset_index(drop=True)
                            if len(led_elements)%2==0:
                                mid1=len(led_elements)//2-1
                                mid2=len(led_elements)//2
                            else:
                                mid1=len(led_elements)//2
                                mid2=len(led_elements)//2
                            for k in range(mid1,-1,-1):
                                order_map.append([led_elements['ID'].loc[mid1-k],led_elements['ID'].loc[mid2+k],valve_elements['ID'].loc[mid1-k],valve_elements['ID'].loc[mid2+k]])
                                order_channel.append([led_elements['Channel'].loc[mid1-k],led_elements['Channel'].loc[mid2+k],valve_elements['Channel'].loc[mid1-k],valve_elements['Channel'].loc[mid2+k]])
                                order_shuffle.append(shuffle)
                        elif shuffle == 'All Together':
                            led_elements=group_elements[group_elements['Type']=='LED'].reset_index(drop=True)
                            valve_elements=group_elements[group_elements['Type']=='Valve'].reset_index(drop=True)
                            order_map.append(group_elements['ID'].to_list())
                            order_channel.append(group_elements['Channel'].to_list())
                            order_shuffle.append(shuffle)
                        else:
                            messagebox.showerror(title='EXPORT MAP SORT_ELEMENTS', message='Shuffle mode is not valid.', parent=self.root, icon='error')
                except Exception as e:
                    messagebox.showerror(title='EXPORT MAP SORT_ELEMENTS', message='Cannot sort elements in group {}.'.format(group_num), parent=self.root, icon='error')
                return order_map, order_channel, order_shuffle
            ### MAP helpers
            try:
                #mode=['First to Last', 'Last to First', 'All Together']
                shuffle=self.shuffle_total_groups
                order_map=[]
                order_channel=[]
                order_shuffle=[]
                if shuffle == 0:
                    control_groups=self.control_groups[self.control_groups['ID']!='Pump'].sort_values(by=['Sort'], ascending=True).reset_index(drop=True)
                    for i in range(len(control_groups)):
                        order_map,order_channel=SORT_ELEMENTS(control_groups['ID'][i],order_map,order_channel,order_shuffle,map_count)
                elif shuffle == 1:
                    control_groups=self.control_groups[self.control_groups['ID']!='Pump'].sort_values(by=['Sort'], ascending=False).reset_index(drop=True)
                    for i in range(len(control_groups)):
                        order_map,order_channel=SORT_ELEMENTS(control_groups['ID'][i],order_map,order_channel,order_shuffle,map_count)
                elif shuffle == 2:
                    control_groups=self.control_groups[self.control_groups['ID']!='Pump'].reset_index(drop=True)
                    order_map_raw=[]
                    channel_map_raw=[]
                    shuffle_map_raw=[]
                    for i in range(len(control_groups)):
                        sub_order=[]
                        sub_channel=[]
                        sub_shuffle=[]
                        sub_order,sub_channel,sub_shuffle=SORT_ELEMENTS(control_groups['ID'][i],sub_order,sub_channel,sub_shuffle,map_count)
                        order_map_raw.append(sub_order)
                        channel_map_raw.append(sub_channel)
                        shuffle_map_raw.append(sub_shuffle)
                    max_iter=max([len(item) for item in order_map_raw])
                    for k in range(max_iter):
                        buff_order=[]
                        buff_channel=[]
                        for item in range(len(order_map_raw)):
                            buff_order.extend(order_map_raw[item][k%len(order_map_raw[item])])
                            buff_channel.extend(channel_map_raw[item][k%len(channel_map_raw[item])])
                        order_map.append(buff_order)
                        order_channel.append(buff_channel)
                        order_shuffle.append(shuffle_map_raw)
                else:
                    messagebox.showerror(title='EXPORT MAP', message='Shuffle mode is not valid.', parent=self.root, icon='error')
            except Exception as e:
                messagebox.showerror(title='EXPORT MAP', message='Cannot create frame map.', parent=self.root, icon='error')
            return order_map, order_channel,order_shuffle
        ### EXPORT helpers
        def ORDER(name, i, channel, group):
            try:
                index=self.control_elements[(self.control_elements['ID']==name) & (self.control_elements['Channel']==channel)  & (self.control_elements['Group']==group)]
                exist=False
                if len(index):
                    index=index.index[0]
                    if self.control_elements['Type'][index] == 'LED':
                        metadata[name+'_R'][i]=self.custom_color[int(self.custom.get(group)['LED'][(map_count - 1) % len(self.custom.get(group))])][0]
                        metadata[name+'_G'][i]=self.custom_color[int(self.custom.get(group)['LED'][(map_count - 1) % len(self.custom.get(group))])][1]
                        metadata[name+'_B'][i]=self.custom_color[int(self.custom.get(group)['LED'][(map_count - 1) % len(self.custom.get(group))])][2]
                    elif self.control_elements['Type'][index] == 'Valve':
                        metadata[name][i]=int(self.custom.get(group)['Valve'][(map_count - 1) % len(self.custom.get(group))])
                    elif self.control_elements['Type'][index] == 'Pump':
                        for j in range(len(pump_range)):
                            if pump_range['From Time'][j]<=i<=pump_range['To Time'][j]:
                                pump=pump_range['From Range'][j]+(i-pump_range['From Time'][j])*(pump_range['To Range'][j]-pump_range['From Range'][j])/(pump_range['To Time'][j]-pump_range['From Time'][j])
                                if pump<0:
                                    pump=0
                                elif 100<pump:
                                    pump=100
                                pump=255*pump/100
                                metadata[name][i]=int(pump)
                    exist=True
            except Exception as e:
                messagebox.showerror(title='EXPORT ORDER', message=e, parent=self.root, icon='error')
            return exist
        ### EXPORT helpers
        try:
            start_time=time.time()
            if min(np.array(self.led_from)+np.array(self.led_to)+np.array(self.pump_from)+np.array(self.pump_to)+np.array(self.valve_from)+np.array(self.valve_to))==9:
                raise Exception('Please modify byte ranges in Options first.')
            if not os.path.isfile(self.music_address):
                raise Exception('Please select an audio first.')
            for g in range(1,len(self.control_groups)):
                led_elements=self.control_elements[(self.control_elements['Type']=='LED') & (self.control_elements['Group']==self.control_groups['ID'][g])]
                valve_elements=self.control_elements[(self.control_elements['Type']=='Valve') & (self.control_elements['Group']==self.control_groups['ID'][g])]
                if len(led_elements)!=len(valve_elements):
                    messagebox.showerror(title=self.name, message='LED and Valve are not equal in group {}. Please fix this issue first.'.format(self.control_groups['ID'][g]), parent=self.root, icon='error')
                    return
                if (self.custom.get(self.control_groups['ID'][g]) is None):
                    messagebox.showerror(title=self.name, message='There is no custom for group {}. Please create a custom for this group first.'.format(self.control_groups['ID'][g]), parent=self.root, icon='error')
                    return
                else:
                    if len(self.custom.get(self.control_groups['ID'][g]))==0:
                        messagebox.showerror(title=self.name, message='There is no custom for group {}. Please create a custom for this group first.'.format(self.control_groups['ID'][g]), parent=self.root, icon='error')
                        return
            if (0 < len(self.control_groups)) and (0 < len(self.control_elements)):
                num_bytes=513
                y, sr=librosa.load(self.music_address)
                pump_range=self.pump_range.copy()
                pump_range['From Time']=(pump_range['From Time']/(0.001*self.packet_time)).astype(int)
                pump_range['To Time']=(pump_range['To Time']/(0.001*self.packet_time)).astype(int)
                name_final='{}_{}'.format(os.path.basename(self.music_address).split('/')[-1], int(time.time()))
                os.mkdir(self.result_address+'\\'+name_final)
                os.mkdir(self.result_address+'\\'+name_final+'\\raw')
                all_metadata=[]
                all_border=[]
                all_range=[]
                for ch in range(1, self.channels+1):
                    metadata=pd.DataFrame(index=range(int(len(y)//(sr*0.001*self.packet_time))))
                    sep=0
                    for col in range(1,(self.led_to[ch-1]-self.led_from[ch-1])//3+1):
                        metadata['LED{}_R'.format(col)]=np.nan
                        metadata['LED{}_G'.format(col)]=np.nan
                        metadata['LED{}_B'.format(col)]=np.nan
                        sep+=3
                    led_col_num=sep
                    for col in range(1,(self.valve_to[ch-1]-self.valve_from[ch-1])*8+1):
                        metadata['Valve{}'.format(col)]=np.nan
                        sep+=1
                    valve_col_num=sep
                    for col in range(1,self.pump_to[ch-1]-self.pump_from[ch-1]+1):
                        metadata['Pump{}'.format(col)]=np.nan
                        sep+=1
                    pump_col_num=sep
                    for i in range(int(len(y)//(sr*0.001*self.packet_time))):
                        for p in self.control_elements['ID'][self.control_elements['Type']=='Pump'].to_list():
                            ORDER(p,i,ch,'Pump')
                    for group in range(1,len(self.control_groups)):
                        if group==1:
                            i_copy=0
                        elif self.shuffle_total_groups==2:
                            i_copy=0
                        else:
                            i_copy=i_copy
                        map_count=0
                        repeated_frame=self.custom[self.control_groups['ID'][group]]['Frame'][map_count%len(self.custom[self.control_groups['ID'][group]])]//self.packet_time
                        order_map,order_channel,order_shuffle=MAP(map_count)
                        map_count+=1
                        ord_ind=0
                        max_i_copy=0
                        while i_copy<int(len(y)//(sr*0.001*self.packet_time)):
                            done=False
                            item=order_map[(ord_ind // repeated_frame) % len(order_map)]
                            ch_item=order_channel[(ord_ind // repeated_frame) % len(order_map)]
                            sh_item=order_shuffle[(ord_ind // repeated_frame) % len(order_map)]
                            if len(self.custom.get(self.control_groups['ID'][group]))<map_count:
                                break
                            if type(item) == str:
                                if ch == ch_item:
                                    exist=ORDER(item, i_copy, ch_item, self.control_groups['ID'][group])
                                    if exist:
                                        done=True
                                else:
                                    done=True
                            else:
                                for s in range(len(item)):
                                    if type(item[s]) == str:
                                        if ch == ch_item[s]:
                                            exist=ORDER(item[s], i_copy, ch_item[s], self.control_groups['ID'][group])
                                            if exist:
                                                done=True
                                        else:
                                            done=True
                                    else:
                                        for b in range(len(item[s])):
                                            if ch == ch_item[s][b]:
                                                exist=ORDER(item[s][b], i_copy, ch_item[s][b], self.control_groups['ID'][group])
                                                if exist:
                                                    done=True
                                            else:
                                                done=True
                            if done:
                                i_copy+=1
                            if (ord_ind // len(order_map)) == repeated_frame and sh_item[group-1][(map_count-1)%len(sh_item[group-1])] != 'All Together':
                                repeated_frame=self.custom[self.control_groups['ID'][group]]['Frame'][map_count%len(self.custom[self.control_groups['ID'][group]])]//self.packet_time
                                order_map,order_channel,order_shuffle=MAP(map_count)
                                map_count+=1
                                ord_ind=0
                            elif ord_ind == repeated_frame and sh_item[group-1][(map_count-1)%len(sh_item[group-1])] == 'All Together':
                                repeated_frame=self.custom[self.control_groups['ID'][group]]['Frame'][map_count%len(self.custom[self.control_groups['ID'][group]])]//self.packet_time
                                order_map,order_channel,order_shuffle=MAP(map_count)
                                map_count+=1
                                ord_ind=0
                            elif (ord_ind // len(order_map)) == repeated_frame//2 and sh_item[group-1][(map_count-1)%len(sh_item[group-1])] == 'Middle to Sides':
                                repeated_frame=self.custom[self.control_groups['ID'][group]]['Frame'][map_count%len(self.custom[self.control_groups['ID'][group]])]//self.packet_time
                                order_map,order_channel,order_shuffle=MAP(map_count)
                                map_count+=1
                                ord_ind=0
                            elif (ord_ind // len(order_map)) == repeated_frame//2 and sh_item[group-1][(map_count-1)%len(sh_item[group-1])] == 'Sides to Middle':
                                repeated_frame=self.custom[self.control_groups['ID'][group]]['Frame'][map_count%len(self.custom[self.control_groups['ID'][group]])]//self.packet_time
                                order_map,order_channel,order_shuffle=MAP(map_count)
                                map_count+=1
                                ord_ind=0
                            else:
                                ord_ind+=1
                                if (ord_ind // len(order_map)) == repeated_frame and sh_item[group-1][(map_count-1)%len(sh_item[group-1])] != 'All Together':
                                    repeated_frame=self.custom[self.control_groups['ID'][group]]['Frame'][map_count%len(self.custom[self.control_groups['ID'][group]])]//self.packet_time
                                    order_map,order_channel,order_shuffle=MAP(map_count)
                                    map_count+=1
                                    ord_ind=0
                                elif ord_ind == repeated_frame and sh_item[group-1][(map_count-1)%len(sh_item[group-1])] == 'All Together':
                                    repeated_frame=self.custom[self.control_groups['ID'][group]]['Frame'][map_count%len(self.custom[self.control_groups['ID'][group]])]//self.packet_time
                                    order_map,order_channel,order_shuffle=MAP(map_count)
                                    map_count+=1
                                    ord_ind=0
                                elif (ord_ind // len(order_map)) == repeated_frame//2 and sh_item[group-1][(map_count-1)%len(sh_item[group-1])] == 'Middle to Sides':
                                    repeated_frame=self.custom[self.control_groups['ID'][group]]['Frame'][map_count%len(self.custom[self.control_groups['ID'][group]])]//self.packet_time
                                    order_map,order_channel,order_shuffle=MAP(map_count)
                                    map_count+=1
                                    ord_ind=0
                                elif (ord_ind // len(order_map)) == repeated_frame//2 and sh_item[group-1][(map_count-1)%len(sh_item[group-1])] == 'Sides to Middle':
                                    repeated_frame=self.custom[self.control_groups['ID'][group]]['Frame'][map_count%len(self.custom[self.control_groups['ID'][group]])]//self.packet_time
                                    order_map,order_channel,order_shuffle=MAP(map_count)
                                    map_count+=1
                                    ord_ind=0
                            if max_i_copy<i_copy:
                                max_i_copy=i_copy
                        max_i_copy=max_i_copy-1
                        col_list=self.control_elements['ID'][(self.control_elements['Group']==self.control_groups['ID'][group]) & (self.control_elements['Channel']==ch)].to_list()
                        cols=[]
                        for item in col_list:
                            if ('LED' in item):
                                cols.append(item+'_R')
                                cols.append(item+'_G')
                                cols.append(item+'_B')
                            else:
                                cols.append(item)
                        metadata.loc[:max_i_copy+1,cols]=metadata[cols][:max_i_copy+1].fillna(0)
                        for c in cols:
                            metadata.loc[:,c]=metadata[c][:max_i_copy+1].to_list()*(len(metadata)//(max_i_copy+1))+metadata[c][:max_i_copy+1].to_list()[:(len(metadata)%(max_i_copy+1))]                    
                    #metadata.to_excel('test_{}.xlsx'.format(ch))
                    metadata=metadata.ffill()
                    metadata=metadata.fillna(0)
                    metadata=metadata.astype(int)
                    result=[]
                    #print(led_col_num,valve_col_num,pump_col_num)
                    for i in range(len(metadata)):
                        buff=[0]*num_bytes
                        buff[self.led_from[ch-1]:self.led_to[ch-1]]=metadata.iloc[i,0:led_col_num].to_list()
                        valve_buff=np.array_split(metadata.iloc[i,led_col_num:valve_col_num].to_list(), int(self.valve_to[ch-1]-self.valve_from[ch-1]))
                        valve_buff=[int(''.join(str(x) for x in list(chunk.astype(int))[::-1]),2) for chunk in valve_buff]
                        buff[self.valve_from[ch-1]:self.valve_to[ch-1]]=valve_buff
                        buff[self.pump_from[ch-1]:self.pump_to[ch-1]]=metadata.iloc[i,valve_col_num:pump_col_num].to_list()
                        result.extend(buff[1:])
                    result=bytearray(result)
                    with open(self.result_address+'\\{}\\raw\\output_ch{}.DMX'.format(name_final,ch), 'wb') as res_file:
                        res_file.write(result)
                    metadata.to_excel(self.result_address+'\\{}\\raw\\metadata_ch{}.xlsx'.format(name_final, ch))
                    all_metadata.append(metadata)
                    all_border.append([led_col_num,valve_col_num,pump_col_num])
                    all_range.append([self.led_from[ch-1],self.led_to[ch-1],self.valve_from[ch-1],self.valve_to[ch-1],self.pump_from[ch-1],self.pump_to[ch-1]])
                all_channels=pd.DataFrame({'metadata':all_metadata, 'border':all_border, 'range':all_range})
                all_channels.to_pickle(self.result_address+'\\{}\\channels_{}.{}'.format(name_final, name_final, self.ex))
                vars_file=pd.DataFrame({'Vars':[[self.channels,self.led_from,self.led_to,self.pump_from,self.pump_to,self.valve_from,self.valve_to,self.packet_time,self.custom_color,self.shuffle_total_groups]],'Pump Range':[self.pump_range],'Custom':[self.custom],'Groups':[self.control_groups],'Elements':[self.control_elements]})
                vars_file.to_pickle(self.result_address+'\\{}\\vars_{}.{}'.format(name_final, name_final, self.ex))
                end_time=time.time()
                response=messagebox.askquestion(title='Completed', message='Process has completed successfully in {} seconds. For seeing the results go to:\n{}\nDo you want to start division of the channels?'.format(int(end_time-start_time),self.result_address+'\\'+name_final), parent=self.root, icon='info') 
                if response == 'yes':
                    self.DIVISION(merge_address=self.result_address+'\\{}\\channels_{}.{}'.format(name_final, name_final, self.ex))
            else:
                raise Exception('Please add some groups and elements before continue.')
        except Exception as e:
            messagebox.showerror(title='EXPORT', message=e, parent=self.root, icon='error')
        return
    ##################################################################################################################################################################################
    def REFRESH(self, time_pos, label_time):
        try:
            if self.load:
                pos=round(self.last_pos+pygame.mixer.music.get_pos()/1000, 2)
                time_pos.set(float(pos))
                if round(self.audio_length, 2) <= pos:
                    self.play=not self.play
                    time_pos.set(float(0))
                    pos=0
                    self.music_pos=0
                    self.last_pos=0
                    pygame.mixer.music.stop()
                    pygame.mixer.music.play(start=0)
                    pygame.mixer.music.pause()
                label_time.config(text='    {:.2f} / {:.2f}    '.format(pos, round(self.audio_length, 2)))
        except Exception as e:
            pass
        self.root.after(10, lambda: self.REFRESH(time_pos, label_time))
    ##################################################################################################################################################################################    
    def APP(self, start=True):
        ### APP helpers
        def UPLOAD():
            try:
                music_address=filedialog.askopenfilename(filetypes=(('Audio Files', '.mp3 .flac .wav .ogg'), ('All Files', '*.*')))
                if music_address:
                    self.music_address=music_address
                    audio=pygame.mixer.Sound(self.music_address)
                    pygame.mixer.music.load(self.music_address)
                    pygame.mixer.music.play(start=self.music_pos)
                    pygame.mixer.music.pause()
                    self.load=True
                    self.audio_length=audio.get_length()
                    label_container_player_music.config(text=' {} '.format(os.path.basename(self.music_address).split('/')[-1]))
                    time_pos.config(to=audio.get_length())
                    label_time.config(text='    {:.2f} / {:.2f}    '.format(0, round(audio.get_length(), 2)))
            except Exception as e:
                messagebox.showerror(title='APP UPLOAD', message='The app failed to upload the music.', parent=self.root, icon='error')
            return
        ### APP helpers
        def TOGGLE(pos):
            try:
                if 0.02<abs(float(pos)-round(self.last_pos+pygame.mixer.music.get_pos()/1000, 2)):
                    pygame.mixer.music.play(start=float(pos))
                    time_pos.set(float(pos))
                    self.last_pos=float(pos)
                    if self.play:
                        pygame.mixer.music.unpause()
                    else:
                        pygame.mixer.music.pause()
            except Exception as e:
                messagebox.showerror(title='APP TOGGLE', message='Audio cannot be shifted.', parent=self.root, icon='error')
            return
        ### APP helpers
        def PLAY():
            try:
                if self.load:
                    self.play=not self.play
                    if self.play:
                        pygame.mixer.music.unpause()
                    else:
                        pygame.mixer.music.pause()
            except Exception as e:
                messagebox.showerror(title='APP PLAY', message='Audio cannot be played/paused.', parent=self.root, icon='error')
            return
        ### APP helpers
        def SHUFFLE(btn):
            try:
                mode=['First to Last', 'Last to First', 'All Together']
                self.shuffle_total_groups += 1
                if len(mode)-1 < self.shuffle_total_groups:
                    self.shuffle_total_groups=0
                btn.config(text=mode[self.shuffle_total_groups])
            except Exception as e:
                messagebox.showerror(title='APP SHUFFLE', message='Cannot change shuffle mode.', parent=self.root, icon='error')
            return
        ### APP helpers
        def SHUFFLE_COMBOBOX_CHANGE(event,combobox, group_num):
            try:
                self.control_groups['Shuffle'][group_num] = combobox.get()
            except Exception as e:
                messagebox.showerror(title='APP SHUFFLE_COMBOBOX_CHANGE', message='Cannot change shuffle mode.', parent=self.root, icon='error')
            return
        ### APP helpers
        def CONTROL_FORM():
            try:
                for child in label_container_control.winfo_children():
                    child.destroy()
                canvas_total=Canvas(master=label_container_control, bg=self.colors['Control Bar'])
                canvas_total.place(relx=0, rely=0, relwidth=1, relheight=1)
                yscrollbar_total=ttk.Scrollbar(master=label_container_control, orient=VERTICAL, command=canvas_total.yview)
                yscrollbar_total.place(relx=0.99, rely=0, relwidth=0.01, relheight=1)
                canvas_total.configure(yscrollcommand=yscrollbar_total.set, highlightbackground=self.colors['Control Bar'], highlightcolor=self.colors['Control Bar'])
                width, height=int(0.98*label_container_control.winfo_width()), label_container_control.winfo_height()                
                data_group=self.control_groups.sort_values(by=['Sort']).reset_index(drop=True)
                for i in range(len(data_group)):
                    if data_group['ID'][i]=='Pump':
                        section=LabelFrame(master=canvas_total, text='  {}  '.format(data_group['ID'][i]), width=width, height=height//2.5, font=('Times', 12, 'bold'), bd=5, bg=self.colors['Control Bar'])
                        canvas1=Canvas(master=section, bg=self.colors['Control Bar'])
                        canvas1.place(relx=0, rely=0.25, relwidth=0.95, relheight=0.42)
                        xscrollbar1=ttk.Scrollbar(master=section, orient=HORIZONTAL, command=canvas1.xview)
                        xscrollbar1.place(relx=0, rely=0.67, relwidth=0.95, relheight=0.07)
                        canvas1.configure(xscrollcommand=xscrollbar1.set, highlightbackground=self.colors['Control Bar'], highlightcolor=self.colors['Control Bar'])
                        data_element1=self.control_elements[(self.control_elements['Group']==data_group['ID'][i]) & (self.control_elements['Type']=='Pump')].sort_values(by=['Sort']).reset_index(drop=True)
                        for j in range(len(data_element1)):
                            button_element1=Button(master=canvas1, text='{} {}\nch: {}\n{}'.format(data_element1['Type'][j], data_element1['ID'][j].replace('Pump',''), data_element1['Channel'][j],data_element1['Sort'][j]+1), bg=self.colors[data_element1['Type'][j]], width=8, font=('Times', 11, 'bold'), command=lambda group=data_group.iloc[i], data=data_element1.iloc[j]: ELEMENT_SETTINGS(group, data))
                            canvas1.create_window(90*j, 0, anchor=NW, window=button_element1)
                        canvas1.bind('<Configure>', canvas1.configure(scrollregion=canvas1.bbox('all')))
                        button_add_element=Button(master=section, text='\u2795', bg=self.colors['Red'], font=('Times', 16, 'bold'), command=lambda group=data_group.iloc[i], data='': ELEMENT_SETTINGS(group, data))
                        button_add_element.place(relx=0.975, rely=-0.03, relwidth=0.02, relheight=0.17)
                    else:
                        section=LabelFrame(master=canvas_total, text='  {}  '.format(data_group['ID'][i]), width=width, height=height//2.5, font=('Times', 12, 'bold'), bd=5, bg=self.colors['Control Bar'])
                        canvas2=Canvas(master=section, bg=self.colors['Control Bar'])
                        canvas2.place(relx=0, rely=0.01, relwidth=0.95, relheight=0.42)
                        xscrollbar2=ttk.Scrollbar(master=section, orient=HORIZONTAL, command=canvas2.xview)
                        xscrollbar2.place(relx=0, rely=0.42, relwidth=0.95, relheight=0.07)
                        canvas2.configure(xscrollcommand=xscrollbar2.set, highlightbackground=self.colors['Control Bar'], highlightcolor=self.colors['Control Bar'])
                        data_element2=self.control_elements[(self.control_elements['Group']==data_group['ID'][i]) & (self.control_elements['Type']=='LED')].sort_values(by=['Sort']).reset_index(drop=True)
                        for j in range(len(data_element2)):
                            button_element2=Button(master=canvas2, text='{} {}\nch: {}\n{}'.format(data_element2['Type'][j], data_element2['ID'][j].replace('LED',''), data_element2['Channel'][j],data_element2['Sort'][j]+1), bg=self.colors[data_element2['Type'][j]], width=8, font=('Times', 11, 'bold'), command=lambda group=data_group.iloc[i], data=data_element2.iloc[j]: ELEMENT_SETTINGS(group, data))
                            canvas2.create_window(90*j, 0, anchor=NW, window=button_element2)
                        canvas3=Canvas(master=section, bg=self.colors['Control Bar'])
                        canvas3.place(relx=0, rely=0.51, relwidth=0.95, relheight=0.42)
                        xscrollbar3=ttk.Scrollbar(master=section, orient=HORIZONTAL, command=canvas3.xview)
                        xscrollbar3.place(relx=0, rely=0.92, relwidth=0.95, relheight=0.07)
                        canvas3.configure(xscrollcommand=xscrollbar3.set, highlightbackground=self.colors['Control Bar'], highlightcolor=self.colors['Control Bar'])
                        data_element3=self.control_elements[(self.control_elements['Group']==data_group['ID'][i]) & (self.control_elements['Type']=='Valve')].sort_values(by=['Sort']).reset_index(drop=True)
                        for j in range(len(data_element3)):
                            button_element3=Button(master=canvas3, text='{} {}\nch: {}\n{}'.format(data_element3['Type'][j], data_element3['ID'][j].replace('Valve',''), data_element3['Channel'][j],data_element3['Sort'][j]+1), bg=self.colors[data_element3['Type'][j]], width=8, font=('Times', 11, 'bold'), command=lambda group=data_group.iloc[i], data=data_element3.iloc[j]: ELEMENT_SETTINGS(group, data))
                            canvas3.create_window(90*j, 0, anchor=NW, window=button_element3)
                        canvas2.bind('<Configure>', canvas2.configure(scrollregion=canvas2.bbox('all')))
                        canvas3.bind('<Configure>', canvas3.configure(scrollregion=canvas3.bbox('all')))
                        button_setting_group=Button(master=section, text='\u2699\uFE0F', bg=self.colors['Red'], font=('Times', 16, 'bold'), command=lambda data=data_group.iloc[i]: GROUP_SETTINGS(data))
                        button_setting_group.place(relx=0.975, rely=-0.03, relwidth=0.02, relheight=0.17)
                        button_add_element=Button(master=section, text='\u2795', bg=self.colors['Red'], font=('Times', 16, 'bold'), command=lambda group=data_group.iloc[i], data='': ELEMENT_SETTINGS(group, data))
                        button_add_element.place(relx=0.975, rely=0.17, relwidth=0.02, relheight=0.17)
                        button_add_custom=Button(master=section, text='\u267E', bg=self.colors['Red'], font=('Times', 16, 'bold'), command=lambda group=data_group.iloc[i]: CUSTOM(group))
                        button_add_custom.place(relx=0.975, rely=0.77, relwidth=0.02, relheight=0.17)                        
                    canvas_total.create_window(0, i*1.05*height//2.6, anchor=NW, window=section)
                canvas_total.bind('<Configure>', canvas_total.configure(scrollregion=canvas_total.bbox('all')))
                button_add_group=Button(master=labelframe_control, text='Add Group', bg=self.colors['Buttons'], font=('Times', 12, 'bold'), command=lambda data='': GROUP_SETTINGS(data))
                button_add_group.place(relx=0.35, rely=0.92, relwidth=0.10, relheight=0.06)
                button_shuffle_all=Button(master=labelframe_control, text=['First to Last', 'Last to First', 'All Together'][self.shuffle_total_groups], bg=self.colors['Buttons'], font=('Times', 12, 'bold'))
                button_shuffle_all.place(relx=0.55, rely=0.92, relwidth=0.10, relheight=0.06)
                button_shuffle_all['command']=lambda btn=button_shuffle_all:SHUFFLE(btn)
            except Exception as e:
                messagebox.showerror(title='APP CONTROL_FORM', message='Control Bar is not accessable.', parent=self.root, icon='error')
            return
        ### APP helpers
        def RANGE(names):
            try:
                list_names=[]
                if ('-' in names) and (names.count('-')==1) and (not ',' in names):
                    names=names.split('-')
                    if int(names[0]) <= int(names[1]):
                        list_names=[str(k) for k in range(int(names[0]),int(names[1])+1)]
                    else:
                        messagebox.showerror(title=self.name, message='Higher ranges is lower than lower range for group add range.', parent=self.root, icon='error')
                        return list_names
                elif (not '-' in names) and (names.count(',')!=0) and (',' in names):
                    list_names=names.split(',')
                else:
                    list_names.append(names)
            except Exception as e:
                messagebox.showerror(title='APP RANGE', message='Cannot use range adding.', parent=self.root, icon='error')
            return list_names
        ### APP helpers
        def GROUP_SETTINGS(data=''):
            ### GROUP_SETTINGS helpers
            def ADD_GROUP():
                try:
                    names=entry_id.get()
                    poses=entry_pos.get()
                    names=RANGE(names)
                    poses=RANGE(poses)
                    if (len(names) != len(poses)) and (len(poses) == 1):
                        poses=[str(k) for k in range(int(poses[0]),int(poses[0])+len(names))]
                    elif (len(names) != len(poses)) and (len(poses) != 1):
                        messagebox.showerror(title=self.name, message='Cannot use range adding.', parent=self.root, icon='error')
                    for i in range(len(names)):
                        name=names[i]
                        pos=poses[i]
                        if name!='' and type(int(pos))==int:
                            pos=int(pos)
                            if pos < 0:
                                messagebox.showerror(title=self.name, message='Invalid Group Pos number.', parent=self.root, icon='error')
                            elif name in self.control_groups['ID'].tolist():
                                messagebox.showerror(title=self.name, message='Group ID must be unique.', parent=self.root, icon='error')
                            else:
                                if 0 < len(self.control_groups):
                                    line=pd.DataFrame({'ID':name, 'Position':len(self.control_groups), 'Sort':pos, 'Shuffle':self.mode[-1]}, index=[pos])
                                    shuffle_group_pump=self.control_groups['Shuffle'][0]
                                    self.control_groups=self.control_groups.sort_values(by=['Sort'])[1:].reset_index(drop=True)
                                    self.control_groups=pd.concat([self.control_groups.iloc[:pos], line, self.control_groups.iloc[pos:]]).reset_index(drop=True)
                                    self.control_groups['Sort']=range(len(self.control_groups))
                                    self.control_groups.loc[-1]=['Pump',0,-np.inf,shuffle_group_pump]
                                    self.control_groups.index = self.control_groups.index + 1 
                                    self.control_groups.sort_index(inplace=True) 
                                else:
                                    self.control_groups=pd.DataFrame({'ID':name, 'Position':1, 'Sort':0, 'Shuffle':self.mode[-1]}, index=[0])
                            CONTROL_FORM()
                            entry_id.delete(0, END)
                            entry_pos.delete(0, END)
                            entry_pos.insert(0, len(self.control_groups))
                        else:
                            messagebox.showerror(title='APP ADD_GROUP', message='Please enter a valid Group ID and Pos.', parent=self.root, icon='error')
                except Exception as e:
                    messagebox.showerror(title='APP ADD_GROUP', message='Group cannot be added.', parent=self.root, icon='error')
                return
            ### GROUP_SETTINGS helpers
            def EDIT_GROUP():
                try:
                    pos=entry_pos.get()
                    name=entry_id.get()
                    if name!='' and type(int(pos))==int:
                        pos=int(pos)-1
                        if pos < 0:
                            messagebox.showerror(title=self.name, message='Invalid Group Pos number.', parent=self.root, icon='error')
                        elif (name in self.control_groups['ID'].tolist()) and (self.control_groups['ID'][self.control_groups['Position']==pos_id].iloc[-1]!=name):
                            messagebox.showerror(title=self.name, message='Group ID must be unique.', parent=self.root, icon='error')
                        else:
                            shuffle_group_pump=self.control_groups['Shuffle'][0]
                            group_index=self.control_groups[self.control_groups['Position']==pos_id].index[-1]
                            shuffle=self.control_groups['Shuffle'][group_index]
                            pre_id=self.control_groups['ID'][group_index]
                            self.control_groups=self.control_groups.drop(group_index)
                            self.control_groups=self.control_groups.sort_values(by=['Sort'])[1:].reset_index(drop=True)
                            self.control_groups['Sort']=range(len(self.control_groups))
                            line=pd.DataFrame({'ID':name, 'Position':pos_id, 'Sort':pos, 'Shuffle':shuffle}, index=[pos])
                            self.control_groups=self.control_groups.sort_values(by=['Sort']).reset_index(drop=True)
                            self.control_groups=pd.concat([self.control_groups.iloc[:pos], line, self.control_groups.iloc[pos:]]).reset_index(drop=True)
                            self.control_groups['Sort']=range(len(self.control_groups))
                            self.control_elements.loc[self.control_elements['Group']==pre_id,'Group']=name
                            self.control_groups.loc[-1]=['Pump',0,-np.inf,shuffle_group_pump]
                            self.control_groups.index = self.control_groups.index + 1
                            self.control_groups.sort_index(inplace=True)
                            self.custom.update({name:self.custom.get(pre_id)})
                            self.custom.pop(pre_id)
                            CONTROL_FORM()
                            window.destroy()
                    else:
                        messagebox.showerror(title='APP EDIT_GROUP', message='Please enter a valid Group ID and Pos.', parent=self.root, icon='error')
                except Exception as e:
                    messagebox.showerror(title='APP EDIT_GROUP', message='Group cannot be editted.', parent=self.root, icon='error')
                return
            ### GROUP_SETTINGS helpers
            def DELETE_GROUP():
                try:
                    name=entry_id.get()
                    if name in self.control_groups['ID'].tolist():
                        group_index=self.control_groups[self.control_groups['ID']==name].index
                        self.control_groups=self.control_groups.drop(group_index)
                        self.control_groups=self.control_groups.sort_values(by=['Sort'])
                        self.control_groups['Sort']=range(len(self.control_groups))
                        elements_index=self.control_elements[self.control_elements['Group']==name].index
                        self.control_elements=self.control_elements.drop(elements_index)
                        try:
                            self.custom.pop(name)
                        except:
                            pass
                        CONTROL_FORM()
                        window.destroy()
                    else:
                        messagebox.showerror(title='APP DELETE_GROUP', message='Group cannot be found.', parent=self.root, icon='error')
                except Exception as e:
                    messagebox.showerror(title='APP DELETE_GROUP', message='Group cannot be deleted.', parent=self.root, icon='error')
                return
            ### GROUP_SETTINGS helpers
            try:
                window=Toplevel(bd=10, bg=self.colors['Group Form'])
                if len(data):
                    pos_length=len(self.control_groups)
                    name=data['ID']
                    pos=data['Sort']+1
                    pos_id=data['Position']
                    window.title('Edit Group')
                else:
                    pos_length=len(self.control_groups)
                    name=''
                    pos=pos_length
                    window.title('Add Group')
                window.resizable(0, 0)
                window.grab_set()
                window.geometry('300x200')
                window.iconbitmap(self.icon)
                Label(master=window, text='', bg=self.colors['Group Form']).pack(side=LEFT, fill=BOTH, expand=True)
                Label(master=window, text='', bg=self.colors['Group Form']).pack(side=RIGHT, fill=BOTH, expand=True)
                Label(master=window, text='', bg=self.colors['Group Form']).pack(fill=BOTH, expand=True)
                labelframe_id=LabelFrame(master=window, text='Group ID:   ', labelanchor=W, bd=0, font=('Times', 12, 'bold'), bg=self.colors['Group Form'])
                labelframe_id.pack(fill=BOTH, expand=True)
                entry_id=Entry(master=labelframe_id, justify=CENTER, width=10)
                entry_id.pack()
                entry_id.insert(0, name)
                Label(master=window, text='', bg=self.colors['Group Form']).pack(fill=BOTH, expand=True)
                labelframe_pos=LabelFrame(master=window, text='Group Pos: ', labelanchor=W, bd=0, font=('Times', 12, 'bold'), bg=self.colors['Group Form'])
                labelframe_pos.pack(fill=BOTH, expand=True)
                entry_pos=Entry(master=labelframe_pos, justify=CENTER, width=10)
                entry_pos.pack()
                entry_pos.insert(0, int(pos))
                Label(master=window, text='', bg=self.colors['Group Form']).pack(fill=BOTH, expand=True)
                label_container_btn=Label(master=window, text='', bg=self.colors['Group Form'])
                label_container_btn.pack(fill=BOTH, expand=True)
                if len(data):
                    button_edit=Button(master=label_container_btn, text='   Edit   ', bg=self.colors['Green'], font=('Times', 12, 'bold'), command=EDIT_GROUP)
                    button_edit.pack(side=LEFT)
                    button_delete=Button(master=label_container_btn, text='Delete', bg=self.colors['Red'], font=('Times', 12, 'bold'), command=DELETE_GROUP)
                    button_delete.pack(side=RIGHT)
                else:
                    button_add=Button(master=label_container_btn, text='   Add   ', bg=self.colors['Green'], font=('Times', 12, 'bold'), command=ADD_GROUP)
                    button_add.pack()
                Label(master=window, text='', bg=self.colors['Group Form']).pack(fill=BOTH, expand=True)
            except Exception as e:
                messagebox.showerror(title='APP GROUP_SETTINGS', message='Cannot edit group settings.', parent=self.root, icon='error')
            return
        ### APP helpers
        def CUSTOM(group):
            try:
                group=group['ID']
                if self.custom.get(group) is not None:
                    data=self.custom.get(group)
                else:
                    data=pd.DataFrame(columns=['Shuffle', 'Frame', 'LED', 'Valve'])
                data.to_excel('custom_group_{}.xlsx'.format(group),index=False)
                response=False
                while not response:
                    os.system('start "excel" "{}\\custom_group_{}.xlsx"'.format(os.getcwd(), group))
                    response=messagebox.askyesno(title='EXCEL SAVE WARNING', message='Did you fill and save custom_order_map.xlsx?\nBe sure to save and close the excel file.', parent=self.root, icon='warning')
                    custom_raw=pd.read_excel('custom_group_{}.xlsx'.format(group))
                    if not (all((0<=custom_raw['Shuffle']) & (custom_raw['Shuffle']<len(self.mode)-1))):
                        response=False
                        messagebox.showerror(title='CUSTOM {}'.format(group), message='Custom Shuffle values should be between 0 and {}.\nPlease try agin.'.format(str(len(self.mode)-2)), parent=self.root, icon='error')
                    if not (all((0<=custom_raw['LED']) & (custom_raw['LED']<len(self.custom_color)))):
                        response=False
                        messagebox.showerror(title='CUSTOM {}'.format(group), message='Custom LED values should be between 0 and {}.\nPlease try agin.'.format(str(len(self.custom_color)-1)), parent=self.root, icon='error')
                    if not (all(custom_raw['Frame']%self.packet_time==0)):
                        response=False
                        messagebox.showerror(title='CUSTOM {}'.format(group), message='Custom Frame values should be divided to packet time {} ms.\nPlease try agin.'.format(self.packet_time), parent=self.root, icon='error')
                    if not (all(custom_raw['Valve'].isin([0,1]))):
                        response=False
                        messagebox.showerror(title='CUSTOM {}'.format(group), message='Custom Valve values are either 0 or 1.\nPlease try agin.', parent=self.root, icon='error')
                    self.custom[group]=custom_raw
                os.remove('custom_group_{}.xlsx'.format(group))
                messagebox.showinfo(title='CUSTOM {}'.format(group), message='Custom {} editted successfully.'.format(group), parent=self.root, icon='info')
            except Exception as e:
                messagebox.showerror(title='APP CUSTOM', message=e, parent=self.root, icon='error')
            return
        ### APP helpers
        def ELEMENT_SETTINGS(group, data=''):
            ### ELEMENT_SEETTINGS helpers
            def ADD_ELEMENT():
                try:
                    element_type=var_type.get()
                    element_group=combobox_group.get()
                    element_channel=int(combobox_channel.get())
                    names=entry_id.get()
                    poses=entry_pos.get()
                    names=RANGE(names)
                    poses=RANGE(poses)
                    if (len(names) != len(poses)) and (len(poses) == 1):
                        poses=[str(k) for k in range(int(poses[0]),int(poses[0])+len(names))]
                    elif (len(names) != len(poses)) and (len(poses) != 1):
                        messagebox.showerror(title=self.name, message='Cannot use range adding.', parent=self.root, icon='error')
                    for i in range(len(names)):
                        name=names[i]
                        pos=poses[i]
                        try:
                            name=int(name)
                            pos=int(pos)-1
                            if pos < 0:
                                messagebox.showerror(title=self.name, message='Invalid Element Pos number.', parent=self.root, icon='error')
                            elif (element_type == 'LED') and ((not (1 <= name <= (self.led_to[element_channel-1]-self.led_from[element_channel-1])/3)) or (self.led_to[element_channel-1] == self.led_from[element_channel-1])):
                                messagebox.showerror(title=self.name, message='LED is out of byte range.', parent=self.root, icon='error')
                            elif (element_type == 'Pump') and ((not (1 <= name <= (self.pump_to[element_channel-1]-self.pump_from[element_channel-1]))) or (self.pump_to[element_channel-1] == self.pump_from[element_channel-1])):
                                messagebox.showerror(title=self.name, message='Pump is out of byte range.', parent=self.root, icon='error')
                            elif (element_type == 'Valve') and ((not (1 <= name <= 8*(self.valve_to[element_channel-1]-self.valve_from[element_channel-1]))) or (self.valve_to[element_channel-1] == self.valve_from[element_channel-1])):
                                messagebox.showerror(title=self.name, message='Valve is out of byte range.', parent=self.root, icon='error')
                            elif (element_type+str(name) in self.control_elements['ID'].tolist()) and (element_channel in self.control_elements[self.control_elements['ID']==element_type+str(name)]['Channel'].tolist()):
                                messagebox.showerror(title=self.name, message='Element ID must be unique in each channel.', parent=self.root, icon='error')
                            else:
                                if 0 < len(self.control_elements):
                                    self.control_elements[(self.control_elements['Group']==element_group) & (self.control_elements['Type']==element_type)]['Sort'][pos>=self.control_elements[(self.control_elements['Group']==element_group) & (self.control_elements['Type']==element_type)]['Sort']] += 1
                                    self.control_elements.loc[len(self.control_elements)]={'Type':element_type, 'ID':element_type+str(name), 'Position':len(self.control_elements), 'Sort':pos, 'Channel': element_channel, 'Group':element_group}
                                    self.control_elements=self.control_elements.sort_values(by=['Sort']).reset_index(drop=True)
                                    self.control_elements.loc[(self.control_elements['Group']==element_group) & (self.control_elements['Type']==element_type),'Sort']=list(range(len(self.control_elements[(self.control_elements['Group']==element_group) & (self.control_elements['Type']==element_type)]['Sort'])))
                                else:
                                    self.control_elements=pd.DataFrame({'Type':element_type, 'ID':element_type+str(name), 'Position':0, 'Sort':0, 'Channel': element_channel, 'Group':element_group}, index=[0])
                                CONTROL_FORM()
                                entry_id.delete(0, END)
                                entry_pos.delete(0, END)
                                entry_pos.insert(0, len(self.control_elements[(self.control_elements['Group']==element_group) & (self.control_elements['Type']==element_type)])+1)
                        except Exception as ee:
                            messagebox.showerror(title='APP ADD_ELEMENT', message='Please enter a valid Element ID and Pos as integer.', parent=self.root, icon='error')
                except Exception as e:
                    messagebox.showerror(title='APP ADD_ELEMENT', message='Element cannot be added.', parent=self.root, icon='error')
                return
            ### ELEMENT_SETTINGS helpers
            def EDIT_ELEMENT():
                try:
                    element_type=var_type.get()
                    element_group=combobox_group.get()
                    element_channel=int(combobox_channel.get())
                    pos=entry_pos.get()
                    name=entry_id.get()
                    if name!='' and type(int(pos))==int:
                        name=int(name)
                        pos=int(pos)-1
                        if (element_type == 'LED') and (not (1 <= name <= (self.led_to[element_channel-1]-self.led_from[element_channel-1])/3)):
                            messagebox.showerror(title=self.name, message='LED is out of byte range.', parent=self.root, icon='error')
                        elif (element_type == 'Pump') and (not (1 <= name <= (self.pump_to[element_channel-1]-self.pump_from[element_channel-1]))):
                            messagebox.showerror(title=self.name, message='Pump is out of byte range.', parent=self.root, icon='error')
                        elif (element_type == 'Valve') and (not (1 <= name <= 8*(self.valve_to[element_channel-1]-self.valve_from[element_channel-1]))):
                            messagebox.showerror(title=self.name, message='Valve is out of byte range.', parent=self.root, icon='error')
                        elif pos < 0:
                            messagebox.showerror(title=self.name, message='Invalid Element Pos number.', parent=self.root, icon='error')
                        elif (element_type+str(name) in self.control_elements['ID'].tolist()) and (self.control_elements['ID'][self.control_elements['Position']==element_pos_id].iloc[-1] != element_type+str(name)) and (element_channel in self.control_elements[self.control_elements['ID']==element_type+str(name)]['Channel'].tolist()):
                            messagebox.showerror(title=self.name, message='Element ID must be unique in each channel.', parent=self.root, icon='error')
                        else:
                            element_index=self.control_elements[self.control_elements['Position']==element_pos_id].index[-1]
                            pre_group=self.control_elements['Group'][element_index]
                            self.control_elements['Sort'][self.control_elements[(self.control_elements['Group']==element_group) & (self.control_elements['Type']==element_type)]['Sort'][pos <= self.control_elements[(self.control_elements['Group']==element_group) & (self.control_elements['Type']==element_type)]['Sort']].index] += 1
                            self.control_elements.loc[element_index]={'Type':element_type, 'ID':element_type+str(name), 'Position':int(element_pos_id), 'Sort':pos, 'Channel':element_channel, 'Group':element_group}
                            self.control_elements=self.control_elements.sort_values(by=['Sort'])
                            self.control_elements[(self.control_elements['Group']==element_group) & (self.control_elements['Type']==element_type),'Sort']=list(range(len(self.control_elements[(self.control_elements['Group']==element_group) & (self.control_elements['Type']==element_type)]['Sort'])))
                            self.control_elements[(self.control_elements['Group']==pre_group) & (self.control_elements['Type']==element_type),'Sort']=list(range(len(self.control_elements[(self.control_elements['Group']==pre_group) & (self.control_elements['Type']==element_type)])))
                            CONTROL_FORM()
                            window.destroy()
                    else:
                        messagebox.showerror(title='APP EDIT_ELEMENT', message='Please enter a valid Element ID and Pos.', parent=self.root, icon='error')
                except Exception as e:
                    messagebox.showerror(title='APP EDIT_ELEMENT', message='Element cannot be editted.', parent=self.root, icon='error')
                return
            ### ELEMENT_SETTINGS helpers
            def DELETE_ELEMENT():
                try:
                    element_type=var_type.get()
                    group_id=str(combobox_group.get())
                    channel=int(combobox_channel.get())
                    name=entry_id.get()
                    if element_type+name in self.control_elements['ID'].tolist():
                        element_index=self.control_elements[(self.control_elements['ID']==element_type+str(name)) & (self.control_elements['Group']==group_id) & (self.control_elements['Channel']==channel)].index
                        self.control_elements=self.control_elements.drop(element_index)
                        self.control_elements=self.control_elements.sort_values(by=['Sort'])
                        self.control_elements.loc[(self.control_elements['Group']==group_id) & (self.control_elements['Type']==element_type),'Sort']=list(range(len(self.control_elements[(self.control_elements['Group']==group_id) & (self.control_elements['Type']==element_type)])))
                        CONTROL_FORM()
                        window.destroy()
                    else:
                        messagebox.showerror(title='APP DELETE_ELEMENT', message='{} {} cannot be found in group {}.'.format(element_type, name, group_id), parent=self.root, icon='error')
                except Exception as e:
                    messagebox.showerror(title='APP DELETE_ELEMENT', message='Element {} {} cannot be deleted.'.format(element_type, name), parent=self.root, icon='error')
                return
            ### ELEMENT_SETTINGS helpers
            def CHANGE_COMBOBOX(event):
                try:
                    element_type=var_type.get()
                    element_group=combobox_group.get()
                    entry_pos.delete(0,END)
                    entry_pos.insert(0, len(self.control_elements[(self.control_elements['Group']==element_group) & (self.control_elements['Type']==element_type)])+1)
                except Exception as e:
                    messagebox.showerror(title='APP CHANGE_COMBOBOX', message=e, parent=self.root, icon='error')
                return
            ### ELEMENT_SETTINGS helpers
            def CHANGE_RADIOBUTTON():
                try:
                    element_type=var_type.get()
                    element_group=combobox_group.get()
                    entry_pos.delete(0,END)
                    entry_pos.insert(0, len(self.control_elements[(self.control_elements['Group']==element_group) & (self.control_elements['Type']==element_type)])+1)
                except Exception as e:
                    messagebox.showerror(title='APP CHANGE_RADIOBUTTON', message=e, parent=self.root, icon='error')
                return
            ### ELEMENT_SETTINGS helpers
            try:
                window=Toplevel(bd=10, bg=self.colors['Element Form'])
                if len(data):
                    element_type=data['Type']
                    element_name=data['ID']
                    element_channel=data['Channel']
                    element_group=data['Group']
                    element_pos=data['Sort']
                    element_pos_id=data['Position']
                    window.title('Edit Element')
                else:
                    if group['ID']=='Pump':
                        element_type='Pump'
                        element_name=''
                        element_channel=1
                        element_group=group['ID']
                        element_pos=len(self.control_elements[(self.control_elements['Group']==element_group) & (self.control_elements['Type']==element_type)])
                    else:
                        element_type='LED'
                        element_name=''
                        element_channel=1
                        element_group=group['ID']
                        element_pos=len(self.control_elements[(self.control_elements['Group']==element_group) & (self.control_elements['Type']==element_type)])
                    window.title('Add Element')
                window.resizable(0, 0)
                window.grab_set()
                window.geometry('+%d+%d' % (0, 0))
                window.iconbitmap(self.icon)
                Label(master=window, text='', bg=self.colors['Element Form']).pack(side=LEFT, fill=BOTH, expand=True)
                Label(master=window, text='', bg=self.colors['Element Form']).pack(side=RIGHT, fill=BOTH, expand=True)
                Label(master=window, text='', bg=self.colors['Element Form']).pack(fill=BOTH, expand=True)
                var_type=StringVar()
                var_type.set(element_type)
                if element_group!='Pump':
                    labelframe_type=LabelFrame(master=window, text='Element Type:    ', labelanchor=W, bd=0, font=('Times', 12, 'bold'), bg=self.colors['Element Form'])
                    labelframe_type.pack(fill=BOTH, expand=True)
                    r1=Radiobutton(master=labelframe_type, text='LED', command=CHANGE_RADIOBUTTON, variable=var_type, value='LED', bg=self.colors['Element Form'], activebackground=self.colors['Element Form'], font=('Times', 12, 'bold'))
                    r1.pack(side=LEFT)
                    r2=Radiobutton(master=labelframe_type, text='Valve', command=CHANGE_RADIOBUTTON, variable=var_type, value='Valve', bg=self.colors['Element Form'], activebackground=self.colors['Element Form'], font=('Times', 12, 'bold'))
                    r2.pack(side=LEFT)
                    Label(master=window, text='', bg=self.colors['Element Form']).pack(fill=BOTH, expand=True)
                labelframe_id=LabelFrame(master=window, text='Element ID:     ', labelanchor=W, bd=0, font=('Times', 12, 'bold'), bg=self.colors['Element Form'])
                labelframe_id.pack(fill=BOTH, expand=True)
                entry_id=Entry(master=labelframe_id, justify=CENTER, width=10)
                entry_id.pack()
                entry_id.insert(0, element_name.replace('LED','').replace('Pump','').replace('Valve',''))
                Label(master=window, text='', bg=self.colors['Element Form']).pack(fill=BOTH, expand=True)
                labelframe_channel=LabelFrame(master=window, text='Element Channel: ', labelanchor=W, bd=0, font=('Times', 12, 'bold'), bg=self.colors['Element Form'])
                labelframe_channel.pack(fill=BOTH, expand=True)
                combobox_channel=ttk.Combobox(master=labelframe_channel, justify=CENTER, width=10)
                combobox_channel['values']=tuple(list(range(1,self.channels+1)))
                combobox_channel['state']='readonly'
                combobox_channel.set(element_channel)
                combobox_channel.pack()
                Label(master=window, text='', bg=self.colors['Element Form']).pack(fill=BOTH, expand=True)
                labelframe_group=LabelFrame(master=window, text='Element Group:    ', labelanchor=W, bd=0, font=('Times', 12, 'bold'), bg=self.colors['Element Form'])
                labelframe_group.pack(fill=BOTH, expand=True)
                combobox_group=ttk.Combobox(master=labelframe_group, justify=CENTER, width=10)
                if element_group!='Pump':
                    combobox_group['values']=tuple(self.control_groups['ID'][self.control_groups['ID']!='Pump'].tolist())
                else:
                    combobox_group['values']=tuple(['Pump'])
                combobox_group['state']='readonly'
                combobox_group.set(element_group)
                combobox_group.pack()
                combobox_group.bind('<<ComboboxSelected>>',CHANGE_COMBOBOX)
                Label(master=window, text='', bg=self.colors['Element Form']).pack(fill=BOTH, expand=True)
                labelframe_position=LabelFrame(master=window, text='Element Pos:    ', labelanchor=W, bd=0, font=('Times', 12, 'bold'), bg=self.colors['Element Form'])
                labelframe_position.pack(fill=BOTH, expand=True)
                entry_pos=Entry(master=labelframe_position, justify=CENTER, width=10)
                entry_pos.pack()
                entry_pos.insert(0, element_pos+1)
                Label(master=window, text='', bg=self.colors['Element Form']).pack(fill=BOTH, expand=True)
                label_container_btn=Label(master=window, text='', bg=self.colors['Element Form'])
                label_container_btn.pack(fill=BOTH, expand=True)
                if len(data):
                    button_edit=Button(master=label_container_btn, text='   Edit   ', bg=self.colors['Green'], font=('Times', 12, 'bold'), command=EDIT_ELEMENT)
                    button_edit.pack(side=LEFT)
                    button_delete=Button(master=label_container_btn, text='Delete', bg=self.colors['Red'], font=('Times', 12, 'bold'), command=DELETE_ELEMENT)
                    button_delete.pack(side=RIGHT)
                else:
                    button_add=Button(master=label_container_btn, text='   Add   ', bg=self.colors['Green'], font=('Times', 12, 'bold'), command=ADD_ELEMENT)
                    button_add.pack()
                Label(master=window, text='', bg=self.colors['Element Form']).pack(fill=BOTH, expand=True)
            except Exception as e:
                messagebox.showerror(title='APP ELEMENT_SETTINGS', message='Cannot edit element settings.', parent=self.root, icon='error')
            return
        ### APP helpers
        if start:
            self.root.configure(background=self.colors['Root'])
            #menu bar
            menu_bar=Menu(self.root)
            menu_bar.add_command(label='New', command=self.NEW)
            menu_bar.add_command(label='Options', command=self.OPTIONS)
            menu_bar.add_command(label='Save', command=self.SAVE)
            menu_bar.add_command(label='Import', command=self.IMPORT)
            menu_bar.add_command(label='Division', command=self.DIVISION)
            menu_bar.add_command(label='Custom', command=self.CUSTOMS)
            menu_bar.add_command(label='Help', command=self.HELP)
            menu_bar.add_command(label='Exit', command=self.EXIT)
            self.root.config(menu=menu_bar)
            #music bar
            labelframe_music=LabelFrame(master=self.root, text=' Music Bar ', labelanchor=N, bd=0, font=('Times', 14, 'bold'), bg=self.colors['Music Bar'])
            labelframe_music.place(relx=0.01, rely=0.02, relwidth=0.98, relheight=0.15)
            if os.path.isfile(self.music_address):
                label_container_player_music=LabelFrame(master=labelframe_music,text=' {} '.format(os.path.basename(self.music_address).split('/')[-1]), labelanchor=NW, bd=0, font=('Times', 12, 'bold'), bg=self.colors['Music Bar'])            
            else:
                label_container_player_music=LabelFrame(master=labelframe_music,text=' {} '.format(self.music_address), labelanchor=NW, bd=0, font=('Times', 12, 'bold'), bg=self.colors['Music Bar'])
            label_container_player_music.place(relx=0.01, rely=0, relwidth=0.79, relheight=0.85)
            time_pos=Scale(master=label_container_player_music, repeatdelay=1, from_=0, to=0, resolution=0.01, orient=HORIZONTAL, bd=0, troughcolor=self.colors['Buttons'], bg=self.colors['Music Bar'], activebackground=self.colors['Music Bar'], highlightcolor=self.colors['Music Bar'], highlightbackground=self.colors['Music Bar'],command=TOGGLE)
            time_pos.pack(side=LEFT, fill=BOTH, expand=True)
            button_play=Button(master=label_container_player_music, text='\u23EF', bg=self.colors['Music Bar'], activebackground=self.colors['Music Bar'], bd=0, relief=FLAT, font=('Times', 20, 'bold'), command=PLAY)
            button_play.pack(side=RIGHT, fill=Y)
            label_time=Label(master=label_container_player_music, text='    {:.2f} / {:.2f}    '.format(0, round(self.audio_length, 2)), width=16, bg=self.colors['Music Bar'], bd=0, font=('Times', 12, 'bold'))
            label_time.pack(side=RIGHT, fill=Y)
            button_upload=Button(master=labelframe_music, text='Upload', bg=self.colors['Buttons'], font=('Times', 12, 'bold'), command=UPLOAD)
            button_upload.place(relx=0.88, rely=0.05, relwidth=0.10, relheight=0.35)
            button_export=Button(master=labelframe_music, text='Export', bg=self.colors['Buttons'], font=('Times', 12, 'bold'), command=self.EXPORT)
            button_export.place(relx=0.88, rely=0.50, relwidth=0.10, relheight=0.35)
        #control bar
        labelframe_control=LabelFrame(master=self.root, text=' Control Bar ', labelanchor=N, bd=0, font=('Times', 14, 'bold'), bg=self.colors['Control Bar'])
        labelframe_control.place(relx=0.01, rely=0.19, relwidth=0.98, relheight=0.79)
        label_container_control=Label(master=labelframe_control, bd=0, bg=self.colors['Control Bar'])
        label_container_control.place(relx=0, rely=0, relwidth=1, relheight=0.90)
        label_container_control.update()
        CONTROL_FORM()
        #loop
        if start:
            self.REFRESH(time_pos, label_time)
            self.root.mainloop()
        return
    ##################################################################################################################################################################################
##################################################################################################################################################################################
if __name__ == '__main__':
    gui=GUI()
