# 本文件存放评估局面得分函数
import const

import numpy as np

# 记录棋型个数
count_chess_type_human = None
count_chess_type_ai = None


def reset_count():
    global count_chess_type_human
    global count_chess_type_ai
    count_chess_type_human = [0 for i in range(const.CHESS_TYPE_NUM)]
    count_chess_type_ai = [0 for i in range(const.CHESS_TYPE_NUM)]


def count_line_type(line, who):
    # 传入一行棋盘,检测该数组中出现的棋型数目
    # who参数是指目前统计哪位棋手的棋型,而不是当前谁下
    global count_chess_type_human
    global count_chess_type_human

    line = line.copy()    # 防止统计时line被更改
    len_of_line = len(line)
    count_chess_type = count_chess_type_human if who == const.HUMAN else count_chess_type_ai
    # 记录每个棋子是否已经被计算过,初始化为全false,使用numpy便于切片赋值
    had_cal = np.array([False for i in range(len_of_line)])
    count_not_cal = len_of_line  # 判断当前有几个棋子尚未统计.如果小于5,则不需要再统计,因为没有棋型的长度小于5

    line = [-i for i in line] if who == -1 else line  # 将需要统计的那位转为1,便于统计
    # 这里使用一个技巧,在列表头尾分别插入-1,便于统计棋型
    # 因为棋盘的边界不能下子,和被对方棋子挡住无异
    line.insert(0, -1)  # 头部插入
    line.append(-1)  # 尾部

    # 连五 活四
    for type_name in range(const.FIVE, const.LFOUR+1):
        for each_type_tuple in const.SHAPE_LIST[type_name]:
            each_type = each_type_tuple[0]
            length = each_type_tuple[1]
            for i in range(len_of_line-length+1):
                if line[i:i+length] == each_type:
                    count_chess_type[type_name] += 1
                    return  # 连五活四为必赢棋型,不需要继续检测

    # 冲四 活三 眠三 活二 眠二
    for type_name in range(const.CFOUR, const.STWO+1):
        for each_type_tuple in const.SHAPE_LIST[type_name]:
            # 判断是否还需要继续统计
            if count_not_cal < 5:
                return
            # 统计初始化
            each_type = each_type_tuple[0]
            length_each_type = each_type_tuple[1]
            last_1_next_pos = each_type_tuple[2]
            # 开始统计棋型
            i = 0
            while i <= len_of_line - length_each_type:
                if had_cal[i:i+length_each_type].any() == True:
                    # 如果接下来的一段中存在true,那么就无需统计
                    i += 1
                elif line[i:i+length_each_type] == each_type:
                    count_chess_type[type_name] += 1
                    had_cal[i:i+last_1_next_pos] = True  # 该部分已经统计过
                    count_not_cal -= last_1_next_pos
                    i += last_1_next_pos  # 如果统计出棋型,则跳过一段.否则,加一即可
                else:
                    i += 1


def convert_board_to_list_2021_4_18(gobang_board):
    # 将二维棋盘的每一行/列/斜边分别取出
    # gobang_board = np.array(gobang_board)
    gobang_list = []
    # 横
    for i in gobang_board:
        i = list(i)
        gobang_list.append(i)
    # 竖
    for i in gobang_board.T:
        i = list(i)
        gobang_list.append(i)
    # 斜-左上到右下
    for i in range(0, const.SIDE_LEN-4):
        line = []
        for j in range(const.SIDE_LEN-i):
            line.append(gobang_board[j][j+i])
        gobang_list.append(line)
    for i in range(1, const.SIDE_LEN-4):
        line = []
        for j in range(const.SIDE_LEN-i):
            line.append(gobang_board[j+i][j])
        gobang_list.append(line)
    # 斜-右上到左下
    for i in range(4, const.SIDE_LEN):
        line = []
        for j in range(i+1):
            line.append(gobang_board[j][i-j])
        gobang_list.append(line)
    for i in range(1, const.SIDE_LEN-4):
        line = []
        for j in range(i, const.SIDE_LEN):
            line.append(gobang_board[j][const.SIDE_LEN+i-j-1])
        gobang_list.append(line)

    return gobang_list


def convert_board_to_list_2021_4_20(gobang_board):
    # 原先的convert函数有一个严重的问题：拆解了许多不必要的行列和斜线
    # 一局五子棋中，有许多的行列和斜线都是无子的。这些线没有检查的必要
    # 故作出改进：对于每一个棋子，检查其横纵斜四条线

    # 对于每个棋子进行拆分有个实现的困难：难以判断是否重复拆分某条线
    # 故暂不实现本方法
    return []


