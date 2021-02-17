#!/usr/bin/env python
#some helper funtions
from shapely.ops import cascaded_union
import geopandas as gpd
from shapely.geometry import *

def determineWeight(state1,state2):
    #an edge connect state1 and state2
    #return the weight of this edge
    # 8 kinds of transitions
    #weight is the distance, the lower the better
    if len(state2['stack']) - len(state1['stack']) > 1:
        method = 'scooping'
    else:
        method = 'flexflip'
    #1: flexflip, valley, non-reflect
    if method == 'flexflip' and state2['fold'] == 'valley' and state2['reflect'] == 0:
        weight = 1
    #2: flexflip, valley, reflect
    if method == 'flexflip' and state2['fold'] == 'valley' and state2['reflect'] == 1:
        weight = 5
    #3: flexflip, mountain, non-reflect
    if method == 'flexflip' and state2['fold'] == 'mountain' and state2['reflect'] == 0:
        weight = 3
    #4: flexflip, mountain, reflect
    if method == 'flexflip' and state2['fold'] == 'mountain' and state2['reflect'] == 1:
        weight = 7
    #5: scooping, valley, non-reflect
    if method == 'scooping' and state2['fold'] == 'valley' and state2['reflect'] == 0:
        weight = 2
    #6: scooping, valley, reflect
    if method == 'scooping' and state2['fold'] == 'valley' and state2['reflect'] == 1:
        weight = 6
    #7: scooping, mountain, non-reflect
    if method == 'scooping' and state2['fold'] == 'mountain' and state2['reflect'] == 0:
        weight = 4
    #8: scooping, mountain, reflect
    if method == 'scooping' and state2['fold'] == 'mountain' and state2['reflect'] == 1:
        weight = 8
    #if overlap 1
    if state2['overlap'] == 1:
        weight = weight + 10
    #if overlap2
    if state2['overlap'] == 2:
        weight = weight + 20
    return weight

def ifOverlap(base,flap,polygon):
    #determine if the area of the base < the area of the flap
    #if yes, this fold is hard to execute, and the weight will increase
    #return 0 if flap < base
    #return 1 if flap = base
    #return 2 if flap > base
    base_area = 0.0
    flap_area = 0.0
    for i in range(len(base)):
        base_area_tmp = 0.0
        for j in range(len(base[i])):
            facet = base[i][j]
            line = LineString(polygon[facet])
            poly = Polygon(line)
            base_area_tmp += poly.area
        if base_area_tmp >= base_area:
            base_area = base_area_tmp
    for i in range(len(flap)):
        flap_area_tmp = 0.0
        for j in range(len(flap[i])):
            facet = flap[i][j]
            line = LineString(polygon[facet])
            poly = Polygon(line)
            flap_area_tmp += poly.area
        if flap_area_tmp >= flap_area:
            flap_area = flap_area_tmp
    if flap_area < base_area:
        return 0
    elif flap_area == base_area:
        return 1
    elif flap_area > base_area:
        return 2
