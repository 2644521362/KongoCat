# -*- coding:utf-8 -*-
from pathlib import Path

from zhconv import convert
import time
import pypinyin
from pychai import Schema
min_match = 1
max_match = 2
class WordDetect:
    def __init__(self, word_path):
        self.index = 0
        self.answer = []
        self.transfomer_hanzi = {}
        original_sensitive_word = []
        pinyin_sentitive_word = []
        self.already_exist = {}
        self.first_zimu={}
        # --读入敏感词汇 获得pinyin
        with open(word_path, 'r', encoding='utf-8') as file:
            original_sensitive_word = file.readlines()  # 读入文本

        original_sensitive_word = sorted([i.split('\n')[0] for i in original_sensitive_word])  # 按照换行符区分不同敏感词

        for string in original_sensitive_word:
            pinyin_sentitive_word.append(string.lower())
            self.transfomer_hanzi[string.lower()] = string
        filename = r"D:\qqdata\2644521362\FileRecv\ans2.txt"
        pinyin_sentitive_word = list(set(pinyin_sentitive_word))  # 去重
        # 开始做拼音+本体的中文

        # ans_dataset中 1为需要用拼音的地方 0为用中文的地方 2为拆字 3为首字母 开始组词

        for temp_word in pinyin_sentitive_word.copy():  # 注意用copy 不然越打越多

            if ('\u4e00' <= temp_word[0] <= '\u9fff'):  # 识别为汉字

                pinyin = pypinyin.lazy_pinyin(temp_word)  # 拼音数组
                temp_word_respective = []  # 汉字数组 临时每一个单词
                for i in range(len(temp_word)):
                    temp_word_respective.append(temp_word[i])
                ans_dataset = self.subsets(len(temp_word))  # ans_dataset是列表
                for i in ans_dataset:
                    index = 0  # 子列表中第几个数
                    result_word = ""
                    for j in range(len(i)):
                        if i[j] == 1:
                            result_word += temp_word_respective[index]
                        if i[j] == 0:
                            result_word += pinyin[index]
                        if i[j] == 2:
                            result_word += pinyin[index][0]
                            self.first_zimu[pinyin[index][0]]=1
                        index += 1

                    pinyin_sentitive_word.append(result_word)
                    self.transfomer_hanzi[result_word] = temp_word
            else:
                self.transfomer_hanzi[temp_word] = temp_word

        pinyin_sentitive_word = list(set(pinyin_sentitive_word))  # 去重
        print(pinyin_sentitive_word)
        self.sensitive_word_map = self.init_sensitive_word_map(pinyin_sentitive_word)  # 构造trie树

        # print(self.sensitive_word_map.__sizeof__())
        file = open(r"D:\qqdata\2644521362\FileRecv\org.txt", encoding="utf-8")
        lines = 0
        while 1:
            line = file.readline()  # 带缓存的文件读取
            if not line:
                break
            lines += 1
            ans_in_lines = []  # 本行扫描结果
            ans_in_lines.extend(self.get_sensitive_word_list(line, lines, filename))

            for i in ans_in_lines:
                self.answer.append("Line" + str(lines) + ":<" + i[2] + ">" + line[i[0]:i[0] + i[1]] + "\n")


        self.output_doc(filename)
    def init_sensitive_word_map(self, sensitive_word_list):     # 造树过程，sensitive_word_list包含各种组合的敏感词
        sensitive_word_map = {}
        for word in sensitive_word_list:
            now_map = sensitive_word_map

            # 遍历该敏感词的每一个特定字符
            for i in range(len(word)):
                keychar = word[i]
                word_map = now_map.get(keychar)
                if word_map != None:
                    now_map = word_map
                else:
                    new_next_map = {}
                    new_next_map["isEnd"] = 0
                    now_map[keychar] = new_next_map
                    now_map = new_next_map
                    if(keychar.isalpha() and keychar in self.first_zimu):
                        now_map["canBeMore"]=1
                # 到最后一个词
                if i == len(word) - 1:
                    now_map["isEnd"] = 1
                    now_map["word"] = word
                if i == 0:
                    now_map["isStart"] = 1
        return sensitive_word_map

    def get_sensitive_word_list(self, txt, lines, filename):  # 传入（测试文本，没用，没用）返回起始位置、长度、敏感词 三元组
        now_map = self.sensitive_word_map
        start_index = -1
        original_length = -1
        scan_mode = -1  # 1检测中文
        ans_location = []
        index_text=0
        temp_now_map ={}
        ingore_index= -1
        while index_text< len(txt):
            key = txt[index_text]
            if key.isalpha():
                key = key.lower()  # 一律改小写
            if '\u4e00' <= key <= '\u9fff':
                key = convert(key, 'zh-hans')  # 一律转简体

            if not key.isalpha() and not ('\u4e00' <= key <= '\u9fff'):  # 去除掉 符号 空格等
                original_length += 1
                index_text+=1
                continue
            flag_find = key in now_map
            if flag_find:
                now_map = now_map.get(key)
                if now_map.get("isEnd") == 1:  # 结束识别
                    if(not temp_now_map and now_map.get("canBeMore")):
                        if(index_text==len(txt)-1):

                            if str(lines) + str(start_index) not in self.already_exist.keys():
                                ans_location.append(
                                    (start_index, original_length, self.transfomer_hanzi[now_map.get("word")]))
                            self.already_exist[str(lines) + str(start_index)] = 1
                            now_map = self.sensitive_word_map  # 恢复now_map
                            original_length = -1
                            start_index = -1
                            scan_mode = -1
                            self.index += 1
                            index_text += 1
                            temp_now_map={}
                            continue
                        temp_now_map = now_map #保存当前状态
                        ingore_index+=1
                        index_text+=1
                        original_length+=1
                        continue
                    else:
                        print("there1")
                        if str(lines) + str(start_index) not in self.already_exist.keys():
                            ans_location.append((start_index, original_length, self.transfomer_hanzi[now_map.get("word")]))
                        self.already_exist[str(lines) + str(start_index)] = 1
                        now_map = self.sensitive_word_map  # 恢复now_map
                        original_length = -1
                        start_index = -1
                        scan_mode = -1
                        self.index += 1
                        index_text+=1
                        temp_now_map={}
                        continue
                if (now_map.get("isStart") == 1) & (start_index == -1):  # 找到敏感词头
                    if scan_mode == -1 and ('\u4e00' <= key <= '\u9fff'):
                        scan_mode = 1
                    original_length = 1
                    start_index = index_text
                original_length += 1
                index_text+=1
            else:
                if(temp_now_map):
                    if str(lines) + str(start_index) not in self.already_exist.keys():
                        ans_location.append((start_index, original_length-1, self.transfomer_hanzi[temp_now_map.get("word")]))
                    self.already_exist[str(lines) + str(start_index)] = 1
                    now_map = self.sensitive_word_map  # 恢复now_map
                    original_length = -1
                    start_index = -1
                    scan_mode = -1
                    self.index += 1
                    index_text-=ingore_index
                    temp_now_map={}
                    continue
                if scan_mode == 1:
                    if key.isalpha() or key.isdecimal():  # 这里屏蔽不了中文 不知道为啥
                        if not ('\u4e00' <= key <= '\u9fff'):
                            original_length += 1
                            index_text+=1
                            continue
                if (('\u4e00' <= key <= '\u9fff')):  # 对于中文 寻找同音的替换
                    pinyin = pypinyin.lazy_pinyin(key)[0]
                    noYet = True
                    now_index = index_text
                    for i in pinyin:
                        flag_find_pinyin = i in now_map
                        if (flag_find_pinyin == True):
                            if (now_map.get("isStart") == 1) & (start_index == -1):  # 找到敏感词头
                                if (scan_mode == -1 and ('\u4e00' <= key <= '\u9fff')):
                                    scan_mode = 1
                                original_length = 1
                                start_index = now_index
                            now_map = now_map.get(i)
                        else:
                            noYet = False
                            break
                    if (noYet == True):
                        original_length += 1
                        if now_map.get("isEnd") == 1:  # 结束识别
                            original_length -= 1
                            if str(lines) + str(start_index) not in self.already_exist.keys():
                                ans_location.append(
                                    (start_index, original_length, self.transfomer_hanzi[now_map.get("word")]))
                            self.already_exist[str(lines) + str(start_index)] = 1
                            now_map = self.sensitive_word_map  # 恢复now_map
                            original_length = -1
                            start_index = -1
                            scan_mode = -1
                            self.index += 1
                            index_text+=1
                            temp_now_map={}
                            continue
                        index_text+=1
                        continue
                now_map = self.sensitive_word_map
                start_index = -1
                original_length = -1
                index_text+=1
        return ans_location

    def output_doc(self, filename):
        with open(filename, 'a', encoding='utf-8') as file_object:
            file_object.write("tot : " + str(self.index) + '\n')
            for info in self.answer:
                file_object.write(info)

    def subsets(self, nums):  # 只有汉字进来，敏感字长度，返回排列组合后的所有可能(数字形式)
        # 从空集开始搜索，每次将nums的节点加入空集中
        result = []
        tmp = []
        startIndex = 1
        self.dfsHelper(nums, startIndex, tmp, result)

        return result

    def dfsHelper(self, nums, cur, tmp, result):
        # dfs出口
        tmp_copy = tmp.copy()  # 拷贝一份
        if (len(tmp) >= nums):
            result.append(tmp_copy)
            return

        for i in range(3):  # [0,2)的所有组合
            tmp.append(i)
            self.dfsHelper(nums, i + 1, tmp, result)
            tmp.pop()
        return


if __name__ == '__main__':
    t = time.time()

    ans = WordDetect(r"D:\qqdata\2644521362\FileRecv\words.txt")

    print(time.time() - t)
    exit()
