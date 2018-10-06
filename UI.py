import sys
from PyQt5 import QtWidgets, QtGui, QtCore
from ui_qt import Ui_MainWindow
import sys
from Net import Net
from MCTS import MCTS
from Board import Board
import pygame
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *


class MyMainWindow(QMainWindow, Ui_MainWindow):
    moveSignal = pyqtSignal()
    endSignal = pyqtSignal()

    def __init__(self,  parent=None):
        super(MyMainWindow, self).__init__(parent)
        self.net = Net('./best_policy_1900.model')  # './best_policy_4.model'
        # 第一个和第二个棋手，  ai 1   人0
        self.board = Board(1, 0)
        #'''如果是双人对战，注释以下五行，并把上面的1,0改为1,1
        self.mcts = MCTS(self.net, self.board)
        self.board.next_move = self.mcts.get_move()
        self.board.move()
        self.mcts.board = self.board
        self.mcts.update_with_move()
        #'''

        self.setupUi(self)
        self.initUI()

    def initUI(self):
        self.moveSignal.connect(self.move)
        self.lineEdit.editingFinished.connect(self.emitMoveSignal)
        self.endSignal.connect(self.end)
        self.pushButton.clicked.connect(self.end)

    # 发射移动信号
    def emitMoveSignal(self):

        self.board.next_move = int(self.lineEdit.text())
        self.board.find_move()
        if self.board.next_move not in self.board.valid_move:
            return
        self.lineEdit.clear()
        self.board.move()
        self.label_4.setText("--------------\n电脑回合\n请等待...")
        self.moveSignal.emit()
        self.update()
        self.show()
        self.ai_move()

    def ai_move(self):
        self.board.not_end()
        if not self.board.not_end_number:
            self.endSignal.emit()
            return
        self.board.next_move = self.mcts.get_move()  # 格式 xyab
        self.board.move()
        self.label_4.setText("--------------\n你的回合\n请输入下一步：")
        self.moveSignal.emit()
        self.update()

    def move(self):

        dict = {1: 'rj', 2: 'rs', 3: 'rx', 4: 'rm', 5: 'rc', 6: 'rp', 7: 'rb',-1: 'bj', -2: 'bs', -3: 'bx', -4: 'bm', -5: 'bc', -6: 'bp', -7: 'bb'}
        for i in range(16):
            self.mp[i].setPixmap(QtGui.QPixmap(''))
            self.op[i].setPixmap(QtGui.QPixmap(''))
        for i in range(len(self.board.my_pieces)):
            piece = self.board.my_pieces[i]
            self.mp.append(QtWidgets.QLabel(self.centralwidget))
            p_type = piece//100
            p_loc = piece%100
            p_x = p_loc % 10
            p_y = 9-p_loc // 10
            self.mp[i].setPixmap(QtGui.QPixmap('data/'+dict[self.board.current_player_start * p_type]+'.png'))
            self.mp[i].move(99+92*p_x-42, 96+92*p_y-42)
        for i in range(len(self.board.op_pieces)):
            piece = -self.board.op_pieces[i]
            self.op.append(QtWidgets.QLabel(self.centralwidget))
            p_type = -(piece//100)
            p_loc = piece%100
            p_x = p_loc % 10
            p_y = 9-p_loc // 10
            self.op[i].setPixmap(QtGui.QPixmap('data/'+dict[self.board.current_player_start * p_type]+'.png'))
            self.op[i].move(99+92*p_x-42, 96+92*p_y-42)
        self.lm.setPixmap(QtGui.QPixmap(''))
        self.lm.setPixmap(QtGui.QPixmap('data/move.png'))
        self.lm.setGeometry(QtCore.QRect(99+92*((self.board.next_move%100)%10)-42, 90+92*(9-(self.board.next_move%100)//10)-42, 80,80))
        #self.lm.move(99+92*((self.board.next_move%100)%10)-42, 90+92*(9-(self.board.next_move%100)//10)-42)
        self.update()

    def end(self):
        self.label_end.setText("棋局结束!")


if __name__ == "__main__":
    pygame.init()
    pygame.mixer.init()
    pygame.mixer.music.load("data/The_Nightingale.ogg")
    pygame.mixer.music.set_volume(0.2)
    pygame.mixer.music.play(-1)
    app = 0
    app = QApplication(sys.argv)
    win = MyMainWindow()
    win.mp = []
    win.op = []
    for i in range(16):
        win.mp.append(QtWidgets.QLabel(win.centralwidget))
        win.op.append(QtWidgets.QLabel(win.centralwidget))
    win.label_4.setText("--------------\n你的回合\n请输入下一步：")
    win.lm = QtWidgets.QLabel(win.centralwidget)
    win.moveSignal.emit()
    win.show()
    sys.exit(app.exec_())



