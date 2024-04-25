from tkinter import *
import paramiko as pm
from scp import SCPClient
import win32com.client as win32
import psutil
from binarytobraille import binToBraille

scp = None
ssh = None
server = None

def createSSHClient(server, port, user, password):
	client = pm.SSHClient()
	client.load_system_host_keys()
	client.set_missing_host_key_policy(pm.AutoAddPolicy())
	client.connect(server, port, user, password)
	return client

def is_process_running(process_name):
	for process in psutil.process_iter(['pid', 'name']):
		if process.info['name'] == process_name:
			return True
	return False
	 
def connect():
	global scp
	global ssh
	global server
	global status
	global login
	global enterBt
	global ip_entry
	if is_process_running("WINWORD.EXE"):
		status.config(text = "Please close all word tabs before creating new doc.")
	else:
		status.config(text = "Connecting...")
		login.update()
		server = ip_entry.get()
		try:
			ssh = createSSHClient(server, 22, "leap", "BestTeam")
			ssh.invoke_shell()
			ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command('/bin/bash -lc "cd Transliteration; python transliteration.py"')
			scp = SCPClient(ssh.get_transport())
			status.config(text = "Connected! Please close all Word tabs to create new doc. (Make sure to save your progress.)")
			login.update_idletasks()
			edit_word()
		except Exception as e: 
			status.config(text = 'Failed. Please check hotspot settings to ensure IP is correct and brailler is still connected.')
			login.update_idletasks()

def edit_word():
	global scp
	global ssh
	global server
	try:
		word = win32.gencache.EnsureDispatch('Word.Application')
		ascii_doc = word.Documents.Add()
		braille_doc = word.Documents.Add()
		word.Visible = True
		ascii_doc.Sections(1).Headers(win32.constants.wdHeaderFooterPrimary).Range.Text = server + " Alpha-Numeric"
		braille_doc.Sections(1).Headers(win32.constants.wdHeaderFooterPrimary).Range.Text = server + " Braille"
		while (True):
			while (True):
				try:
					scp.get("~/Transliteration/transliterateOutput.txt")
					scp.get("~/Transliteration/tempBin.txt")
					break
				except:
					pass
			f_scp_ascii = open("transliterateOutput.txt", "r")
			f_scp_braille = open("tempBin.txt")
			ascii_doc.Content.Text = f_scp_ascii.read()
			braille_doc.Content.Text = binToBraille(f_scp_braille.read())
	except Exception as e:
		on_closing()
	
	
def on_closing():
	global ssh
	global enterBt
	ssh.exec_command('/bin/bash -lc "pkill -f transliteration"')
	ssh.exec_command('/bin/bash -lc "pkill -f encoder"')

def to_login(): # Sequence 1
	global no_win
	global inputtxt
	global login
	global status
	global enterBt
	global win
	global ip_entry
	win.destroy()
	if not no_win:
		no_win = True
		login = Tk()
		login.geometry('1500x200')
		login.title("Login")
		
		prompt = Label(login, text = 'Enter Device IP Address', font = ('Calibri 20 bold'))
		prompt.pack()
		ip_entry = StringVar()
		inputtxt = Entry(login, width = 90, font = 'Calibri 20', textvariable = ip_entry)
		inputtxt.pack()
		inputtxt.bind("<Return>", lambda e: connect())
		enterBt = Button(login, text = 'Create New Doc', command = connect, font = 'Calibri 18')
		enterBt.pack()
		status = Label(login, text = " ", font = "Calibri 18")
		status.pack(pady = 1)
	
win = Tk()
win.title('Leap Transliteration Reader v 0.1.0')
win.geometry('720x480')

label1 = Label(win, text = 'Leap Transliteration Reader v 0.1.0', font = ('Calibri 20 bold'))
label2 = Label(win, text = "Please read the following below before continuing!", font = ('Calibri 15 bold'))
label3 = Label(win, text = 'To begin, you will need to create a hotspot on your computer. For Windows 10: open settings, open Network & Internet, then Mobile Hotspot. \
Edit the network name and password to "PiConfig", then switch the Mobile Hotspot "on". When the device is connected, the IP Address should show up on the window on your computer: copy it down.', wraplength = 600, font = ('Calibri 15'))
label1.pack(pady = 20)
label2.pack(pady = 20)
label3.pack(pady = 20)

button1 = Button(win, text = 'I have read the following information above.', command = to_login, font = "Calibri 18")
button1.pack(pady = 30)
#win.after(3000, lambda: button1.config(state = 'normal'))
no_win = False
win.mainloop()
