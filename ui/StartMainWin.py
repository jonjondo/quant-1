__author__ = 'lottiwang'
from PyQt5.QtWidgets import QApplication,QMainWindow,QFileDialog
from PyQt5.QtGui import QTextCursor

from ui.mainwindow import *
from WhiteGuardStock4UI import  *


class BackEndThread(QThread,WhiteGuardStockCore4UI):
	def __init__(self,dst_ip = '192.168.0.106',dst_port = 11111):
		try:
			super(BackEndThread,self).__init__()
			self.start_connect('192.168.0.106',11111)
		except Exception as e:
			print(e.message)

	def run(self):
		self.get_everyday_schedule(0)
		self.clear_quote()



class StartMainWindow(QMainWindow,Ui_MainWindow):
	def __init__(self,parent=None):
		super(StartMainWindow,self).__init__(parent)
		self.setupUi(self)



	def OnBtnGoClicked(self):
		self.backend = BackEndThread()
		try:
			self.backend.update_progress.connect(self.handleProgress)
			self.backend.update_info.connect(self.handleProcessInfo)
			self.backend.start()
		except Exception as e:
			print(e.message)

	def close(self):
		pass

	def __del__(self):
		#self.backend.stop()
		pass



	def OnBtnOpenStockList(self):
		file,ok = QFileDialog.getOpenFileName(self,"打开","C:/","All Files (*);;Text Files (*.txt);; CSV Files (*.csv)")
		self.statusbar.showMessage(file)

	def handleProgress(self,value):
		self.progressBar.setValue(float(value))

	def handleProcessInfo(self,value):
		self.textEdit.setPlainText(value)
		cur= self.textEdit.textCursor()
		cur.movePosition(QTextCursor.End)
		self.textEdit.setTextCursor(cur)




if __name__ == "__main__":
	app = QApplication(sys.argv)
	WindyQuantMainWindow = StartMainWindow()
	WindyQuantMainWindow.show()
	sys.exit(app.exec_())