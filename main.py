# -*- coding:utf-8 -*-
import logging
import sys
from zhconv import convert
import time
import pypinyin
from pychai import Schema


class WordDetect:
    def __init__(self, word_path, org_txt, ans_txt):
        self.index = 0
        self.answer = []
        self.transfomer_hanzi = {}
        original_sensitive_word = []
        pinyin_sentitive_word = []
        self.already_exist = {}
        self.first_zimu = {}
        self.need_rescan = {}
        self.need_pass = {}
        self.need_another_part = {}
        wubi98 = Schema('wubi98')
        wubi98.run()
        # --读入敏感词汇 获得pinyin
        with open(word_path, "r", encoding='utf-8') as file:
            original_sensitive_word = file.readlines()  # 读入文本

        original_sensitive_word = sorted([i.split('\n')[0] for i in original_sensitive_word])  # 按照换行符区分不同敏感词

        for string in original_sensitive_word:    # 增加汉字组合 去除某些不需要的组合
            pinyin_sentitive_word.append(string.lower())
            temp_word = ""
            if '\u4e00' <= string[0] <= '\u9fff':
                for char in string:
                    if char in wubi98.tree:
                        tree = wubi98.tree[char]
                        first = tree.first
                        second = tree.second
                        while first.structure == 'h':
                            if first.first is None:
                                break
                            first = first.first
                        while second.structure == 'h':
                            if second.second is None:
                                break
                            second = second.second
                        temp_word += first.name[0]
                        temp_word += second.name
                        self.need_pass[first.name[0]] = 1  #对于偏旁来说 拼音的组合不被需要
                        self.need_pass[second.name] = 1
                        self.need_another_part[first.name[0]] = second.name  # 对于偏旁来说 汉字的组合需要增加另一半
                    else:
                        temp_word += char
                pinyin_sentitive_word.append(temp_word)
            self.transfomer_hanzi[string.lower()] = string
            self.transfomer_hanzi[temp_word] = string
        pinyin_sentitive_word = list(set(pinyin_sentitive_word))  # 去重
        # 开始做拼音+本体的中文

        # ans_dataset中 0为需要用拼音的地方 1为用中文的地方 2为拆字  开始组词

        for temp_word in pinyin_sentitive_word.copy():  # 注意用copy 不然越打越多

            if '\u4e00' <= temp_word[0] <= '\u9fff':  # 识别为汉字

                pinyin = pypinyin.lazy_pinyin(temp_word)  # 拼音数组
                temp_word_respective = []  # 汉字数组 临时每一个单词
                for i in range(len(temp_word)):
                    temp_word_respective.append(temp_word[i])
                ans_dataset = self.subsets(len(temp_word))  # ans_dataset是组合列表
                need_pass = False
                for i in ans_dataset:

                    index = 0  # 子列表中第几个数
                    result_word = ""  # 最终组合结果
                    for j in range(len(i)):
                        if i[j] == 1:
                            result_word += temp_word_respective[index]
                            if temp_word_respective[index] in self.need_another_part:
                                result_word += self.need_another_part[temp_word_respective[index]]
                        if i[j] == 0:
                            if temp_word_respective[index] in self.need_pass:
                                need_pass = True
                            result_word += pinyin[index]
                        if i[j] == 2:
                            if temp_word_respective[index] in self.need_pass:
                                need_pass = True
                            result_word += pinyin[index][0]
                            self.first_zimu[pinyin[index][0]] = 1
                        index += 1

                    if not need_pass:  # 不需要跳过
                        pinyin_sentitive_word.append(result_word)
                    if result_word not in self.transfomer_hanzi:
                        self.transfomer_hanzi[result_word] = temp_word
            else:
                self.transfomer_hanzi[temp_word] = temp_word

        pinyin_sentitive_word = list(set(pinyin_sentitive_word))  # 去重

        self.sensitive_word_map = self.init_sensitive_word_map(pinyin_sentitive_word)  # 构造trie树

        self.get_answear_by_line(org_txt)  # 得到答案数组

        self.output_doc(ans_txt)  # 输出到文件


    def init_sensitive_word_map(self, sensitive_word_list):  # 造树过程，sensitive_word_list包含各种组合的敏感词
        sensitive_word_map = {}
        for word in sensitive_word_list:
            now_map = sensitive_word_map

            # 遍历该敏感词的每一个特定字符
            for i in range(len(word)):
                keychar = word[i]
                word_map = now_map.get(keychar)
                if word_map:
                    now_map = word_map
                    if keychar in self.first_zimu:
                        now_map["canBeMore"] = 1
                else:
                    new_next_map = {"isEnd": 0}
                    now_map[keychar] = new_next_map
                    now_map = new_next_map
                    if keychar in self.first_zimu:
                        now_map["canBeMore"] = 1
                # 到最后一个词
                if i == len(word) - 1:
                    now_map["isEnd"] = 1
                    now_map["word"] = word
                if i == 0:
                    now_map["isStart"] = 1
        return sensitive_word_map

    def get_sensitive_word_list(self, txt, lines):  # 传入（测试文本，没用，没用）返回起始位置、长度、敏感词 三元组
        now_map = self.sensitive_word_map
        start_index = -1
        original_length = -1
        scan_mode = -1  # 1检测中文
        ans_location = []
        index_text = 0
        temp_now_map = {}
        ingore_index = -1
        while index_text < len(txt):
            key = txt[index_text]
            if key.isalpha():
                key = key.lower()  # 一律改小写
            if '\u4e00' <= key <= '\u9fff':
                key = convert(key, 'zh-hans')  # 一律转简体

            if not key.isalpha() and not ('\u4e00' <= key <= '\u9fff'):  # 去除掉 符号 空格等
                original_length += 1
                index_text += 1
                continue
            flag_find = key in now_map
            if flag_find:
                now_map = now_map.get(key)
                if now_map.get("isEnd") == 1:  # 结束识别
                    if not temp_now_map and now_map.get("canBeMore"):

                        if index_text == len(txt) - 2:
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
                            temp_now_map = {}
                            continue
                        temp_now_map = now_map  # 保存当前状态
                        ingore_index += 1
                        index_text += 1
                        original_length += 1
                        continue
                    else:
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
                        temp_now_map = {}
                        continue
                if (now_map.get("isStart") == 1) & (start_index == -1):  # 找到敏感词头
                    if scan_mode == -1 and ('\u4e00' <= key <= '\u9fff'):
                        scan_mode = 1
                    original_length = 1
                    start_index = index_text
                original_length += 1
                index_text += 1
            else:
                if temp_now_map:
                    if str(lines) + str(start_index) not in self.already_exist.keys():
                        ans_location.append(
                            (start_index, original_length - 1, self.transfomer_hanzi[temp_now_map.get("word")]))
                    self.already_exist[str(lines) + str(start_index)] = 1
                    now_map = self.sensitive_word_map  # 恢复now_map
                    original_length = -1
                    start_index = -1
                    scan_mode = -1
                    self.index += 1
                    index_text -= ingore_index
                    temp_now_map = {}
                    continue
                if scan_mode == 1:
                    if key.isalpha() or key.isdecimal():  # 这里屏蔽不了中文 不知道为啥
                        if not ('\u4e00' <= key <= '\u9fff'):
                            original_length += 1
                            index_text += 1
                            continue
                if '\u4e00' <= key <= '\u9fff':  # 对于中文 寻找同音的替换
                    pinyin = pypinyin.lazy_pinyin(key)[0]
                    noYet = True
                    now_index = index_text
                    for i in pinyin:
                        flag_find_pinyin = i in now_map
                        if flag_find_pinyin:
                            if (now_map.get("isStart") == 1) & (start_index == -1):  # 找到敏感词头
                                if scan_mode == -1 and ('\u4e00' <= key <= '\u9fff'):
                                    scan_mode = 1
                                original_length = 1
                                start_index = now_index
                            now_map = now_map.get(i)
                        else:
                            noYet = False
                            break
                    if noYet:
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
                            index_text += 1
                            temp_now_map = {}
                            continue
                        index_text += 1
                        continue
                now_map = self.sensitive_word_map
                start_index = -1
                original_length = -1
                index_text += 1
        return ans_location

    def output_doc(self, filename):
        with open(filename, 'a', encoding='utf-8') as file_object:
            file_object.write("Total : " + str(self.index) + '\n')
            for info in self.answer:
                file_object.write(info)

    def subsets(self, nums):  # 只有汉字进来，敏感字长度，返回排列组合后的所有可能(数字形式)
        # 从空集开始搜索，每次将nums的节点加入空集中
        result = []
        tmp = []
        self.dfsHelper(nums, tmp, result)

        return result

    def dfsHelper(self, nums, tmp, result):
        # dfs出口
        tmp_copy = tmp.copy()  # 拷贝一份
        if len(tmp) >= nums:
            result.append(tmp_copy)
            return

        for i in range(3):  # [0,2)的所有组合
            tmp.append(i)
            self.dfsHelper(nums, tmp, result)
            tmp.pop()
        return
    def get_answear_by_line(self,org_txt):
        file = open(org_txt, encoding="utf-8")
        lines = 0
        while 1:
            line = file.readline()  # 带缓存的文件读取
            if not line:
                break
            lines += 1
            ans_in_lines = []  # 本行扫描结果
            ans_in_lines.extend(self.get_sensitive_word_list(line, lines))

            for i in ans_in_lines:
                self.answer.append("Line" + str(lines) + ":<" + i[2] + ">" + line[i[0]:i[0] + i[1]] + "\n")



if __name__ == '__main__':
    t = time.time()

    if len(sys.argv) > 1:
        words_txt = sys.argv[1]
        org_txt = sys.argv[2]
        ans_txt = sys.argv[3]
    else:
        words_txt = 'words.txt'
        org_txt = 'org.txt'
        ans_txt = 'ans.txt'
    try:
        ans = WordDetect(words_txt, org_txt, ans_txt)
    except IOError:
        logging.warning('你输入的文件路径有误!')
exit()
