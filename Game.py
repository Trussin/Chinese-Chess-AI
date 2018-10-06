from Net import Net
from MCTS import MCTS
from Board import Board

net = Net('./best_policy_1900.model') #'./best_policy_4.model'
count = 5000  # 训练的局数
count_ai = 1
board_move_data = []
board_round = []
board_result = []
# 第一个和第二个棋手，  ai 1   人0
for n in range(1, count + 1):
    board = Board(1, 1)
    m=1
    mcts = MCTS(net, board)
    #print("第%d局开始"% (n))
    while 1:
        board.not_end()
        if not board.not_end_number:
            break
        if board.current_player:
            board.next_move = mcts.get_move()  # 格式 xyab
        else:
            board.next_move = int(input('请输入下一步棋，格式xy ab: '))  # 输入格式 xyab
        board.all_move.append(board.next_move)
        board.move()
        mcts.board = board
        mcts.update_with_move()
        m += 1
        #print("移动了%d步,%d" % (m,board.next_move))

    board.print_result(n)
    board_move_data.append(board.all_move)
    board_round.append(board.all_round)
    board_result.append(board.result)
    net_train_data = board.decode_data(mcts)
    net_train_data = net.get_equi_data(net_train_data)
    net.policy_update(net_train_data)
    if count_ai%100 == 0:
        net.save_model('./best_policy_' + str(count_ai) + '.model')
        board.save_data(board_move_data, board_round, board_result, count_ai//100+1)
    count_ai += 1
    board_move_data = []
    board_round = []
    board_result = []

print('%d次训练完成，程序结束！' % (count))






