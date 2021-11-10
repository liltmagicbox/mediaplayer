from collections import deque
#from queue import Queue #full empty put get(False) #if empty, get errors.
from datetime import datetime

from tkinter import *
from tkinter import filedialog, messagebox
from tkinter.ttk import Combobox

import time


class Player:
	def __init__(self, media = None):
		self.cputime = 0
		self.time = 0
		self.playing = False
		
		self.media = None
		self.time_max = 0
		if not media == None:
			self.time_max = media.length
			self.media = media			

	def tick(self):
		if self.playing:
			tnow = time.time()
			self.time += tnow - self.cputime
			self.cputime = tnow
			self.timesure()
			self.show()
	def show(self):
		"""varis by media type."""
		if not self.media == None:
			datalist = self.media.get(self.time)			
			for data in datalist:
				screen_show(data)

	def play(self):
		self.cputime = time.time()
		self.playing = True
	def pause(self):
		self.playing = False
	def space(self):
		if self.playing:
			self.pause()
			label0['bg'] ='coral'
		else:
			self.play()
			label0['bg'] ='#EEEEEE'


	def get_time(self):
		return self.time
	def seek(self,bias):
		""" remain deque. export all remain."""
		self.time += bias
		self.timesure()
		if bias<0:
			if self.media:
				self.media.jump(self.time)
	def jump(self,jumpto):
		""" clear deque."""
		self.time = jumpto
		self.timesure()
		if self.media:
			self.media.jump(self.time)		

	def timesure(self):
		if self.time < 0:
			self.time = 0
		if self.time >= self.time_max:
			self.time = self.time_max
			self.reachend()
	def reachend(self):
		self.pause()
		self.time = 0
		print('end of time')



#===================================
def sec_to_timestamp(sec):
	"""output = string '0h:0m:0s' """
	h,m = divmod(sec,3600)
	m,s = divmod(m,60)
	#s = round(s,0)
	hh=str(int(h)).zfill(2)
	mm=str(int(m)).zfill(2)
	ss=str(int(s)).zfill(2)
	return f"{hh}:{mm}:{ss}"

def timestamp_to_sec(timestamp):
	"""input = string 'hh:mm:ss' """

	splist = timestamp.split(':')
	if len(splist)==3:
		h,m,s = splist
		seconds = int(h)*3600+int(m)*60+int(s)
	elif len(splist)==2:
		m,s = splist
		seconds = int(m)*60+int(s)
	return seconds

def parse(text):
	"""via specific format"""
	if '_' in text:
		text = text.strip()
		if text[-1]==',':
			text = text[:-1]			
		if text[0] == '"' and text[-1]=='"':
			text = text[1:-1]
		#else:
			#print('y4eah', text)
		#text = text.replace('"','')
		
		text = text.split('_')
		timestamp = text[0]
		body = ''.join(text[1:])
		return timestamp,body
	else:
		return '',''

class mediatext:
	def __init__(self,timestamp,data):
		self.time = timestamp
		self.data = data

class Texter:
	def __init__(self,path):
		self.text = []
		self.idx = 0
		self.eot = False
		self.length = 0
		self.seekrange = 1
		self.deq = deque()		
		self.ndict = {}		
		self.load(path)
	def load(self,path):		
		nownth = False
		self.text = []

		with open(path, 'r',encoding='utf-8' )as f:
			lines = f.readlines()
			for line in lines:
				try:

					time,body = parse(line)
					if not time == '':
						seconds = timestamp_to_sec(time)
						self.text.append( mediatext(seconds,body) )
					
					else:#---for {n}
						if line.strip() == '=====':
							nownth = True
					if nownth:
						words = line.strip().split(' ')
						n,h,m,s=('0','0','0','0')
						if len(words) == 4:
							n, h, m, s = words# Nth , hh mm ss
						elif len(words) == 3:
							n, m, s = words
						if not n=='0':
							self.ndict[n] = int(h)*3600+ int(m)*60+ int(s)
				except:
					linenow = f'{lines.index(line)} 번째 줄에서 에러!'
					messagebox.showinfo(title = '3', message = linenow)
					break

		if not self.text == []:
			self.length = self.text[-1].time
			print(f'data load: length of {self.length} seconds')
			self.deq.extend(self.text)
			#print(self.ndict)
			#print(nownth)
			combo['values'] = list(self.ndict.keys())
			
			slider['to'] = self.length
			#slider['tickinterval'] = self.length/5


	def get(self,seektime):
		"""
		seek time, returns list of media_data.
		seektime float, text.time sec"""
		package = []
		try:
			while True:
				data = self.deq.popleft()
				
				t1 = sec_to_timestamp(data.time)
				t2 = sec_to_timestamp(seektime)				
				label0['text'] = f'{t1}/{t2}'

				#print(data.time, seektime)
				if data.time < seektime:
					package.append(data)				
				else:
					self.deq.appendleft(data)
					break
		except:#maybe empty.
			pass
		#we got package now.
		return package

		# seekrange = self.seekrange
		# a = seektime-seekrange
		# b = seektime+seekrange

		# while True:
		# 	idx = self.idx
		# 	readytime = self.text[idx].time
		# 	print(a,readytime,b)
		# 	if a <= readytime <= b:
		# 		self.idx+=1				
		# 		package.append( self.text[idx] )
		# 	else:
		# 		break
		# return package

	def seek(self,seektime):
		"""
		deprecated by deque.
		soft move. if forward, hold all."""
		idx = 0
		while True:			
			readytime = self.text[idx].time
			if seektime > readytime:
				idx += 1
			else:
				break
		self.idx = idx
	def jump(self,jumpto):
		"""removes all past. means clear deque."""
		self.deq = deque()
		for i in self.text:
			if i.time >= jumpto-10:
				self.deq.append(i)

