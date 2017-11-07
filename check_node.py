#!/usr/bin/env python
# -*- coding: utf-8 -*-

boundary = {"left_top":[1.404433, 103.659460], "right_bottom":[1.240146, 104.068023]}


def check_lat(lat):

   if lat > boundary['right_bottom'][0] and lat < boundary['left_top'][0]:

       return str(lat)

   else:

       return None


def check_lon(lon):

    if lon < boundary['right_bottom'][1] and lon > boundary['left_top'][1]:
        return str(lon)
    else:

        return None