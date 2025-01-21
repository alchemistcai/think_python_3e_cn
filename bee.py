'''计算符合Spelling Bee规则的字谜和结果分值。显示分数最高的前5个字谜，以及分数最高字谜的所有pangram。'''

import math
from itertools import combinations

import pandas as pd
import numpy as np

def is_acc(word: str, available: str, required: str) -> bool:
    '''检查`word`是否由`available`中的字母组成，并包含`required`字母.

    `available`必须是7个不同的字母。

    `required`必须在`available`中。
    '''
    if len(word) < 4:
        return False
    if required not in word:
        return False
    return set(word)<=set(available)


def score_acc(word: str,available:str) -> int:
    '''计算字谜`available`的`word`的分值，假定`word`符合要求。'''
    return len(word)-3 + 7*int(set(word)==set(available))


with open('words.txt', 'r+') as file:
    words = [word.strip().lower() for word in file.readlines()]
    availables = list(combinations('abcdefghijklmnopqrstuvwxyz', 7))
    scores = []
    count = 0
    ava_comb = math.comb(26, 7)  # 共C(26,7)
    for ava in availables:
        count += 1
        if count % 20 == 0:
            print(count / ava_comb * 100)
        for required in ava:
            acceptable_words = (word for word in words
                                if is_acc(word, ava, required))
            scores.append(
                (sum(score_acc(word)
                     for word in acceptable_words), ''.join(ava), required))
        if count % 20 == 0:
            print(scores[-1])
    scores = sorted(scores, reverse=True)
    print('总分数前5的字谜为：')
    print(scores[:5])
    max_score, max_ava, max_req = scores[0]
    max_words = [
        word for word in words if is_acc(word, max_ava, max_req) if len(set(word))==7
    ]  # 出于内存和速度考虑，循环内使用生成器，此处仅显示pangram
    print(f'分数最多的字谜pangram共{len(max_words)}个,具体为：')
    print(max_words)