def convert_board_to_list(gobang_board):
    # 本方法对上述两个方法都进行改进
    # 扫描棋盘，取出有子的边，并返回边组成的列表
    # gobang_board = np.array(gobang_board)
    gobang_list = []
    # 横
    for i in gobang_board:
        if i.any() != const.EMPTY:
            gobang_list.append(list(i))
    # 竖
    for i in gobang_board.T:
        if i.any() != const.EMPTY:
            gobang_list.append(list(i))
    # 斜-左上到右下
    for i in range(0, const.SIDE_LEN-4):
        line1, line2 = [], []
        for j in range(const.SIDE_LEN-i):
            line1.append(gobang_board[j][j+i])
            line2.append(gobang_board[j+i][j])
        line1, line2 = np.array(line1), np.array(line2)
        if line1.any() != const.EMPTY:
            gobang_list.append(list(line1))
        if i > 0 and line2.any() != const.EMPTY:
            gobang_list.append(list(line2))

    # 斜-右上到左下
    for i in range(4, const.SIDE_LEN):
        line = []
        for j in range(i+1):
            line.append(gobang_board[j][i-j])
        line = np.array(line)
        if line.any() != const.EMPTY:
            gobang_list.append(list(line))
    for i in range(1, const.SIDE_LEN-4):
        line = []
        for j in range(i, const.SIDE_LEN):
            line.append(gobang_board[j][const.SIDE_LEN+i-j-1])
        line = np.array(line)
        if line.any() != const.EMPTY:
            gobang_list.append(list(line))

    return gobang_list


def count_board_type(gobang_board):
    # 统计整个棋盘的棋型种类
    global count_chess_type_human
    global count_chess_type_ai
    reset_count()
    # 将整个棋盘横竖斜进行划分,形成一个二维数组,其中每个一维数组都是棋盘上的一行/列/斜
    gobang_list = convert_board_to_list(gobang_board)
    for each_line in gobang_list:
        count_line_type(each_line, const.HUMAN)
        if count_chess_type_human[const.FIVE] > 0:  # 如果统计到连五,直接返回
            return
        count_line_type(each_line, const.AI)
        if count_chess_type_ai[const.FIVE] > 0:
            return
        # elif count_chess_type_human[const.LFOUR]+count_chess_type_ai[const.LFOUR] > 0:
        #    return   # 否则,两边若出现活四则也返回


def cal_score(player):
    # 根据棋型统计结果计算得分,返回值为(human_score,ai_score)
    # 注意,必须传入下一步是谁行棋,便于加上行棋手加分
    global count_chess_type_human
    global count_chess_type_ai
    BONUS_SCORE = const.BONUS_SCORE  # 行棋者的加分

    sh, sa = 0, 0  # score_human,score_ai
    ch, ca = count_chess_type_human, count_chess_type_ai

    # 连五 或 活四/冲四+下一步是该选手行棋
    if ch[const.FIVE] > 0:
        return (const.SHAPE_SCORE[const.FIVE], 0)
    elif ca[const.FIVE] > 0:
        return (0, const.SHAPE_SCORE[const.FIVE])
    elif player == const.HUMAN and ch[const.LFOUR]+ch[const.CFOUR] > 0:
        return (const.SHAPE_SCORE[const.LFOUR], 0)
    elif player == const.AI and ca[const.LFOUR]+ca[const.CFOUR] > 0:
        return (0, const.SHAPE_SCORE[const.LFOUR])

    # 活四 双冲四 双活三 冲四活三
    if ch[const.LFOUR] > 0 or ch[const.CFOUR]+ch[const.LTHREE] >= 2:  # 冲四活三若大于2,则抵得上一个活四
        sh += const.SHAPE_SCORE[const.LFOUR]
    if ca[const.LFOUR] > 0 or ca[const.CFOUR]+ca[const.LTHREE] >= 2:
        sa += const.SHAPE_SCORE[const.LFOUR]
    if sa+sh > 0:
        # 如果出现必赢棋型,返回
        return (sh, sa)

    # 单冲四 单活三统计
    sh += ch[const.CFOUR]*const.SHAPE_SCORE[const.CFOUR]
    sh += ch[const.LTHREE]*const.SHAPE_SCORE[const.LTHREE]
    if player == const.HUMAN and sh > 0:
        sh += BONUS_SCORE
    sa += ca[const.CFOUR]*const.SHAPE_SCORE[const.CFOUR]
    sa += ca[const.LTHREE]*const.SHAPE_SCORE[const.LTHREE]
    if player == const.AI and sa > 0:
        sa += BONUS_SCORE
    if sa+sh > 0:
        # 如果出现特殊棋型,加上加分,返回
        return (sh, sa)

    # 前面使用许多的return，是因为眠三、眠二棋型太多，不便统计
    # 因此，能不统计就不统计
    # 其他棋型的统计
    for i in range(const.STHREE, const.CHESS_TYPE_NUM):
        sh += ch[i]*const.SHAPE_SCORE[i]
        sa += ca[i]*const.SHAPE_SCORE[i]

    return (sh, sa)


