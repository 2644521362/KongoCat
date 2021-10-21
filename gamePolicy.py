import random
import numpy as np
import keras
from collections import deque
from keras.models import Model
from keras.layers import Input, Dense
from keras.optimizer_v2.adam import Adam

import cardGame
import cardGame as card
import os

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'


def myNetWork():  # 创建卷积神经网络  3层全连接层  最后一层输出5个结果
    Inputs = Input(shape=(20,))
    X = Dense(24, activation='relu')(Inputs)
    X = Dense(24, activation='relu')(X)
    X = Dense(5)(X)

    model = Model(inputs=Inputs, outputs=X)
    model.compile(loss='mse', optimizer=Adam(learning_rate=0.001))
    return model


def replay(action_size, state_size, batch_size, Memory, model, gamma):  # 进行自我训练

    minibatch = random.sample(Memory, batch_size)
    States = np.empty((batch_size, state_size))
    Labels = np.empty((batch_size, action_size))
    i = 0
    for state, action, reward, next_state, done in minibatch:  # 挑状态进行训练

        if not done:
            target = reward + gamma * np.amax(model.predict(next_state)[0])  # bellman方程 reward+预期 这里预期不好计算 用预测结果进行代替
        else:
            target = reward

        label = model.predict(state)
        label[0][action] = target
        States[i, :] = state
        Labels[i, :] = label
        i += 1
    model.fit(States, Labels, epochs=1, verbose=0)  # fit
    return model


def myTrainNetWork(Episodes=100, batch_size=1800):  # 训练
    gamma = 0.75
    epsilon = 0.8
    done = False
    Memory = deque(maxlen=2000)
    game = card.GameState()
    model = myNetWork()
    weights_path = './weight.h5'
    try:
        model.load_weights(weights_path)  # 尝试读取权重参数
        print("load weights succeed")
    except OSError:
        print("no weights found")

    for e in range(Episodes):  # 进行游戏
        game = card.GameState()
        state = np.reshape(game.data, [1, 20])  # 状态转换成1*20格式化矩阵
        score = 0
        for time in range(1000):
            state = np.reshape(game.data, [1, 20])
            action = act(state, epsilon, model)  # 行动获得
            epsilon = epsilon_update(epsilon)  # epsilon缩小
            next_state, reward, done = game.frame_step(action)  # 获得下一状态
            score += reward  # 计算得分
            next_state = np.reshape(next_state, [1, 20])  # 结果转换
            Memory = remember(Memory, state, action, reward, next_state, done)  # 保存留着做计算
            state = next_state
            if done:
                print("episode: {}/{}, score: {}, epsilon: {:.2}".format(e, Episodes, score, epsilon))
                print(state)
                # define the score as the number of actions taken
                break
            if len(Memory) > batch_size:  # 放置存太多溢出
                model = replay(5, 20, batch_size, Memory, model, gamma)
                Memory = deque(maxlen=2000)
            # train the model after the Memory is enough
    model.save_weights(weights_path)  # 保存
    print('weights saved after {} episode'.format(e))
    # save the model
    return


def remember(Memory, state, action, reward, next_state, done):  # 保存结果
    Memory.append((state, action, reward, next_state, done))
    return Memory


def epsilon_update(epsilon, epsilon_min=0.01, epsilon_decay=0.995):  # 更新epsilon随机参数
    if epsilon > epsilon_min:
        epsilon *= epsilon_decay

    return epsilon


def act(state, epsilon, model):  # 利用epsilon进行进行 预测或者进行随机
    s = 0  # s存手牌数 手牌为0的时候不能进行出牌
    for i in state[0][0:4]:
        s += i
    if s == 0:
        return 0
    if np.random.rand() <= epsilon:
        act = random.randrange(0, 5)
        if act != 0:
            while state[0][act - 1] <= 0:
                act = random.randrange(1, 5)

        return act
    act_values = model.predict(state)
    act = np.argmax(act_values[0])
    if act != 0 and state[0][act - 1] <= 0:
        return 0
    return np.argmax(act_values[0])


class gamePolicy:
    def __init__(self):
        self.model = myNetWork()
        weights_path = './weight.h5'
        game = card.GameState()
        try:
            self.model.load_weights(weights_path)
            print("load weights succeed")
        except OSError:
            print("no weights found")

    def getRes(self, data):  # data is 4*5
        act = self.model.predict(np.reshape(data, [1, 20]))
        return act



if __name__ == '__main__':
    p = gamePolicy()
    print(np.zeros((5, 4)))
    #res = p.getRes(np.zeros((5, 4)))
