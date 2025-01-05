# -*- coding: utf-8 -*-
"""
Simple Hardware Resource Viewer
created mostly with tkinter and psutil modules.
Other modules added for niche info due to bugs or easier access. 
Used regular expressions to pull out processor name and model.

Current update rate on the data is every 5 seconds. 

Gathers data from Disk, RAM, CPU, and Network utilization.

Has a usage log that is optionally shown that updates with 
information as it updates.

Future Possible Features:
    -Timestamps on usage log data.
    -Another button that shows the processes currently running 
     and their individual usage.
    -Write Log data to file for future usage?
    -choose color/theme/update interval

@author: demar
"""
import tkinter as tk
import platform
import psutil
import re
import sys
#this import is for Memory usage only as there is a bug with python 3.12
from shutil import disk_usage

#methods to show and remove the log frame
def show_log_frame():
    #show it
    logFrame.grid(columnspan=4, row=3, pady=(20,0), sticky='ew')
    #change the button to remove it
    logButton.config(command= remove_log_frame, text="Close Log")
    
def remove_log_frame():
    #remove it
    logFrame.grid_remove()
    #change button to show it
    logButton.config(command= show_log_frame, text="Show Log")
    
#quit button function to quit the process and the window
def quit_program():
    window.destroy()
    sys.exit()


def update_log():
    #grab new data:
    CPUavail = psutil.cpu_freq().current/1000
    CPUpercentage = psutil.cpu_percent()
    RAMavail = psutil.virtual_memory().available/(1024.0**3)
    RAMpercentage = psutil.virtual_memory().percent
    dTotal, dUsed, dFree = disk_usage('/')
    global WifiRecv, WifiSent, EtherRecv, EtherSent, connection
    
    #update the current showing at the top:
    currentCPUtext.config(text=f'Available: {CPUavail:.1f}Ghz\nUsed: {CPUpercentage:.2f}%')
    currentRAMtext.config(text=f'Available: {RAMavail:.2f}GB\nUsed: {RAMpercentage:.0f}%')
    currentMEMtext.config(text=f'Available: {dFree/(1024.0**4):.2f}TB\nUsed: {(((dUsed/1024.0**4)/(dTotal/1024.0**4))*100):.2f}%')
    
    
    #Update the log values:
    logCPUtext.insert(tk.END, f'A: {CPUavail:.1f}Ghz - U: {CPUpercentage:.2f}%\n', 'tag_center')
    logRAMtext.insert(tk.END, f'A: {RAMavail:.2f}GB - U: {RAMpercentage:.0f}%\n','tag_center')
    logMEMtext.insert(tk.END, f'A: {dFree/(1024.0**4):.2f}TB - U: {(((dUsed/1024.0**4)/(dTotal/1024.0**4))*100):.2f}%\n', 'tag_center')
    
    #update network section:
    if connection == 'WiFi':
        old_Sent = WifiSent
        old_Recv = WifiRecv
        WifiRecv = psutil.net_io_counters(pernic=True)['Wi-Fi'].bytes_recv/1024
        WifiSent = psutil.net_io_counters(pernic=True)['Wi-Fi'].bytes_sent/1024
        currentNETtext.config(text=f'Sent: {(WifiSent-old_Sent)/5:.1f}KB\nReceived: {(WifiRecv-old_Recv)/5:.1f}KB')
        logNETtext.insert(tk.END, f'S: {(WifiSent-old_Sent)/5:.1f}KB - R: {(WifiRecv-old_Recv)/5:.1f}KB\n', 'tag_center')
    
    if connection == 'Ethernet':
        old_Sent = EtherSent
        old_Recv = EtherRecv
        EtherRecv = psutil.net_io_counters(pernic=True)['Ethernet'].bytes_recv/1024
        EtherSent = psutil.net_io_counters(pernic=True)['Ethernet'].bytes_sent/1024
        currentNETtext.config(text=f'Sent: {(EtherSent-old_Sent)/5:.1f}KB\nReceived: {(EtherRecv-old_Recv)/5:.1f}KB')
        logNETtext.insert(tk.END, f'S: {(EtherSent-old_Sent)/5:.1f}KB - R: {(EtherRecv-old_Recv)/5:.1f}KB\n', 'tag_center')
        
    
    window.after(5000, update_log)

#create the window class
window = tk.Tk()
#config the main window
window.title("Simple Hardware Resource Viewer")
window.columnconfigure(0, weight=1)
window.rowconfigure(0, weight=1)

#frame widget created off of the window
frm = tk.Frame(window, padx=10, pady=10, bg="light grey")
#grid defines the relative position, needs to be created first before use
frm.grid(column=0, row=0, sticky="nsew")
frm.columnconfigure(0, weight=1)
frm.columnconfigure(1, weight=1)
frm.columnconfigure(2, weight=1)
frm.columnconfigure(3, weight=1)
frm.rowconfigure(1, weight=1)
frm.rowconfigure(3, weight=3)

#labels on top:
tk.Label(frm, text="CPU", font=("Times", 16, "bold"), bg= "light blue1").grid(ipadx=10, padx=(50,25), column=0, row=0, sticky = "n")
tk.Label(frm, text="Ram", font=("Times", 16, "bold"), bg= "light blue2").grid(ipadx=10, padx=25, column=1, row=0, sticky = "n")
tk.Label(frm, text="Memory", font=("Times", 16, "bold"), bg= "light sky blue2").grid(ipadx=10, padx=25, column=2, row=0, sticky = "n")
tk.Label(frm, text="Network", font=("Times", 16, "bold"), bg= "steel blue2").grid(ipadx=10, padx=(25,50), column=3, row=0, sticky = "n")