#texter = Texter('loop1_1-22.txt')
#player = Player(texter)
player = Player()

#---grab near timestamp

def grab(timestamp,scope_a=60,scope_b=60):
	reli = []
	for data in texter.text:
		time = data.time
		#if timestamp-scope< time < timestamp+scope:
		if timestamp-scope_a< time < timestamp+scope_b:
			reli.append(data.data)
		elif timestamp+scope_b< time:
			break
	return reli


#-0----word
def word_sortedf(textlist):
	worddict = {}
	for data in textlist:
		wordlist = data.split(' ')
		for word in wordlist:
			if word in worddict.keys():
				worddict[word]+=1
			else:
				worddict[word]=1
	slist = sorted(worddict.items(), key = lambda x:x[1] , reverse =True)# 0=key,1=value
	exdict = {}
	for s in slist:
		exdict[s[0]] = s[1]
	return exdict


#-----3rd phase.combine
def scam(time,scopea=60,scopeb=60,cutoff=20):
	lili = grab(time,scopea,scopeb)
	bb=word_sortedf(lili)
	cc={}
	for a,b in bb.items():
		if b>=cutoff:
			cc[a]=b
	return cc

times=['02:30:20',
'02:52:53',
'03:15:35',
'03:38:20',
'04:01:07',
'04:22:23',
'04:47:28',
'05:10:12',
'05:33:00',
'05:56:30',
'06:19:15',
'06:42:01',
'07:04:46',
'07:27:35',
'07:50:20',
'08:13:05',]


#times = [aaa]
# for tt in times:
# 	tt= timestamp_to_sec(tt)
# 	print(scam(tt,30,30,2))
# 	print('----')

"""
cc=0
worddict = {}
for data in texter.text:
	wordlist = data.data.split(' ')
	for word in wordlist:
		if word in worddict.keys():
			worddict[word]+=1
		else:
			worddict[word]=1
	cc+=1
	if cc==1005:
		break
worddict = sorted(worddict, key = lambda x:worddict[x] , reverse =True)
"""

#sorted(a, key = lambda x:a[x] ,reverse = True)
#-----------------plt

# x=[]
# y=[]
# for data in texter.text:	
# 	#time = sec_to_timestamp(data.time)
# 	time = data.time
# 	if '7세' in data.data:
# 		x.append(time)
# 		y.append(1)
# 	else:
# 		x.append(time)
# 		y.append(0)


# from matplotlib import pyplot as plt
# #x=range(10)
# #y = [i*i for i in x]
# plt.plot(x,y, '*')
# plt.show()


#-------------------------------------------texter kinds.
def clear_text():
	my_text.configure(state='normal')	
	my_text.delete('1.0',END)
	my_text.configure(state='disabled')

def comboselected(e=None):
	clear_text()
	n = combo.get()
	#print(combo.get())
	sec = player.media.ndict[n]
	player.jump(sec)#how wonderful
	player.space()
	player.tick()
	player.space()
	



#----------------------------------

def slider_changed(e=None):
	clear_text()
	sec = slider.get()
	player.jump(sec)

def open_txt(e=None):
	global player
	text_file_dir = filedialog.askopenfilename(initialdir ='./', title="open txt",filetypes=(("txt file", "*.txt"),("all files", "*.*") ))
        #initialdir ='txt'	
	if not text_file_dir == '':
		root.title(text_file_dir.split('/')[-1])
		texter = Texter(text_file_dir)
		player = Player(texter)
		clear_text()		

#when player tick, each calls player.show. redefine it.




def show_line(e=None):
	playertime = player.get()
	#print(playertime)
	#print(texter.get())

	#for line in texter.ready:
	
	#while texter.ready[0].time <= playertime:
		#line = texter.ready.pop(0)

	#position = my_text.index(END)#where cursor is.
	#textline = texter.get_line()	
	#my_text.insert( END, textline )
	


