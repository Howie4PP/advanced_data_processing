#!/usr/bin/env python
# -*- coding: utf-8 -*-

import csv
import codecs
import pprint
import re
import xml.etree.cElementTree as ET

import cerberus

import schema
import check_node as checkNode
import check_street_name as checkStreetName

OSM_PATH = "sample.osm"

NODES_PATH = "nodes.csv"
NODE_TAGS_PATH = "nodes_tags.csv"
WAYS_PATH = "ways.csv"
WAY_NODES_PATH = "ways_nodes.csv"
WAY_TAGS_PATH = "ways_tags.csv"

LOWER_COLON = re.compile(r'^([a-z]|_)+:([a-z]|_)+')
PROBLEMCHARS = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

SCHEMA = schema.schema

# Make sure the fields order in the csvs matches the column order in the sql table schema
NODE_FIELDS = ['id', 'lat', 'lon', 'user', 'uid', 'version', 'changeset', 'timestamp']
TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_FIELDS = ['id', 'user', 'uid', 'version', 'changeset', 'timestamp']
WAY_NODES_FIELDS = ['id', 'node_id', 'position']


def shape_element(element, node_attr_fields=NODE_FIELDS, way_attr_fields=WAY_FIELDS,
                  problem_chars=PROBLEMCHARS, default_tag_type='regular'):
    """Clean and shape node or way XML element to Python dict"""

    node_attribs = {}
    way_attribs = {}
    way_nodes = []
    tags = []  # Handle secondary tags the same way for both node and way elements
    position = 0
    if element.tag == 'node':
        # 得到node字典
        for attr in node_attr_fields:
            if attr in element.attrib:
                node_attribs[attr] = element.attrib[attr]

        for key, value in node_attribs.items():

            try:
                if key == 'lat':
                    lat_num = float(value)
                    lat_value = checkNode.check_lat(lat_num)
                    if lat_value is None:
                        node_attribs.clear()
                if key == 'lon':
                    lon_num = float(value)
                    lon_value = checkNode.check_lon(lon_num)
                    if lon_value is None:
                        node_attribs.clear()

            except ValueError:
                pass

        # 得到node_tags 列表
        for key in element.iter('tag'):
            tag_not_dict = {}

            street_name = checkStreetName.audit(key)

            # 如果街道名不对，将不会添加
            if street_name is None:
                continue

            if LOWER_COLON.search(key.attrib['k']):
                    values = key.attrib['k'].split(":", 1)
                    tag_not_dict[TAGS_FIELDS[0]] = element.attrib['id']
                    tag_not_dict[TAGS_FIELDS[1]] = values[-1]
                    tag_not_dict[TAGS_FIELDS[2]] = key.attrib['v']
                    tag_not_dict[TAGS_FIELDS[3]] = values[0]

            else:
                    tag_not_dict[TAGS_FIELDS[0]] = element.attrib['id']
                    tag_not_dict[TAGS_FIELDS[1]] = key.attrib['k']
                    tag_not_dict[TAGS_FIELDS[2]] = key.attrib['v']
                    tag_not_dict[TAGS_FIELDS[3]] = default_tag_type

            tags.append(tag_not_dict)


    # 当tag等于way
    if element.tag == 'way':
        # 这个列表储存着街道名合理的wayID
        way_id = []

        # 得到way_tags 列表
        for key in element.iter('tag'):
            tag_way_dict = {}

            street_name = checkStreetName.audit(key)

            # 如果街道名不对，将不会添加
            if street_name is None:
                continue

            if PROBLEMCHARS.search(key.attrib['k']):
                continue
            else:
                if LOWER_COLON.search(key.attrib['k']):
                    values = key.attrib['k'].split(":", 1)
                    tag_way_dict[TAGS_FIELDS[0]] = element.attrib['id']
                    tag_way_dict[TAGS_FIELDS[1]] = values[-1]
                    tag_way_dict[TAGS_FIELDS[2]] = key.attrib['v']
                    tag_way_dict[TAGS_FIELDS[3]] = values[0]
                    way_id.append(element.attrib['id'])

                else:
                    tag_way_dict[TAGS_FIELDS[0]] = element.attrib['id']
                    tag_way_dict[TAGS_FIELDS[1]] = key.attrib['k']
                    tag_way_dict[TAGS_FIELDS[2]] = key.attrib['v']
                    tag_way_dict[TAGS_FIELDS[3]] = default_tag_type
                    way_id.append(element.attrib['id'])

            tags.append(tag_way_dict)

        # 得到way_nd字典
        for key in element.iter('nd'):
            nd_dict = {}
            if element.attrib['id'] in way_id:
                nd_dict['id'] = element.attrib['id']
                nd_dict['node_id'] = key.attrib['ref']
                nd_dict['position'] = position
                position += 1

                way_nodes.append(nd_dict)

        # 得到way字段的字典,由于这里没有经纬度可以进行辅助判断，所以要根据way的街道名进行添加
        for attr in way_attr_fields:
            if attr in element.attrib:
                # 加入字典前，先判断是否id是否储存在街道名合理的列表里
                if element.attrib['id'] in way_id:
                    way_attribs[attr] = element.attrib[attr]

    if element.tag == 'node' and len(node_attribs) == 8:
        return {'node': node_attribs, 'node_tags': tags}

    elif element.tag == 'way' and len(way_attribs) == 6:

        return {'way': way_attribs, 'way_nodes': way_nodes, 'way_tags': tags}




