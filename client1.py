import socket, os
import thread
import sys
from PyQt4.QtCore import *
from PyQt4.QtGui import *
#import numpy as np
#import cv2


#	thread control
end = 1
doUDP = 0
non = 1

#	communication
TCPCommuPort = 13315
OppositeAddress = "127.0.0.1"

#	send image needed
TCPCtrlPort = 13915
UDPPort = 13115
MISTAKEBOUND = 100	#	mistake upper check times
IMAGEEACHLENGTH = 512	#	the image length each time we send

#PyQt string
commandInformation = """There are 2 command you can use:\n
1. :close \n
	You can type :close to end the conversation.\n
\n
2. :send   [the image name include type]\n
	You can type :send to send a image.\n
	After you type, we would ask you the name of the file\n
	for example, you type:\n
	:send ball.jpg\n"""
msgList = ["----    chat message    ----"," "," "," "," "," ","."]
msgCounter = 1

#thread doing constant
IsMsgChange = 0
IsPixMapChange = 0


#	change string to global that the qt can use 
input_string = "test"
filaName = "test"
hasWriteFileName = 0


#	revise the message list in Qt
def ReviseLabMsg(newMsg):
	global msgCounter
	global msgList
	global IsMsgChange
	if msgCounter < 5:
		msgList[msgCounter] = newMsg
		msgCounter = msgCounter + 1
		print "small"
	else:
		i = 1
		for i in range (1, 6, 1):
			print msgList[i]
		i = 1
		while i < 6:
			msgList[i] = msgList[i+1]
			i = i+1
		msgList[5] = newMsg
		print "big"
	IsMsgChange = 1


#	define PyQt
def WidgetThread( non, non2):
	app = QApplication(sys.argv)
	widget = MyWidget()
	widget.setWindowTitle("Sunner Line")
	widget.show()

	app.exec_()


class InforLayout(QHBoxLayout):
	def __init__(self, parent = None):
		super(InforLayout, self).__init__(parent)
		self.addButton()
		self.commandInformation = commandInformation

	def addButton(self):
		inforBtn = QPushButton('          Command          ')
		inforBtn.setCheckable(True)
		inforBtn.clicked.connect(self.runProcess)

		#self.addStretch(5)
		self.addWidget(inforBtn)
		self.addStretch(5)

	def runProcess(self):
		global commandInformation
		widget = QWidget()
		reply = QMessageBox.information(
	    widget,'\t\t\t\tinfomation\t\t',
		commandInformation,
	    QMessageBox.Ok)

class OppoLayout(QHBoxLayout):
	def __init__(self, parent = None):
		super(OppoLayout, self).__init__(parent)
		self.addButton()
		self.address = OppositeAddress
		self.TCPCommuPort = TCPCommuPort
		self.oppoInfor = "The opposite member's information:\n\nAddress: "+str(self.address)+"\nPort Number: "+str(self.TCPCommuPort)
	def addButton(self):
		commandBtn = QPushButton('        Information        ')
		commandBtn.setCheckable(True)
		commandBtn.clicked.connect(self.runProcess)

		#self.addStretch(5)
		self.addWidget(commandBtn)
		self.addStretch(5)

	def runProcess(self):
		global commandInformation
		widget = QWidget()
		reply = QMessageBox.information(
	    widget,'\t\t\t\tinfomation\t\t',
		self.oppoInfor,
	    QMessageBox.Ok)



class quitLayout(QHBoxLayout):
	def __init__(self, parent = None):
		super(quitLayout, self).__init__(parent)
		self.addButton()

	def addButton(self):
		quitBtn = QPushButton('quit')
		quitBtn.setCheckable(True)
		quitBtn.clicked.connect(self.runProcess)

		self.addWidget(quitBtn)
		self.addStretch(5)

	def runProcess(self):
		global end
		client_socket.send(":close")
		end = 0





class QLab(QLabel):
	def __init__(self, parent, text=''):
		QLabel.__init__(self, parent)
		self.setText(text)
		self.setFont(QFont('Arial', 16, 30, False))
		self.setStyleSheet(
			'background-color:white;' +
			'color:brown;' +
			'border:brown;'+
			'text-align: right;')
		self.show()


	def revise(self):
		global msgList
		reviseText = msgList[0] + "\n" + msgList[1] + "\n" + msgList[2] + "\n" + msgList[3] + "\n" + msgList[4] + "\n" + msgList[5] + "\n"

		#print reviseText
		qstr = QString(reviseText);
		self.setText(qstr)





