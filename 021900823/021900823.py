import xmnlp

min_match = 1
max_match = 2
class WordDetect:
    def __init__(self,word_path):
        original_sensitive_word = []
        pinyin_sentitive_word = []
        #--读入敏感词汇 获得pinyin
        with open(word_path,'r',encoding='utf-8') as file:
            original_sensitive_word=file.readlines()
        original_sensitive_word = sorted([i.split('\n')[0] for i in original_sensitive_word])


        for string in original_sensitive_word:
            temp=""
            listd = xmnlp.pinyin(string)
            for word in listd:
                temp +=word
                # 一律转换为小写
            pinyin_sentitive_word.append(temp.lower())
            pinyin_sentitive_word.append(string.lower())

        pinyin_sentitive_word = list(set(pinyin_sentitive_word))#去重
        print(original_sensitive_word)
        print(pinyin_sentitive_word)
        #self.sensitive_word_map = self.init_sensitive_word_map(pinyin_sentitive_word)#构造trie树
        #print(self.sensitive_word_map)
        temp="fuck,fuc_k,fu#ck,fu ck"
        #lst=self.get_sensitive_word_list(temp)
       # print(lst)
      # 构造字符树
    def init_sensitive_word_map(self, sensitive_word_list):
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
                # 到最后一个词
                if i == len(word) - 1:
                    now_map["isEnd"] = 1
                    now_map["word"]=word
                if i == 0:
                    now_map["isStart"]=1
        return sensitive_word_map

    def get_sensitive_word_list(self, txt):
        now_map = self.sensitive_word_map
        start_index=-1
        original_length = -1
        text_txt=""
        scan_mode= -1# 1检测中文
        print(txt)
        for i in range(len(txt)):
            key = txt[i]
            #print(" start exe :",key)
            if(not key.isalpha() and not ('\u4e00'<=key<='\u9fff')):#去除掉 符号 空格等
                original_length +=1
                continue
            flag_find = key in now_map
            if flag_find!=False:
                now_map=now_map.get(key)
                if now_map.get("isEnd")==1:#结束识别
                    print(start_index+1,now_map.get("word"),txt[start_index:start_index+original_length])#输出位置和原词
                    now_map = self.sensitive_word_map#恢复now_map
                    original_length =-1
                    text_txt += key
                    start_index=-1
                    scan_mode=-1
                    continue
                if (now_map.get("isStart")==1) & (start_index==-1):#找到敏感词头
                    if (scan_mode == -1 and ('\u4e00' <= key <= '\u9fff')):
                        scan_mode = 1
                    original_length = 1
                    start_index=i
                original_length+=1
            else:
                if(scan_mode == 1):
                    if(key.isalpha() or key.isdecimal()):
                        original_length+=1
                        continue
                now_map=self.sensitive_word_map
                start_index=-1
                original_length = -1
        return
if __name__ == '__main__':
    ans = WordDetect(r"C:\Users\Administrator\Documents\Tencent Files\2644521362\FileRecv\words.txt")