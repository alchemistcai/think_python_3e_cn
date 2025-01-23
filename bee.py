'''计算符合Spelling Bee规则的字谜和结果分值。显示分数最高的前5个字谜，以及分数最高字谜的前20高分pangram。'''

import math
from itertools import combinations
from pprint import pprint
from multiprocessing import Pool,cpu_count
from typing import Iterable

ava_comb = math.comb(26, 7)
'''26个字母中7个字母的组合数.'''

def is_acc(word: str, available: Iterable[str], required: str) -> bool:
    '''检查`word`是否由`available`中的字母组成，并包含`required`字母。

    `word`长度必须>=4。

    `available`必须是7个不同的字母的组合。

    `required`必须在`available`中。
    '''
    return required in word and set(word)<=set(available)


def score_acc(word: str) -> int:
    '''计算字谜`available`的`word`的分值，假定`word`符合要求。'''
    if len(word)==4:
        return 1
    # pangram必然集合长度为7
    return len(word) + 7*int(len(set(word))==7)


def worker(idx_and_available: tuple[int,Iterable[str]]) -> list:
    '''计算某个(索引,字谜)的所有必须字母对应的分数.
    
    shared_list用于并行计算保存列表.
    '''
    shared_list=[]
    idx,available=idx_and_available
    for required in available:
        acceptable_words = (word for word in words
                            if is_acc(word, available, required))
        shared_list.append(
            (sum(score_acc(word)
                    for word in acceptable_words), ''.join(available), required))
    if idx%400==0:
        print(f'{idx/ava_comb*100:.2f}%')
        print(shared_list[-1])
    return shared_list

with open('words.txt', 'r+') as file:
    words = (word.strip().lower() for word in file.readlines())
    words=[word for word in words if len(word)>3]
    availables=combinations('abcdefghijklmnopqrstuvwxyz', 7)
    with Pool(processes=int(cpu_count()*0.9)) as pool:
        scores=[score for scores_list in pool.map(worker,enumerate(availables)) for score in scores_list]
    scores.sort(reverse=True)
    print('总分数前5的字谜为：')
    pprint(scores[:5])
    max_score, max_ava, max_req = scores[0]
    max_words = [
        word for word in words if is_acc(word, max_ava, max_req) if len(set(word))==7
    ]  # 出于内存和速度考虑，循环内使用生成器，此处仅显示pangram
    max_words.sort(key=score_acc,reverse=True)
    print(f'分数最多的字谜pangram共{len(max_words)}个,前20高分的pangram为：')
    pprint(max_words[:20])
