import xlrd
from xlutils.copy import copy
import numpy as np
np.set_printoptions(threshold=np.inf)

'''

【棋盘】

列号编号从左到右：012345678
行号编号从下到上：0123456789
红方在棋盘下部，黑方在棋盘上部
描述位置格式：xy       x为行号(0省略)，y为列号
描述移动格式：xyab    xy为移动前坐标，ab为移动后坐标

    
移动格式：xyx'y'
    xy为移动前坐标
        x为行号(为0则省略)
        y为列号(xy均为0时省略)
    x'y'为移动后坐标


【棋子】
红方
帅104 仕203/205 象302/306 马401/407 车500/508 炮621/627 兵730/732/734/736/738
黑方
将-104 士-203/-205 相-302/-306 马-401/-407 车-500/-508 炮-621/-627 卒-703/-732/-734/-736/-738
空位 0

棋子用p表示：如632
位置用c表示：如32

输入：己方平面7个，是否是先手,对方平面7个,己方布局，对方布局，
对方上次移动的位置，我方可用的行动三个平面  共21个

'''


class Board:
    def __init__(self,p1,p2):
        self.situation = [[500, 401, 302, 203, 104, 205, 306, 407, 508],
                          [0, 0, 0, 0, 0, 0, 0, 0, 0],
                          [0, 621, 0, 0, 0, 0, 0, 627, 0],
                          [730, 0, 732, 0, 734, 0, 736, 0, 738],
                          [0, 0, 0, 0, 0, 0, 0, 0, 0],
                          [0, 0, 0, 0, 0, 0, 0, 0, 0],
                          [-760, 0, -762, 0, -764, 0, -766, 0, -768],
                          [0, -671, 0, 0, 0, 0, 0, -677, 0],
                          [0, 0, 0, 0, 0, 0, 0, 0, 0],
                          [-590, -491, -392, -293, -194, -295, -396, -497, -598]]
        self.my_pieces = [104, 203,205,302,  306,401,  407,500,  508, 621, 627, 730,  732,  734, 736, 738]
        self.op_pieces = [-194, -293,  -295,-392,  -396, -491,  -497,-590, -598, -671, -677, -760,  -762,  -764, -766, -768]

        # self.situation = [[0, 401, 0, 0, 104, 0, 0, 0, 0],
        #                   [0, 0, 0, 0, 0, 0, 0, 0, 0],
        #                   [0, 0, 0, 0, 0, 0, 0, 0, 0],
        #                   [0, 0, 0, 0, 734, 0, 0, 0, 0],
        #                   [0, 0, 0, 0, 0, 0, 0, 0, 0],
        #                   [0, 0, 0, 0, 0, 0, 0, 0, 0],
        #                   [0, 0, 0, 0, -764, 0, 0, 0, 0],
        #                   [0, 0, 0, 0, 0, 0, 0, 0, 0],
        #                   [0, 0, 0, 0, 0, 0, 0, 0, 0],
        #                   [0, 0, 0, 0, -194, 0, 0, -497, 0]]
        # self.my_pieces = [104, 401, 734]
        # self.op_pieces = [-194, -497, -764]
        self.temp_pieces = 0
        self.player1 = p1
        self.player2 = p2
        self.current_player = self.player1
        self.result = 0  #先手胜1平0负-1
        self.current_player_start = 1
        self.end = 0
        self.round = 0
        self.all_round = 0
        self.all_move = []
        self.next_move = 0
        self.not_end_number = 1
        self.winner = 0
        self.all_prob = []

    def move(self):
        start = self.next_move//100
        end = self.next_move%100
        self.my_piece = self.situation[start// 10][start% 10]
        self.op_piece = self.situation[end//10][end%10]
        if self.op_piece < 0:
            self.eat(self.op_piece)
        self.my_pieces.remove(self.my_piece)
        self.my_pieces.append(self.my_piece//100*100+end)
        self.situation[end// 10][end% 10] = self.my_piece//100*100+end
        self.situation[start// 10][start% 10] = 0
        self.round+=1
        self.all_round+=1
        self.change_side()

    def save_data(self, board_move_data,board_round,board_result,n):
        rb = xlrd.open_workbook(r'result.xls')
        wb = copy(rb)
        ws = wb.get_sheet(0)
        ws.write(n, 0, str(n))
        ws.write(n, 1, str(board_round))
        ws.write(n, 2, str(board_result))
        for m in range(len(board_move_data)):
            ws.write(n, 3+m, str(board_move_data[m]))
        wb.save('result.xls')

    def change_side(self):
        self.temp_pieces = self.my_pieces
        self.my_pieces = [-x for x in self.op_pieces] # (9-(-x)%100//10)*10+(-x)%10+(-x)//100*100
        self.op_pieces = [-x for x in self.temp_pieces]  #-((9-x%100//10)*10+x %10+x //100*100)
        self.situation_temp = self.situation
        for i in range(10):
            for j in range(9):
                self.situation[i][j] = -self.situation_temp[i][j]
        if self.player1 + self.player2 == 1:
            self.current_player = 1 - self.current_player
        self.current_player_start = -self.current_player_start

    def decode_data(self,mcts):
        net_train_data = []
        for i in range(len(mcts.all_prob)):
            net_train_data.append([mcts.all_prob[i][0].decode_board(), mcts.all_prob[i][1].tolist(),self.result])
        return net_train_data

    def decode_board(self):
        #input  输入：己方平面7个，是否是先手,对方平面7个,己方棋子布局，对方棋子布局，
        #对方上次移动的位置，我方可用的行动3个平面  共21个平面
        net_inut  = [None] * 21
        for i in range(21):
            net_inut[i] = [None] * 10
            for j in range(10):
                net_inut[i][j] = [0] * 9
        #14
        for i in range(10):
            for j in range(9):
                if self.situation[i][j]!=0:
                    net_inut[self.situation[i][j]//100+7][i][j]=1
                    if self.situation[i][j]>0:
                        net_inut[15][i][j] = 1
                    else:
                        net_inut[16][i][j] = 1
                net_inut[7][i][j]=abs(self.current_player_start)
        a = self.next_move//100
        net_inut[17][9-a//10][8-a%10] = 1

        for i in self.valid_move:

            i = self.decode_move(i)

            if i < 90:
                net_inut[18][i // 9][i% 9] = 1
            elif i <180:
                net_inut[19][(i-90) // 9][(i-90) % 9] = 1
            else:
                net_inut[20][(i - 180) // 9][4] = 1
        return net_inut

    def decode_move(self,move):
        # from xyab to [187]
        start = move//100
        end = move%100

        piece_type = self.situation[start//10][start%10]//100
        delta = end-start
        count = self.same_piece_count(piece_type,start)

        if piece_type == 1:  # 帅
            dict = {1: 183, -1: 184, 10: 185, -10: 186}
            return dict[delta]

        elif piece_type == 2:  # 士
            if count==1:
                dict = {9:80,-9:81,11:82,-11:83}
            else:
                dict = {9:170,-9:171,11:172,-11:173}
            return dict[delta]

        elif piece_type == 3:  # 象
            if count==1:
                dict = {18:76,-18:77,22:78,-22:79}
            else:
                dict = {18:166,-18:167,22:168,-22:169}
            return dict[delta]


        elif piece_type == 4:  # 马
            if count==1:
                dict = {8:68,-8:69,12:70,-12:71,19:72,-19:73,21:74,-21:75}
            else:
                dict = {8:158,-8:159,12:160,-12:161,19:162,-19:163,21:164,-21:165}
            return dict[delta]


        elif piece_type == 5:  # 车
            if count==1:
                dict = {1:0,2:1,3:2,4:3,5:4,6:5,7:6,8:7,-1:8,-2:9,-3:10,-4:11,-5:12,-6:13,-7:14,-8:15,10:16,20:17,30:18,40:19,50:20,60:21,70:22,80:23,90:24,-10:25,-20:26,-30:27,-40:28,-50:29,-60:30,-70:31,-80:32,-90:33}
            else:
                dict = {1:90,2:91,3:92,4:93,5:94,6:95,7:96,8:97,-1:98,-2:99,-3:100,-4:101,-5:102,-6:103,-7:104,-8:105,10:106,20:107,30:108,40:109,50:110,60:111,70:112,80:113,90:114,-10:115,-20:116,-30:117,-40:118,-50:119,-60:120,-70:121,-80:122,-90:123}
            return dict[delta]

        elif piece_type == 6:  # 炮
            if count==1:
                dict = {1:34,2:35,3:36,4:37,5:38,6:39,7:40,8:41,-1:42,-2:43,-3:44,-4:45,-5:46,-6:47,-7:48,-8:49,10:50,20:51,30:52,40:53,50:54,60:55,70:56,80:57,90:58,-10:59,-20:60,-30:61,-40:62,-50:63,-60:64,-70:65,-80:66,-90:67}

            else:
                dict = {1:124,2:125,3:126,4:127,5:128,6:129,7:130,8:131,-1:132,-2:133,-3:134,-4:135,-5:136,-6:137,-7:138,-8:139,10:140,20:141,30:142,40:143,50:144,60:145,70:146,80:147,90:148,-10:149,-20:150,-30:151,-40:152,-50:153,-60:154,-70:155,-80:156,-90:157}
            return dict[delta]

        elif piece_type == 7:  # 兵
            if count==1:
                dict = {1:84,-1:85,10:86,-10:86}
            elif count==2:
                dict = {1:87,-1:88,10:89,-10:89}
            elif count==3:
                dict = {1:180,-1:181,10:182,-10:182}
            elif count==4:
                dict = {1:174,-1:175,10:176,-10:176}
            else:
                dict = {1:177,-1:178,10:179,-10:179}
            return dict[delta]

    def same_piece_count(self,piece_type,loction):
        loction_x = loction//10
        loction_y = loction%10
        count = 1
        for i in range(loction_x):
            for j in range(loction_y):
                if self.situation[i][j]//100 == piece_type:
                    count+=1
        return count

    def eat(self, op_piece):
        self.op_pieces.remove(op_piece)
        self.round = -1

    def print_result(self,n):
        #红方=先手方
        if self.result == 1:
            r = '红方胜'
            print('第%d局结束，%s' % (n, r))
        elif self.result == -1:
            r = '黑方胜'
            print('第%d局结束，%s' % (n, r))
        else:
            r = '平局'
            print(self.result,'第%d局结束，%s' % (n, r))

    def find_move(self):
        self.valid_move = []
        for p in self.my_pieces:
            piece_type = p//100
            c = p%100
            if piece_type == 1:  # 帅
                self.valid = [10,-10,1,-1]
                for i in range(4):
                    c_t = c + self.valid[i]
                    if c_t not in [3,4,5,13,14,15,23,24,25,73,74,75,83,84,85,93,94,95]:  # 出格子
                        continue
                    if self.situation[c_t//10][c_t%10] > 0:   # 被自己棋子卡住
                        continue
                    self.valid_move.append(c*100+c_t)

            elif piece_type == 2:  # 士
                self.valid = [11, -11, 9, -9]
                for i in range(4):
                    c_t = c + self.valid[i]
                    if c_t not in [3, 5, 14, 23, 25,73,75,84,93,95]:        # 出格子
                        continue
                    if self.situation[c_t//10][c_t%10] > 0:  # 被自己棋子卡住
                        continue
                    self.valid_move.append(c*100+c_t)

            elif piece_type == 3:  # 象
                self.valid = [18, -18, 22, -22]
                self.block = [9, -9, 11, -11]
                for i in range(4):
                    c_t = c + self.valid[i]
                    if c_t not in [2, 6, 20, 24, 28, 42, 46,92,96,70,74,78,52,56]:   # 出格子
                        continue
                    if self.situation[c_t // 10][c_t % 10] > 0: # 被自己棋子卡住
                        continue
                    c_block = c + self.block[i]
                    if c_block < 0 or c_block >98 or c_block%10==9:        # 出格子
                        continue
                    if self.situation[c_block//10][c_block%10]: #堵象眼
                        continue
                    self.valid_move.append(c*100+c_t)

            elif piece_type == 4:  # 马
                self.valid = [8, -8, 12, -12, 19, -19, 21, -21]
                self.block = [-1, 1, 1, -1, 10, -10, 10, -10]
                for i in range(8):
                    c_t = c + self.valid[i]
                    if c_t < 0 or c_t >98 or c_t%10==9:        # 出格子
                        continue
                    if self.situation[c_t//10][c_t%10] > 0:                     # 被自己棋子卡住
                        continue
                    c_block = c + self.block[i]
                    if c_block < 0 or c_block >98 or c_block%10==9:        # 出格子
                        continue
                    if self.situation[c_block // 10][c_block % 10]:             # 堵马腿
                        continue
                    self.valid_move.append(c*100+c_t)

            elif piece_type == 5:  # 车
                self.valid = [1,-1,10,-10]
                for i in self.valid:
                    c_t = c + i
                    if c_t < 0 or c_t > 98 or c_t % 10 == 9:
                        continue
                    while self.situation[c_t//10][c_t%10] == 0 :
                        self.valid_move.append(c*100+c_t)
                        c_t += i
                        if c_t < 0 or c_t >98 or c_t%10==9:
                            break
                    if c_t < 0 or c_t > 98 or c_t % 10 == 9:
                        continue
                    if self.situation[c_t//10][c_t%10] < 0:
                        self.valid_move.append(c*100+c_t)

            elif piece_type == 6:  # 炮
                self.valid = [1,-1,10,-10]
                for i in self.valid:
                    c_t = c + i
                    if c_t < 0 or c_t > 98 or c_t % 10 == 9:
                        continue
                    while self.situation[c_t//10][c_t%10] == 0 :
                        self.valid_move.append(c*100+c_t)
                        c_t += i
                        if c_t < 0 or c_t >98 or c_t%10==9:
                            break
                    if c_t < 0 or c_t > 98 or c_t % 10 == 9:
                        continue
                    c_t += i
                    if c_t < 0 or c_t > 98 or c_t % 10 == 9:
                        continue
                    while self.situation[c_t//10][c_t%10] == 0 :
                        c_t += i
                        if c_t < 0 or c_t >98 or c_t%10==9:
                            c_t=-100
                            break
                    if c_t < 0 or c_t > 98 or c_t % 10 == 9:
                        continue
                    if self.situation[c_t//10][c_t%10] < 0:
                        self.valid_move.append(c*100+c_t)

            elif piece_type == 7:  # 兵
                if self.current_player_start == 1:
                    self.valid = [10]
                    if c//10 > 4:
                        self.valid = [10,1,-1]
                else:
                    self.valid = [-10]
                    if c//10 < 5:
                        self.valid = [-10,1,-1]
                for i in range(len(self.valid)):
                    c_t = c + self.valid[i]
                    if c_t < 0 or c_t >98 or c_t%10==9:        # 出格子
                        continue
                    if self.situation[c_t//10][c_t%10] > 0:    # 被自己棋子卡住
                        continue
                    self.valid_move.append(c*100+c_t)

    def not_end(self):
        self.find_move()
        if (not self.valid_move)or (not (1 in [p//100 for p in self.my_pieces])):
            self.not_end_number = 0
            self.winner = -self.current_player_start
            self.result = self.winner
            return
        if self.round > 120:
            self.not_end_number = 0
            return
        for p in self.my_pieces:
            if p // 100 == 1:
                my_king = p%100
        for p in self.op_pieces:
            if (-p) // 100 == 1:
                op_king = (-p)%100
        if my_king%10 == op_king%10:
            for i in range(my_king//10+1,op_king//10):
                if self.situation[i][op_king%10]!=0:
                    return
            self.not_end_number = 0
            self.winner = self.current_player_start
            self.result = self.winner