def get_element(osm_file, tags=('node', 'way', 'relation')):
    """Yield element if it is the right type of tag"""

    context = ET.iterparse(osm_file, events=('start', 'end'))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()


def validate_element(element, validator, schema=SCHEMA):
    """Raise ValidationError if element does not match schema"""
    if validator.validate(element, schema) is not True:
        field, errors = next(validator.errors.iteritems())
        message_string = "\nElement of type '{0}' has the following errors:\n{1}"
        error_string = pprint.pformat(errors)

        raise Exception(message_string.format(field, error_string))


# 查询节点是否有子元素
def no_sub_tag(element):
    if len(element.getchildren()) == 0:
        return True


class UnicodeDictWriter(csv.DictWriter, object):
    """Extend csv.DictWriter to handle Unicode input"""

    def writerow(self, row):
        super(UnicodeDictWriter, self).writerow({
            k: (v.encode('utf-8') if isinstance(v, unicode) else v) for k, v in row.iteritems()
        })

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


def process_map(file_in, validate):
    """Iteratively process each XML element and write to csv(s)"""

    with codecs.open(NODES_PATH, 'w') as nodes_file, \
            codecs.open(NODE_TAGS_PATH, 'w') as nodes_tags_file, \
            codecs.open(WAYS_PATH, 'w') as ways_file, \
            codecs.open(WAY_NODES_PATH, 'w') as way_nodes_file, \
            codecs.open(WAY_TAGS_PATH, 'w') as way_tags_file:

        nodes_writer = UnicodeDictWriter(nodes_file, NODE_FIELDS)
        node_tags_writer = UnicodeDictWriter(nodes_tags_file, TAGS_FIELDS)
        ways_writer = UnicodeDictWriter(ways_file, WAY_FIELDS)
        way_nodes_writer = UnicodeDictWriter(way_nodes_file, WAY_NODES_FIELDS)
        way_tags_writer = UnicodeDictWriter(way_tags_file, TAGS_FIELDS)

        nodes_writer.writeheader()
        node_tags_writer.writeheader()
        ways_writer.writeheader()
        way_nodes_writer.writeheader()
        way_tags_writer.writeheader()

        validator = cerberus.Validator()

        for element in get_element(file_in, tags=('node', 'way')):
            el = shape_element(element)
            if el:
                if validate is True:
                    validate_element(el, validator)

                if element.tag == 'node':
                    nodes_writer.writerow(el['node'])
                    node_tags_writer.writerows(el['node_tags'])
                elif element.tag == 'way':
                    ways_writer.writerow(el['way'])
                    way_nodes_writer.writerows(el['way_nodes'])
                    way_tags_writer.writerows(el['way_tags'])

process_map(OSM_PATH, validate=True)

# def mmmm():
#     for element in get_element(OSM_PATH, tags=('node', 'way')):
#         shape_element(element)
#
# mmmm()