#	merge the Lab and the edit text
class LeftLayout(QVBoxLayout):
	def __init__(self, parent = None):
		super(LeftLayout, self).__init__(parent)
		self.addEditList()
	

	def addEditList(self):
		self.lineEdit = QLineEdit()
		self.labelr = QLab('Hello world!')
		self.addWidget(self.labelr)
		self.addWidget(self.lineEdit)




class ImageLayout(QHBoxLayout):
	def __init__(self, parent = None):
		super(ImageLayout, self).__init__(parent)
		self.addButton()

	def addButton(self):
		quitBtn = QPushButton('&Show Image')
		quitBtn.setCheckable(True)
		quitBtn.clicked.connect(self.runProcess)

		self.addWidget(quitBtn)
		self.addStretch(5)

	def runProcess(self):
		#	Load an color image in grayscale
		img = cv2.imread('R.jpg',1)
		#print img
		if img == None:
			print "The opposite side didn't pass photo !!!"
		else:
			cv2.imshow('image',img)
			cv2.waitKey(0)
			cv2.destroyAllWindows()




class MyWidget(QWidget):
	def __init__(self, parent = None):
		super(MyWidget, self).__init__(parent)
		self.resize(500, 500)
		self.createLayout()
        
	def createLayout(self):
		self.info = InforLayout()
		self.oppo = OppoLayout()
		self.quit = quitLayout()
		self.image = ImageLayout()
		self.left = LeftLayout()


		#	use a thread to listen the text
		try:
			thread.start_new_thread( self.reviseLabThread, ("Thread-1", 2, ) )
			print "revise thread set done..."
		except:
			print "Error: unable to start thread"
		self.left.labelr.revise()


		v1 = QVBoxLayout()
		v1.addLayout(self.info)
		v1.addLayout(self.oppo)
		v1.addLayout(self.image)
		v1.addLayout(self.quit)

		h1 = QHBoxLayout()
		h1.addLayout(self.left)
		h1.addLayout(v1)
		
		self.setLayout(h1)


	#	thread to listen the msg change
	def reviseLabThread(self, non, non2):
		global IsMsgChange
		while True:
			if IsMsgChange == 1:
				self.left.labelr.revise()
				IsMsgChange = 0


	def keyPressEvent(self, event):
		global IsMsgChange
		global input_string
		global end
		global fileName
		global doUDP
		global hasWriteFileName

		#	it's important that you should revise the type here
		#	socket can just pass the python str type, not the QString
		if event.key() == Qt.Key_Return:
			input_string = str(self.left.lineEdit.text())
			commandJudge = input_string[:5]
			print "command: ", commandJudge
			self.left.lineEdit.clear()
			if commandJudge != ":send":
				TCPWriteThreadCont(False)
				if input_string == ":close":
					end = 0
				ReviseLabMsg("I said: "+ QString( input_string ))
				#IsMsgChange = 1
			else:
				fileName = input_string[6:]
				input_string = ":send"
				TCPWriteThreadCont(False)
				print "image name: ", fileName
				hasWriteFileName = 1
				doUDP = 1


def UDPCtrlThread( non, non2):
	global interrupt
	global end
	global doUDP
	global fileName
	global hasWriteFileName

	while True and end == 1:
		if doUDP == 1:
			print "doUDP catch"
			UDPSendImage()
			doUDP = 0


def UDPSendImage():
	global IsMsgChange
	global fileName
	global hasWriteFileName

	filewrong = 0
	showString = "test"
	print "wait for connection"
	UDPserver_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	UDPserver_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	UDPserver_socket.bind(("", TCPCtrlPort))
	UDPserver_socket.listen(1)
	#input_string = "test"


	UDPclient_socket, address = UDPserver_socket.accept()
	showString = "Conencted to - " + str(address) + "\n"
	print showString
	ReviseLabMsg(QString(showString))




	showString = "set UDP socket" + "\n"
	print showString
	ReviseLabMsg(QString(showString))
	UDPImgclient_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


	print "hasWriteFileName: ", hasWriteFileName
	if hasWriteFileName == 0:#	from terminal
		#
		#	enter the file name
		showString = "Enter file name of the image with extentsion" + "\n" + "(example: filename.jpg,filename.png ...etc) - " + "\n"
		print showString


		#
		#	check if you type wrong
		while True:
			file_name = raw_input()


			#
			#	check if the name of the image is wrong
			try:
				img = open(file_name, 'r')
				print "transfer the picture"
				print "open the file ", file_name
				break
			except IOError, e:
				print "you didn't have the file ? Please check..."
				print "Enter file name again..."
				print "(example: filename.jpg,filename.png ...etc) - "
	else:#	from qt
		file_name = fileName
		#
		#	check if the name of the image is wrong
		try:
			img = open(file_name, 'r')
			showString = "transfer the picture" + "\n" + "open the file " + file_name + "\n"
			print showString
			ReviseLabMsg(QString(showString))
		except IOError, e:
			print "you didn't have the file ? Please check..."
			print "close the connection"
			filewrong = 1

	UDPclient_socket.send(str(filewrong))
	hasWriteFileName = 0


	#
	#	send the image
	while True and filewrong == 0:
		print "start to read..."
		img_l = img.read(IMAGEEACHLENGTH)
		print "read..."
		if not img_l:
			break;
		while True:
			print "before send..."
			UDPImgclient_socket.sendto(img_l, ("localhost", UDPPort))
			print "send"
			ACK = UDPclient_socket.recv(1024)
			print ACK, " ",
			if ACK == "0":
				continue;
			else:
				break;
	print "Data sent successful!"

	#
	#	close the socket
	img.close()

	UDPserver_socket.close()
	UDPclient_socket.close()
	UDPImgclient_socket.close()




