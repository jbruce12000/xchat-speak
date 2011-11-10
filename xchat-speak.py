__module_name__ = "xchat-speak"
__module_version__ = "1.0"
__module_description__ = "speak using festival"

import socket
import os
import time
import atexit
import signal
import xchat
import string

class festival:
	"Festival connection object, as returned by festival.open()."
	
	def __init__(self,sock):
		self.sock=sock
		
	def _checkresp(self):
		if self.sock.recv(256)=='ER\n':
			raise Exception
	
	def set_param(self,param,value):
		"Set parameter to a number or a symbol."
		
		if type(value) is str:
			self.sock.send("(Parameter.set '%s '%s)"%(param,value))
		else:
			self.sock.send("(Parameter.set '%s %r)"%(param,value))
		self._checkresp()

	def set_param_str(self,param,value):
		"Set parameter to a string."
		
		self.sock.send("(Parameter.set '%s \"%s\")"%(param,value))
		self._checkresp()
			
	def block(self,flag=True):
		"Sets blocking/nonblocking mode."
		
		if flag:
			self.sock.send("(audio_mode 'sync)")
		else:
			self.sock.send("(audio_mode 'async)")
		self._checkresp()
	
	def set_audio_method(self,method=None,device=None):
		"Set audio method and/or device."
		
		if method is not None:
			self.set_param('Audio_Method',method)
		if device is not None:
			self.set_param_str('Audio_Device',device)
	
	def set_audio_command(self,command,rate=None,format=None):
		"""Set audio command, and optionally rate and format.
		
		Sets audio method to "Audio_Command"."""
		
		self.set_audio_method("Audio_Command")
		if rate is not None:
			self.set_param('Audio_Required_Rate',rate)
		if format is not None:
			self.set_param('Audio_Required_Format',format)
		self.set_param_str('Audio_Command',command)
		
	def say(self,text):
		"Speak string 'text'."
		
		self.sock.send('(SayText "%s")'%text)
		self._checkresp()
		
	def sayfile(self,filename):
		"""Speak contents of file 'filename'.
		
		Note that this is done on the server end, not the client
		end, so you best pass it absolute filenames."""
		
		self.sock.send('(tts "%s" nil)'%filename)
		self._checkresp()
		
	def close(self):
		"Terminate the Festival connection."
		self.sock.send('(quit)')
		
	__del__=close

        def open(self,host='',port=1314,nostart=False):
        	"""Opens a new connection to a Festival server.
	
        	Attempts to connect to a Festival server (most likely started with
        	'festival --server'). Will attempt to start a local server on port
        	1314 if one is not running and the 'nostart' flag is not set to
        	True. Returns a festival.festival object."""
	
        	global festival_pid
                from subprocess import STDOUT, Popen
	
	        sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	        try:
	        	sock.connect((host,port))
	        except socket.error:
	        	if nostart:
	        		raise socket.error
	        	else:
                                festival_pid = Popen(["festival", "--server"],stdout=3,stderr=STDOUT).pid 
		        	atexit.register(_kill_server)
		        	for t in xrange(20):
		        		try:
		        			time.sleep(.25)
		        			sock.connect((host,port))
		        		except socket.error:
		        			pass
		        		else:
		        			break
		        	else:
		        		raise socket.error
		
	        return festival(sock)

        def _kill_server():
        	os.kill(festival_pid,signal.SIGTERM)

def chat_hook(word, word_eol, userdata):
        XCHAT_FESTIVAL.open().say(' '.join(word[3:]))
        xchat.prnt("This is word: " + `word`)
        return xchat.EAT_NONE

global XCHAT_FESTIVAL
XCHAT_FESTIVAL=festival.open()


xchat.hook_server("PRIVMSG", chat_hook)

# load /home/jbruce/tmp/xchat-speak/xchat-speak.py
# unload /home/jbruce/tmp/xchat-speak/xchat-speak.py