def evaluate(gobang_board, player):
    # 评估函数,返回当前局面对ai的有利性,ai越有利,返回越大
    # evaluate函数必须知道下一步是谁行棋
    count_board_type(gobang_board)
    score_human, score_ai = cal_score(player)
    return score_ai-score_human


def convert_point_to_list(gobang_board, rc_pos):
    # 传入一颗棋子，返回其横三行、纵三行、斜四边列表
    # 仅返回大于等于5的边
    r, c = rc_pos
    point_line_list = []
    # 横
    point_line_list.append(list(gobang_board[r]))
    # if r > 0 and gobang_board[r-1].any() != const.EMPTY:
    #     point_line_list.append(list(gobang_board[r-1]))
    # if r < const.SIDE_LEN-1 and gobang_board[r+1].any() != const.EMPTY:
    #     point_line_list.append(list(gobang_board[r+1]))
    # 竖
    point_line_list.append(list(gobang_board.T[c]))
    # if c > 0 and gobang_board.T[c-1].any() != const.EMPTY:
    #     point_line_list.append(list(gobang_board.T[c-1]))
    # if c < const.SIDE_LEN-1 and gobang_board.T[c+1].any() != const.EMPTY:
    #     point_line_list.append(list(gobang_board.T[c+1]))
    # 斜-左上到右下
    delta = r-c
    start_r, end_r = 0, const.SIDE_LEN
    abs_delta = abs(delta)
    if delta >= 0:
        start_r = abs_delta
    else:
        end_r = const.SIDE_LEN-abs_delta
    line = []
    for i in range(start_r, end_r):
        line.append(gobang_board[i][i-delta])   # c=r-delta
    if len(line) >= 5:
        point_line_list.append(line)
    # 斜-右上到左下
    sum_rc = r+c
    if 4 <= sum_rc <= 2*const.SIDE_LEN-6:  # 生成线长度大于等于5
        start_r, end_r = 0, const.SIDE_LEN
        if sum_rc >= const.SIDE_LEN:   # 右下角
            start_r = sum_rc-const.SIDE_LEN+1
        else:
            end_r = sum_rc+1
        line = []
        for i in range(start_r, end_r):
            line.append(gobang_board[i][sum_rc-i])   # c=sum_rc-r
        point_line_list.append(line)

    return point_line_list


def count_point_type(gobang_board, rc_pos):
    # 统计传入棋子位置周围的棋型
    global count_chess_type_human
    global count_chess_type_ai
    reset_count()
    point_line_list = convert_point_to_list(gobang_board, rc_pos)
    for each_line in point_line_list:
        count_line_type(each_line, const.HUMAN)
        if count_chess_type_human[const.FIVE] > 0:  # 如果统计到连五,直接返回
            return
        count_line_type(each_line, const.AI)
        if count_chess_type_ai[const.FIVE] > 0:
            return


def evaluate_point(gobang_board, player, rc_pos):
    # 传入一个位置，大概估计该位置适不适合player下在此处
    # 判断方法：两个人都在此处下一次，结果取两人之差
    r, c = rc_pos
    gobang_board[r][c] = player
    count_point_type(gobang_board, rc_pos)
    score_human, score_ai = cal_score(-player)  # 下棋者反转
    score_1 = score_ai-score_human
    gobang_board[r][c] = -player
    count_point_type(gobang_board, rc_pos)
    score_human, score_ai = cal_score(player)  # 下棋者反转
    score_2 = score_ai-score_human
    gobang_board[r][c] = const.EMPTY
    return score_1-score_2//2


def judge_game_win(gobang_board, rc_pos):
    # 判断是否胜出
    # 因为场上只可能因为最新的一步棋产生连五，故传入刚刚下的位置
    global count_chess_type_human
    global count_chess_type_ai

    count_point_type(gobang_board, rc_pos)
    return True if count_chess_type_human[const.FIVE]+count_chess_type_ai[const.FIVE] > 0 else False


if __name__ == "__main__":
    # 测试用例
    H = const.HUMAN
    A = const.AI
    gobang_board = np.array([
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, H, 0, H, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, A, 0, A, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, A, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    ])

    reset_count()
    count_line_type(list(gobang_board[6]), A)
    # print(evaluate_point(gobang_board, const.AI, (7, 5)))
    print("human:", count_chess_type_human)
    print("ai:", count_chess_type_ai)

    # print("赢了吗?", str(judge_game_win(gobang_board)))
    # i = evaluate(gobang_board, const.AI)
    # print("               5,L4,C4,L3,S3,L2,S2")
    # print("human的棋型: ", count_chess_type_human)
    # print("ai   的棋型: ", count_chess_type_ai)
    # print("评分: ", i)