def UDPRecvImage():
	UDPinput_string = "test"
	client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	while True:
		errorTime = 0
		try:
			client_socket.connect(("localhost", TCPCtrlPort))
			break
		except socket.error, e:
			print "connect again..."
			errorTime = errorTime + 1
			if errorTime > 100000:
				return

	print "wait for connection"
	UDPserver_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	UDPserver_socket.bind(("", UDPPort))

	#
	#	assume the image name is R.jpg
	print "the image name is 'R.jpg' "
	fname = 'R.jpg'
	fp = open(fname,'w')

	fileIsExist = client_socket.recv(1024)

	#
	#	looping recving the image
	#	the counter to represent if we need to close the file descriptor
	endTrans = 0	
	while True and fileIsExist == "0":
		mistake = 0;
		if endTrans == 1:
			break
		while True:
			print "recv...",
			strng, oppositeAddress= UDPserver_socket.recvfrom(IMAGEEACHLENGTH)

			#
			#	if the length of the data is 512, we acknowledge it
			if len(strng) == IMAGEEACHLENGTH:
				UDPinput_string = "1"
				print UDPinput_string
				mistake = 0
				client_socket.send(UDPinput_string)
				break

			#
			#	after we check lots of time, we assume it's the end
			elif len(strng) != IMAGEEACHLENGTH and mistake == MISTAKEBOUND:
				UDPinput_string = "1"
				client_socket.send(UDPinput_string)
				endTrans = 1
				break

			#
			#	if the length is wrong, we assume wrong
			else:
				UDPinput_string = "0"
				print len(strng), "       ", mistake, ""
				client_socket.send(UDPinput_string)
				mistake = mistake+1
				continue
		if not strng:
			break
		print "start write........",
		fp.write(strng)
		print "done write"

	#
	#	close the file descriptor
	fp.close()
	client_socket.close()
	if fileIsExist == "0":
		print "Data Received successfully"
	else:
		print "error! close the image transformation..."


def TCPWriteThread( non, non2):
	global interrupt
	global end
	global input_string
	while True and end == 1:
		input_string = raw_input() 
		TCPWriteThreadCont(True)


def TCPWriteThreadCont( From ):
	global input_string
	client_socket.send(input_string)
	if input_string == ':close':
		end = 0
	if input_string == ':send' and From == True:
		doUDP = 1


def TCPReadThread( non, non2):
	global end
	global IsMsgChange
	while True and end == 1:
		read_string = client_socket.recv(1024)
		if read_string == ':close':
			end = 0
			break
		if read_string == ':send':
			UDPRecvImage()


		#	string isn't the same as qstring
		#	so you should convert before you use
		else:
			print read_string
			read_string = "He/She said:" + read_string
			qstr = QString(read_string)
			ReviseLabMsg(qstr)


if __name__ == "__main__":
	input_string = "test"
	client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

	#client_socket.connect(("localhost", TCPCommuPort))
	while True:
		try:
			input_string = raw_input('enter the IP of destination: ')
			client_socket.connect((input_string, TCPCommuPort))
			break
		except:
			print "destination error, key in again..."

	try:
		thread.start_new_thread( TCPWriteThread, ("Thread-1", 2, ) )
		thread.start_new_thread( TCPReadThread, ("Thread-2", 4, ) )
		thread.start_new_thread( WidgetThread, ("Thread-3", 2, ) )
		thread.start_new_thread( UDPCtrlThread, ("Thread-4", 2, ) )
		print "thread set done..."
	except:
		print "Error: unable to start thread"
		
	while end == 1:
		non = 1
	print "connect close"
	client_socket.close()

	endCounter = 0
	while endCounter<1000000:
		endCounter = endCounter + 1
