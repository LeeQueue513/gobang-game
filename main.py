import numpy as np
import random
import tkinter as tk
from tkinter import scrolledtext
from tkinter import END

import const
import evaluate
import generate
import AI_action

player = const.HUMAN    # 表示谁正要走棋

gobang_board = np.zeros((const.SIDE_LEN, const.SIDE_LEN)).reshape(
    (const.SIDE_LEN, const.SIDE_LEN))


class Draw_chess:
    window = None
    canvas = None
    scr = None  # 右侧滚动文本框
    rect = None  # 小方块，用于标记刚刚下在哪里
    rect_xy_pos = None  # 记录小方框的位置
    rc_pos = None   # 点击位置

    def __init__(self):
        # 目前仅支持绘制15*15的棋盘，其他可能出现错误

        # 常量赋值
        self.SIDE_LEN = const.SIDE_LEN
        self.CANVAS_SIDE_LENGTH = 435
        self.BOARD_SIDE_LENGTH = 400
        self.SIDE = (self.CANVAS_SIDE_LENGTH -
                     self.BOARD_SIDE_LENGTH)/2  # 周围边框宽度
        self.DELTA = (self.BOARD_SIDE_LENGTH-2)/(self.SIDE_LEN-1)

        # 实例化object，建立窗口window
        self.window = tk.Tk()
        # 给窗口的可视化起名字
        self.window.title('五子棋游戏')
        # 设定窗口的大小(长 * 宽)
        self.window.geometry('810x500')  # 这里的乘是小x

        # 绘制画布
        canvas_pos = (30, 30)
        self.__draw_canvas(canvas_pos)
        rspos, cspos = (30, 10), (10, 40)
        self.__draw_rows_and_cols(rspos, cspos)
        # 绘制右边的控制栏
        scroll_pos = (530, 70)
        self.__draw_control(scroll_pos)

        self.window.mainloop()

    def __draw_canvas(self, canvas_pos):
        x, y = canvas_pos

        self.canvas = tk.Canvas(self.window, bg='#cd762f',
                                height=self.CANVAS_SIDE_LENGTH, width=self.CANVAS_SIDE_LENGTH)

        self.canvas.bind("<Button-1>", self.take_one_turn)    # 监听左键

        # 画纵横线
        for i in range(self.SIDE_LEN+1):
            pos = i*self.DELTA
            self.canvas.create_line(
                self.SIDE, self.SIDE+pos, self.SIDE+self.BOARD_SIDE_LENGTH, self.SIDE+pos)
            self.canvas.create_line(
                self.SIDE+pos, self.SIDE, self.SIDE+pos, self.SIDE+self.BOARD_SIDE_LENGTH)

        # 画五个定位点
        point_rc_pos_list = [(3, 3), (3, 11), (7, 7), (11, 3), (11, 11)]
        for rc_pos in point_rc_pos_list:
            self.draw_pieces(const.HUMAN, rc_pos, 3, False)

        self.canvas.place(x=x, y=y)
        # self.draw_0123(canvas_pos)

    def draw_pieces(self, player, rc_pos, RADIUS=10, draw_rect=True):
        x, y = self.__convert_rc_2_xy(rc_pos)
        color = 'black' if player == const.HUMAN else 'white'
        self.canvas.create_oval(x-RADIUS, y-RADIUS, x +
                                RADIUS, y+RADIUS, fill=color, outline=color)
        if draw_rect == True:
            if self.rect == None:
                self.rect = self.canvas.create_rectangle(
                    x-15, y-15, x+15, y+15, outline="#c1005d")
                self.rect_xy_pos = (x, y)
            else:
                rc_pos = self.__convert_xy_2_rc((x, y))
                old_x, old_y = self.rect_xy_pos
                new_x, new_y = self.__convert_rc_2_xy(rc_pos)
                dx, dy = new_x-old_x, new_y-old_y
                self.canvas.move(self.rect, dx, dy)
                self.rect_xy_pos = (new_x, new_y)
        self.canvas.update()    # 更新画布显示

    def __convert_rc_2_xy(self, rc_pos):
        # 传入棋子在棋盘上的r、c值，传出其在canvas上的坐标位置
        r, c = rc_pos
        x = c*self.DELTA+self.SIDE
        y = r*self.DELTA+self.SIDE
        return x, y

    def __convert_xy_2_rc(self, xy_pos):
        # 传入xy值，传出rc坐标
        x, y = xy_pos
        r = round((y-self.SIDE)/self.DELTA)
        c = round((x-self.SIDE)/self.DELTA)
        return r, c

    # def draw_0123(self, xy_pos):
    #     x, y = xy_pos
    #     w = tk.Label(
    #         self.window, text="   0     1     2      3     4      5     6      7     8     9    10    11    12    13   14")
    #     ww = tk.Label(
    #         self.window, text="0\n1\n\n2\n\n3\n4\n\n5\n\n6\n7\n\n8\n\n9\n10\n\n11\n\n12\n13\n\n14")
    #     w.place(x=x, y=y)
    #     ww.place(x=x, y=y)

    def __draw_control(self, xy_pos):
        x, y = xy_pos
        self.scr = tk.scrolledtext.ScrolledText(
            self.window, width=35, height=30)
        self.scr.place(x=x, y=y)
        self.insert_into_src("等待黑方行动")

    def __draw_rows_and_cols(self, rspos, cspos):
        rx, ry = rspos
        cx, cy = cspos
        rlabel = tk.Label(
            self.window, text="   0     1     2      3     4      5     6      7     8     9    10    11    12    13   14    ")
        for i in range(const.SIDE_LEN):
            clabel = tk.Label(self.window, text=str(i))
            clabel.place(x=cx, y=cy+28.2*i)
        rlabel.place(x=rx, y=ry)

    def insert_into_src(self, string):
        self.scr.insert(END, string+'\n')
        self.scr.see(END)
        self.scr.update()

    def take_one_turn(self, event):
        # HUMAN行动
        x, y = event.x, event.y
        r, c = self.__convert_xy_2_rc((x, y))
        # 下一步棋
        move(const.HUMAN, (r, c))
        self.draw_pieces(const.HUMAN, (r, c))
        # 判断是否获胜
        if evaluate.judge_game_win(gobang_board, (r, c)):
            # 进行获胜相应显示
            self.insert_into_src("黑方获胜！！!")
            self.canvas.unbind("<Button-1>")
            return
        else:
            self.insert_into_src("黑方行动完毕\n")

        # AI行动
        self.insert_into_src("白方正在思考...")
        r, c = get_move_ai()
        self.insert_into_src(AI_action.infomation_str)
        # 下一步棋
        move(const.AI, (r, c))
        self.draw_pieces(const.AI, (r, c))
        # 判断是否获胜
        if evaluate.judge_game_win(gobang_board, (r, c)):
            # 进行获胜相应显示
            self.insert_into_src("白方获胜！！!")
            self.canvas.unbind("<Button-1>")
            return
        else:
            # 交替行动
            self.insert_into_src("白方行动完毕\n")
            self.insert_into_src("等待黑方行动")


def move(player, pos):  # 传入玩家和落子位置，下一步棋
    global gobang_board

    r, c = pos
    gobang_board[r][c] = player


def remove(player, pos):    # 撤回刚刚下的棋
    global gobang_board

    r, c = pos
    gobang_board[r][c] = const.EMPTY


def get_move_human_by_keyboard():     # 从键盘输入
    # 读取人的行棋
    global gobang_board

    while True:
        s = input("请输入下棋位置坐标：")
        # 人为保证输入正确
        first_space = s.index(" ")
        r = int(s[:first_space])
        c = int(s[first_space+1:])

        if gobang_board[r][c] != const.EMPTY:
            print("该位置已经有棋子！")
        else:
            break

    return r, c


def get_move_ai():
    # 返回ai决定的落子点
    global gobang_board
    return AI_action.alpha_beta(gobang_board, const.AI, const.DEPTH)
    # return AI_action.consider_one_move(gobang_board)


if __name__ == "__main__":
    Draw_chess()

# 5 5
# 5 7
# 4 6
# 3 5
# 2 4


# 5 5
# 5 7
# 4 6
# 6 8
# 6 4