def screen_show(mediadata):
	time = mediadata.time
	slider.set(time)
	data = mediadata.data
	timestamp = sec_to_timestamp(time)
	textline = timestamp+' '+data+'\n'
	my_text.configure(state='normal')
	my_text.insert( END, textline )
	my_text.configure(state='disabled')
	#print(time,data)
	if autodownClicked:
		view_last()


def view_last(e=None):
	my_text.mark_set("insert", END)
	my_text.yview_pickplace( END )

def press_left(e=None):
	player.seek(-5)
	clear_text()
def press_right(e=None):
	player.seek(5)	
def press_left2(e=None):
	clear_text()
	player.jump(player.time-60)
def press_right2(e=None):
	clear_text()
	player.jump(player.time+60)

def press_pgup(e=None):
	#n = combo.get()
	#keys = player.media.ndict.keys()		
	#n2 = keys[keys.index(n)+1]	
	#comboselected()	
	#1#player.space()
#def press_pgdn(e=None):
	#n = combo.get()
	#print(n)
	#n2 = combo['values'].index(n)+1
	#combo.set(n2)
	#print(n,n2)
	1#player.space()

def press_space(e=None):
	player.space()

def Inter():
    player.tick()
    #label0['text'] = sec_to_timestamp(player.time)
    #label0['text'] = sec_to_timestamp(player.time)
    root.after(100, Inter)



#============================= gui internal
autodownClicked = True
def autodownClick(e=None):
	global autodownClicked
	if autodownClicked:
		autodownClicked=False
		buttonad['bg']='coral'
	else:
		autodownClicked=True
		buttonad['bg']='#EEEEEE'
#============================= gui internal
root = Tk()
root.title('fastimgnote')
root.geometry('300x700')
root.attributes('-topmost', True)

button_frame = Frame(root)
button_frame.pack(side=TOP,padx=0)

label0 = Label(button_frame, text ="time", width = 14)
label0.pack(side=LEFT,padx=0)

open_button = Button(button_frame, text="OPEN", command = open_txt)
open_button.pack(side=LEFT,padx=5)

combo = Combobox(button_frame, width = 3, 
                            values=[])
combo.pack(side = LEFT)


#label1 = Label(button_frame, text ="pgdn")
#label1.pack(side=LEFT,padx=10)

buttonad = Button(button_frame,width=7, text ="스크롤", command=autodownClick)
buttonad.pack(side=LEFT,padx=10)

slider_frame = Frame(root)
slider_frame.pack(side=TOP,padx=0)
#slider = Scale(slider_frame, from_=0, to=200,tickinterval=10000, length = 800, orient=HORIZONTAL)
slider = Scale(slider_frame, from_=0, to=100, length = 800, orient=HORIZONTAL, showvalue = False)
#w2.set(23)
slider.pack(side=LEFT)


text_scroll = Scrollbar(root)
text_scroll.pack(side = RIGHT , fill = Y)
my_text = Text(root, width=83, height=31, font=("맑은 고딕",10) ,yscrollcommand = text_scroll.set)
my_text.configure(state='disabled')
#https://stackoverflow.com/questions/14887610/specify-the-dimensions-of-a-tkinter-text-box-in-pixels/14897186\
my_text.pack(fill=BOTH, expand=1)
my_text.focus_set()
#-----------------------------default text
deftext = '''////////////////////////////
OPEN 으로 txt파일 열기.

스페이스바: 정지/재생

방향키 좌우 : 앞뒤로 5초 이동.
Ctrl 과 함께 : +-60초
////////////////////////////

화수구분을 원할시:
채팅 파일 맨 아래에
=====(구분을위해필요함)
화수 시 분 초
의 형식으로 입력 해 주세요.
예:

...채팅...
"방송종료합니다",
]
=====
1 0 5 10
2 0 30 10

라면, 1화 0시 5분 10초 2화 0시 30분 10초
로 인식됩니다.

////////////////////////////
구분을 위한 띄어쓰기는 한번씩만!
(2 3  51 23 - 3과 51사이가 2칸이므로 안됨!)

0시는 생략 가능.
(2화 0시 51분 23초면,
2 0 51 23 대신 2 51 23 도 됨)

'''
my_text.configure(state='normal')
my_text.insert( END, deftext )
my_text.configure(state='disabled')

text_scroll.config(command = my_text.yview)

#-==-==--=-=-==-
slider.bind('<ButtonRelease-1>', slider_changed)
combo.bind("<<ComboboxSelected>>", comboselected)

root.bind('<Left>', press_left)
root.bind('<Right>', press_right)
root.bind('<Control-Left>', press_left2)
root.bind('<Control-Right>', press_right2)
#root.bind('<Prior>', press_pgup)
#root.bind('<Next>', press_pgdn)

root.bind('<space>', press_space)

Inter()
root.mainloop()
