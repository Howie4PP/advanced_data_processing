#!/usr/bin/env python
# -*- coding: utf-8 -*-

import xml.etree.cElementTree as ET
from collections import defaultdict
import re
import pprint

expected = ["Street", "Avenue", "Boulevard", "Drive", "Court", "Place", "Square", "Lane", "Road",
            "Trail", "Parkway", "Commons"]

# UPDATE THIS VARIABLE
mapping = {"Rd": "Road",
           "Pl": "Place"}

invalid_name = ["Makmur",
                "Mutiara",
                "Ledang",
                "Marzuki",
                "Jl.Ir.Sutami",
                "Maju",
                "Kiri",
                "Kanan",
                "Intan",
                "Hikmat",
                "Belian",
                "Balai",
                "Jaya"]


def is_street_name(elem):
    return (elem.attrib['k'] == "addr:street")


def audit(elem):
    if is_street_name(elem):
        # audit_street_type(street_types, elem.attrib['v'])
        street_name = elem.attrib['v']

        # 排除'Jalan'开头的地名
        if street_name.startswith('Jalan'):
            return None

        # 由于新加坡也有以'Lorong' 开头的街道名称，所以这里用去判定一条街名称的结尾，是否有在非法的街道名称中
        for name in invalid_name:

            if name in street_name:
                return None

        # 最后是替换街道名的缩写
        return update_name(street_name)
    else:
        return elem

def update_name(name):
    change_name = mapping.keys()
    for word in change_name:
        if word in name:
            name = name.replace(word, mapping[word])

    return name
