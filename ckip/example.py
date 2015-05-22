# -*- coding: utf-8 -*-

#################################################
# example.py
# ckip.py
#
# Copyright (c) 2012-2014, Chi-En Wu
# Distributed under The BSD 3-Clause License
#################################################

from __future__ import unicode_literals, print_function

from ckip import CKIPSegmenter, CKIPParser


def traverse(root):
    """Helper function to traverse all leaf nodes of the given tree root."""
    if 'child' in root:
        for child in root['child']:
            for leaf in traverse(child):
                yield leaf
    else:
        yield root


# Usage example of the CKIPSegmenter class
segmenter = CKIPSegmenter('gcsn', 'rb303147258')
# result = segmenter.process('這是一隻可愛的小花貓')
result = segmenter.process('一、在地子弟商管博士林世宗主張「焚化爐輪燒或停爐」、「受污染地區垃圾袋補助」！為您監督市政、看緊荷包，打造士林、北投幸福家園！')
if result['status_code'] != '0':
    print('Process Failure: ' + result['status'])

for sentence in result['result']:
    for term in sentence:
        print(term['term'].encode('utf-8'), term['pos'])
print("")


# Usage example of the CKIPParser class
parser = CKIPParser('gcsn', 'rb303147258')
result = parser.process('這是一隻可愛的小花貓')
if result['status_code'] != '0':
    print('Process Failure: ' + result['status'])

for sentence in result['result']:
    for term in traverse(sentence['tree']):
        print(term['term'].encode('utf-8'), term['pos'])
