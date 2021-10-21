import numpy as np
import random
import math


class GameState:
    role = 0

    def __init__(self):
        # 五行四列 玩家 对手 棋局 弃牌堆 弃牌堆顶和次堆顶  1红桃 2黑桃 3方片 4梅花
        self.data = np.array([[0, 0, 0, 0], [0, 0, 0, 0], [13, 13, 13, 13], [0, 0, 0, 0], [-1, -2, 0, 0]])

    def frame_step(self, input_actions):
        terminal = False
        reward = 0.05
        if input_actions == 0:  # 抽牌(0)
            self.swap_top_two()
            self.drew_one_card()
            reward += 0.05
        if input_actions == 1:  # 放红桃(1)
            self.swap_top_two()
            self.data[0][0] -= 1
            self.data[3][0] += 1
            self.data[4][0] = 1

        if input_actions == 2:  # 放黑桃(2)
            self.swap_top_two()
            self.data[0][1] -= 1
            self.data[3][1] += 1
            self.data[4][0] = 2
        if input_actions == 3:  # 放方片(3)
            self.swap_top_two()
            self.data[0][2] -= 1
            self.data[3][2] += 1
            self.data[4][0] = 3
        if input_actions == 4:  # 放梅花(4)
            self.swap_top_two()
            self.data[0][3] -= 1
            self.data[3][3] += 1
            self.data[4][0] = 4

        if self.check_top_two():  # 检查顶部两张牌是否相同
            self.get_all_card()

        if self.is_terminal():  # 检查游戏是否结束
            terminal = True
            rop = 1
            if self.role == 1:
                rop = 1
            if np.sum(self.data[0]) > np.sum(self.data[1]):  # 游戏结束 进行胜负判定 给出本局得分

                reward += -101 * rop
                reward -= (np.sum(self.data[0]) - np.sum(self.data[1])) * 7  # 胜利得分
                return self.data, reward, terminal
            elif np.sum(self.data[0]) == np.sum(self.data[1]):

                reward += 65  # 平局得分
                return self.data, reward, terminal
            else:

                reward += 101 * rop
                reward -= (np.sum(self.data[0]) - np.sum(self.data[1])) * 7  # 失败得分
            return self.data, reward, terminal
        else:
            if np.sum(self.data[2]) > 26:  # 游戏未结束，进行手牌评估 通过对比手牌数量简单计算得分
                if np.sum(self.data[0]) > np.sum(self.data[1]):
                    reward += 2
                else:
                    reward -= 1
            if np.sum(self.data[2]) <= 26:
                if np.sum(self.data[0]) <= np.sum(self.data[1]):
                    reward += 2
                else:
                    reward -= 2
                if self.data[4][0] > 0 and self.data[2][self.data[4][0] - 1] > self.data[1][self.data[4][0] - 1] + \
                        self.data[0][self.data[4][0] - 1]:  # 进行抽牌得牌概率得分
                    reward += 2
        self.change_role()  # 人机实现自我对战

        datRe = self.data.copy()
        self.data[[0, 1], :] = self.data[[1, 0], :]
        return datRe, reward, terminal

    def is_terminal(self):  # 判断是否结束
        if np.sum(self.data[2]) == 0:
            return True
        return False

    def drew_one_card(self):  # 随机抽牌
        card = random.randrange(0, 4)

        while self.data[2][card] <= 0:
            card = random.randrange(0, 4)
        self.data[3][card] += 1
        self.data[2][card] -= 1
        self.data[4][0] = card + 1

        # print("_______________")
        # print("抽了 --- ",card+1,"----")
        # print(self.data)
        # print("_______________")

    def check_top_two(self):
        if self.data[4][0] == self.data[4][1]:
            return True
        return False

    def swap_top_two(self):
        self.data[4][1] = self.data[4][0]

    def change_role(self):
        self.role += 1
        self.role %= 2

    def get_all_card(self):  # 获得卡牌
        # print(self.role,"   获得了所有牌")
        self.data[0][0] += self.data[3][0]
        self.data[0][1] += self.data[3][1]
        self.data[0][2] += self.data[3][2]
        self.data[0][3] += self.data[3][3]
        self.data[3][0] = 0
        self.data[3][1] = 0
        self.data[3][2] = 0
        self.data[3][3] = 0
        self.data[4][0] = -1
        self.data[4][1] = -2
        # print("获得后")
        # print(self.data)
