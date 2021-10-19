# 本文件存放ai的主要计算函数，包括极大极小搜索、ab剪枝等

import numpy as np
import random

import const
import evaluate
import generate

# 下面两个棋子移动函数供AI_action内部使用

count_pruning = 0   # 记录剪枝次数
infomation_str = ''


def __move(gobang_board, player, rc_pos):
    r, c = rc_pos
    gobang_board[r][c] = player


def __remove(gobang_board, rc_pos):
    r, c = rc_pos
    gobang_board[r][c] = const.EMPTY


def show_searching_info(depth, rc_pos, alpha, beta, score):  # 展示搜索过程中的信息
    print("当前为第", const.DEPTH-depth+1, "层，正在搜索", rc_pos)
    print("α=", alpha, "，β=", beta)
    if depth >= const.DEPTH:
        print(rc_pos, "的分数：", score)
        print("已剪枝", count_pruning, "次")
        print("human的棋型:", evaluate.count_chess_type_human)
        print("ai   的棋型:", evaluate.count_chess_type_ai)
        print()


def update_search_info(string):
    global infomation_str
    if string == '':
        infomation_str = string
    else:
        infomation_str += string


def consider_one_move(gobang_board):
    # 仅考虑一层深度的搜索方法
    # 返回当前局面对于ai而言的最佳下棋位置
    moves = generate.generate(gobang_board, const.AI)
    best_move_pos_list = []

    max_score = const.SCORE_MIN
    for rc_pos in moves:
        __move(gobang_board, const.AI, rc_pos)
        # 因为已经走了一步，故此层为min层，取最小值
        score = evaluate.evaluate(gobang_board, const.HUMAN)
        r, c = rc_pos
        score += const.POS_SCORE[r][c]  # 加上位置得分，使得ai选择尽量靠中间的位置下棋
        if score > max_score:
            max_score = score
            best_move_pos_list = [rc_pos]
        elif score == max_score:
            best_move_pos_list.append(rc_pos)
        __remove(gobang_board, rc_pos)

    length = len(best_move_pos_list)
    best_move_pos = best_move_pos_list[random.randint(
        0, length-1)]  # 若有多个最优位置，随机选择
    return best_move_pos


def get_max(gobang_board, player, depth):
    # 选择当前局面的孩子局面中的最大者，返回其得分
    value = evaluate.evaluate(gobang_board, player)
    # 若节点为终止节点，或深度达到限制
    if depth == 0 or abs(value) > const.SHAPE_SCORE[const.FIVE]/2:
        return value

    moves = generate.generate(gobang_board, player)
    max_score = const.SCORE_MIN  # 初始化为最小值
    for rc_pos in moves:
        __move(gobang_board, player, rc_pos)
        score = get_min(gobang_board, -player, depth-1)
        if score > max_score:
            max_score = score
        __remove(gobang_board, rc_pos)
    return max_score


def get_min(gobang_board, player, depth):
    # 选择当前局面的孩子局面中的最小者，返回其得分
    score = evaluate.evaluate(gobang_board, player)
    # 若节点为终止节点，或深度达到限制
    if depth == 0 or abs(score) > const.SHAPE_SCORE[const.FIVE]/2:
        return score

    moves = generate.generate(gobang_board, player)
    min_score = const.SCORE_MAX  # 初始化为最小值
    for rc_pos in moves:
        __move(gobang_board, player, rc_pos)
        score = get_max(gobang_board, -player, depth-1)

        print(rc_pos, "的分数：", score)
        print("human:", evaluate.count_chess_type_human)
        print("ai:", evaluate.count_chess_type_ai)

        if score < min_score:
            min_score = score
        __remove(gobang_board, rc_pos)
    return min_score