#get basic data:
#processor data
m1 = re.match(r'\w*\s*\d*', platform.processor())
m2 = re.search(r'Model\s*\d*\.?\d*', platform.processor(), re.I)
CPUText = tk.Message(frm, text=f'{m1.group()}\n{m2.group()}\nCores: {psutil.cpu_count(logical=False):d}\nMax: {psutil.cpu_freq().max/1000:.1f}Ghz', font=("Times", 12, "italic"))
CPUText.grid(ipadx=5, padx=(50,0), pady=(0,10), column=0, row=1, sticky = "n")

#RAM data
RAMText = tk.Message(frm, text=f'Total: {psutil.virtual_memory().total/(1024.0**3):.2f}GB', font=("Times", 12, "italic"), width = 150)
RAMText.grid(ipadx=5, padx=25, pady=(0,10), column=1, row=1, sticky = "n")

#SSD Memory data, gathered from root path
dTotal, dUsed, dFree = disk_usage('/')
MEMText = tk.Message(frm, text=f'Total: {dTotal/(1024.0**4):.2f}TB\nUsed: {dUsed/(1024.0**4):.2f}TB', font=("Times", 12, "italic"), width = 150)
MEMText.grid(ipadx=5, padx=25, pady=(0,10), column=2, row=1, sticky = "n")

#Network data
net_data = psutil.net_io_counters(pernic=True)
EtherRecv = net_data['Ethernet'].bytes_recv/1024
EtherSent = net_data['Ethernet'].bytes_sent/1024
#set connection type, when on wifi this shows 0 for ethernet, but on ether it doesn't have a wifi key at all
if EtherRecv > 0:
    connection = 'Ethernet'
    #assign these anyway as I made them global so I need them for now to make sure no errors later.
    WifiRecv = 0
    WifiSent = 0
if EtherRecv == 0:
    connection = 'WiFi'
    WifiRecv = net_data['Wi-Fi'].bytes_recv/1024
    WifiSent = net_data['Wi-Fi'].bytes_sent/1024


NETText = tk.Message(frm, text= f'Connection: {connection:s}', font=("Times", 12, "italic"), width = 150)
NETText.grid(ipadx=5, padx=(0,50), pady=(0,10), column=3, row=1, sticky = "n")



#current data initialization
currentCPUtext = tk.Message(frm, font=("Times", 12), bg="light blue1", width= 150)
currentCPUtext.grid(ipadx=5, padx=(50,25), pady=(0,10), column=0, row=2, sticky = "n")

currentRAMtext = tk.Message(frm, font=("Times", 11), bg="light blue2", width=150)
currentRAMtext.grid(ipadx=5, padx=25, pady=(0,10), column=1, row=2, sticky = "n")

currentMEMtext = tk.Message(frm, font=("Times", 11), bg="light sky blue2", width=150)
currentMEMtext.grid(ipadx=5, padx=25, pady=(0,10), column=2, row=2, sticky = "n")

currentNETtext = tk.Message(frm, font=("Times", 11), bg="steel blue2", width=150)
currentNETtext.grid(ipadx=5, padx=(25,50), pady=(0,10), column=3, row=2, sticky = "n")



#initialize the log frame and entries.
logFrame = tk.Frame(frm, bg="gray68")
tk.Label(logFrame, text="Usage Logs:").grid(row=0, columnspan=4, ipadx= 5, sticky="n", padx=10, pady=(10,))

#CPU Logs
logCPUtext = tk.Text(logFrame, font=("Times", 11), height=10, width=25)
logCPUtext.tag_configure('tag_center', justify='center')
logCPUtext.grid(column=0, row=1, ipadx= 5, sticky="n", pady= (0,10))

#RAM Logs
logRAMtext = tk.Text(logFrame, font=("Times", 11), height=10, width=25)
logRAMtext.tag_configure('tag_center', justify='center')
logRAMtext.grid(column=1, row=1, ipadx= 5, sticky="n", pady= (0,10))

#MEM Logs
logMEMtext = tk.Text(logFrame, font=("Times", 11), height=10, width=25)
logMEMtext.tag_configure('tag_center', justify='center')
logMEMtext.grid(column=2, row=1, ipadx= 5, sticky="n", pady= (0,10))

#NET Logs
logNETtext = tk.Text(logFrame, font=("Times", 11), height=10, width=25)
logNETtext.tag_configure('tag_center', justify='center')
logNETtext.grid(column=3, row=1, ipadx= 5, sticky="n", pady= (0,10))

logFrame.columnconfigure(0, weight=1)
logFrame.columnconfigure(1, weight=1)
logFrame.columnconfigure(2, weight=1)
logFrame.columnconfigure(3, weight=1)
logFrame.rowconfigure(0, weight=0)
logFrame.rowconfigure(1, weight=1)



#create the actionable button in the frame, give it the command and position.
quitButton = tk.Button(frm, text="Quit", command=quit_program, background="firebrick1",activebackground="red3")
quitButton.grid(column=3, row=4, sticky="se", pady=(30,0), ipadx=10)

#create the button to open the log files
logButton = tk.Button(frm, text="Show Log", command=show_log_frame, background="sea green",activebackground="medium sea green")
logButton.grid(column=0, row=4, sticky="sw", pady=(30,0), ipadx=10)

"""
#future feature?
#shows each process currently running
for proc in psutil.process_iter(['pid', 'name', 'username']):
    print(proc.info)
"""

#this function call starts the logging updates.
update_log()


#mainloop method shows the display and responds to user input.
window.mainloop()