def min_max(gobang_board, player, depth):
    # 返回当前局面对于player而言的最佳下棋位置
    moves = generate.generate(gobang_board, player)
    best_move_pos_list = []

    if player == const.MAX_P:
        max_score = const.SCORE_MIN
        for rc_pos in moves:
            __move(gobang_board, player, rc_pos)
            # 因为已经走了一步，故此层为min层，取孩子们的最小值
            score = get_min(gobang_board, -player, depth-1)
            if score > max_score:
                max_score = score
                best_move_pos_list = [rc_pos]
            elif score == max_score:
                best_move_pos_list.append(rc_pos)
            __remove(gobang_board,  rc_pos)
    else:
        min_score = const.SCORE_MAX
        for rc_pos in moves:
            __move(gobang_board, player, rc_pos)
            # 因为已经走了一步，故此层为max层，取孩子们的最大值
            score = get_max(gobang_board, -player, depth-1)
            if score < min_score:
                min_score = score
                best_move_pos_list = [rc_pos]
            elif score == min_score:
                best_move_pos_list.append(rc_pos)
            __remove(gobang_board,  rc_pos)

    length = len(best_move_pos_list)
    best_move_pos = best_move_pos_list[random.randint(
        0, length-1)]  # 若有多个最优位置，随机选择
    return best_move_pos


def alpha_pruning(gobang_board, player, depth, alpha, beta):
    # α剪枝，本函数实际由max函数修改而来
    global count_pruning

    score = evaluate.evaluate(gobang_board, player)
    # 若节点为终止节点，或深度达到限制
    if depth == 0 or abs(score) > const.SHAPE_SCORE[const.FIVE]/2:
        return score

    moves = generate.generate(gobang_board, player)
    for rc_pos in moves:
        __move(gobang_board, player, rc_pos)
        new_alpha = beta_pruning(gobang_board, -player, depth-1, alpha, beta)
        __remove(gobang_board, rc_pos)
        if new_alpha > alpha:
            alpha = new_alpha
        if beta <= alpha:
            count_pruning += 1  # 剪枝次数加一
            break
    return alpha


def beta_pruning(gobang_board, player, depth, alpha, beta):
    # β剪枝，本函数实际上由min函数修改而来
    global count_pruning

    score = evaluate.evaluate(gobang_board, player)
    # 若节点为终止节点，或深度达到限制
    if depth == 0 or abs(score) > const.SHAPE_SCORE[const.FIVE]/2:
        return score

    moves = generate.generate(gobang_board, player)
    for rc_pos in moves:
        __move(gobang_board, player, rc_pos)
        new_beta = alpha_pruning(gobang_board, -player, depth-1, alpha, beta)
        __remove(gobang_board, rc_pos)

        show_searching_info(depth, rc_pos, alpha, beta, new_beta)  # 展示搜索信息

        if new_beta < beta:
            beta = new_beta
        if beta <= alpha:
            count_pruning += 1  # 剪枝次数加一
            break
    return beta


def alpha_beta(gobang_board, player, depth):
    # 返回当前局面对于player而言的最佳下棋位置，本函数由minmax函数修改而来
    global count_pruning
    update_search_info('')
    count_pruning = 0   # 每调用一次ab剪枝，清0一次剪枝次数，因为函数中分别调用a剪枝和b剪枝

    alpha, beta = const.SCORE_MIN, const.SCORE_MAX
    moves = generate.generate(gobang_board, player)
    best_move_pos = (None, None)

    if player == const.MAX_P:
        for rc_pos in moves:
            __move(gobang_board, player, rc_pos)
            # 因为已经走了一步，故此层为min层，使用β剪枝
            score = beta_pruning(gobang_board, -player, depth-1, alpha, beta)
            __remove(gobang_board, rc_pos)

            show_searching_info(depth, rc_pos, alpha, beta, score)  # 展示搜索信息
            update_search_info(str(rc_pos)+"搜索完毕，得分"+str(score)+'\n')

            if score > alpha:
                alpha = score
                best_move_pos = rc_pos
                if score > const.SHAPE_SCORE[const.FIVE]/2:
                    break   # 如果已经找到获胜点，则退出
            # 剪枝算法不能考虑score=alpha的情况，因为score的计算不完全
            # elif score == beta:
            #     best_move_pos_list.append(rc_pos)
    else:
        for rc_pos in moves:
            __move(gobang_board, player, rc_pos)
            # 因为已经走了一步，故此层为max层，α剪枝
            score = alpha_pruning(gobang_board, -player, depth-1, alpha, beta)
            __remove(gobang_board, rc_pos)
            if score < beta:
                beta = score
                best_move_pos = rc_pos
                if score < -const.SHAPE_SCORE[const.FIVE]/2:
                    break   # 如果已经找到获胜点，则退出
            # elif score == beta:
            #     best_move_pos_list.append(rc_pos)

    return best_move_pos


if __name__ == "__main__":
    pass
