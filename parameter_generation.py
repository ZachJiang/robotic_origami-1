#!/usr/bin/env python
import bfs_plan as bfs
import numpy as np
import math
import copy

def findCreaseFuncByPoints(point1,point2):
    if point1[0] == point2[0]:
        a = 0.0
        if (point1[1]+point2[1])==0:
            c = 0.0
            b = 1.0
            return a,b,c
        c = 1.0
        b = -c*2.0 / (point1[1]+point2[1])
        return a,b,c
    elif point1[1] == point2[1]:
        b = 0.0
        if (point1[0]+point2[0])==0:
            c = 0.0
            a = 1.0
            return a,b,c
        c = 1.0
        a = -c*2.0 / (point1[0]+point2[0])
        return a,b,c
    else:
        k = (point1[1]-point2[1])/(point1[0]-point2[0])
        k = -1.0/k
        x = (point1[0]+point2[0])/2.0
        y = (point1[1]+point2[1])/2.0
        if (-k*x+y)==0.0:
            c = 0.0
            b = 1.0
            a = -b*k
            return a,b,c
        else:
            c = 1.0
            b = -c / (-k*x+y)
            a = -b*k
            return a,b,c

def pointsDistance(point1,point2):
    dx = point1[0]-point2[0]
    dy = point1[1]-point2[1]
    dis = np.sqrt(pow(dx,2)+pow(dy,2))
    return dis

def findCreaseFuncByPolygons(polygon1,polygon2):
    for facet in polygon1.keys():
        poly1 = polygon1[facet]
        poly2 = polygon2[facet]
        crease_func = []
        if (np.array(poly1)==np.array(poly2)).all():
            continue
        else:
            # print "facet",facet
            # print "poly1",poly1
            # print "poly2",poly2
            for i in range(len(poly1)):
                if (np.array(poly1[i])==np.array(poly2[i])).all():
                    continue
                else:
                    # print "poly1[i]",poly1[i]
                    # print "poly2[i]",poly2[i]
                    a,b,c = findCreaseFuncByPoints(poly1[i],poly2[i])
                    crease_func.append(a)
                    crease_func.append(b)
                    crease_func.append(c)
                    return a,b,c

def findReverseFacets(polygon1,polygon2):
    reversed_facets = []
    for facet in polygon1.keys():
        poly1 = polygon1[facet]
        poly2 = polygon2[facet]

        if (np.array(poly1)==np.array(poly2)).all():
            continue
        else:
            # print "facet",facet
            # print "poly1",poly1
            # print "poly2",poly2
            reversed_facets.append(facet)
    return reversed_facets

def PointLineDistance(line_func,point):
    #line_func is in the form of a,b,c
    x=point[0]
    y=point[1]
    a=line_func[0]
    b=line_func[1]
    c=line_func[2]
    dis = abs(a*x+b*y+c)/np.sqrt(a*a+b*b)
    return dis

def findFurthestPointInfo(crease_func,polygon,facets):
    info_tmp = []
    info = []
    for facet in facets:
        poly = polygon[facet]
        for i in range(len(poly)):
            #poly[i] is a point
            dis = PointLineDistance(crease_func,poly[i])
            info_tmp.append([dis,poly[i],facet])
    # print "info_tmp",info_tmp,type(info_tmp)
    dis_tmp = np.array(info_tmp)[:,0]
    max_dis = max(dis_tmp)
    # dis_tmp = list(enumerate(dis_tmp))
    indexs = [i for i,x in enumerate(dis_tmp) if x==max_dis]
    # print "indexs",indexs
    for index in indexs:
        info.append([info_tmp[index][1],info_tmp[index][2]])
    return info

def findGraspPointsAndMethods(grasp_info):
    #return grasp points and methods
    grasp_dict = {}
    point_dict = {}
    for i in range(len(grasp_info)):
        point = grasp_info[i][0]
        p = str(point)
        point_dict.setdefault(p,point)
        grasp_dict.setdefault(p,0)
        grasp_dict[p] += 1

    grasp = []
    for p in grasp_dict.keys():
        if grasp_dict[p] > 1:
            grasp.append([point_dict[p],"scooping"])
        elif grasp_dict[p] == 1:
            grasp.append([point_dict[p],"flexflip"])

    return grasp

def findGraspMoveDis(grasp,crease_func):
    #return ideal crease_perp_l
    grasp_move = []
    for i in range(len(grasp)):
        grasp_point = grasp[i][0]
        dis = PointLineDistance(crease_func,grasp_point)
        dis = 2*dis
        grasp_move.append([grasp_point,grasp[i][1],dis])
    return grasp_move

def ifPointInLine(point,line_func):
    a=line_func[0]
    b=line_func[1]
    c=line_func[2]
    x=point[0]
    y=point[1]
    is_in = a*x+b*y+c
    if is_in == 0:
        return 1
    else:
        return 0

def findCreaseExPoints(crease_func,polygon,facets):
    crease_point = []
    cp_dict={}
    for facet in facets:
        poly = polygon[facet]
        for i in range(len(poly)):
            point = poly[i]
            if ifPointInLine(point,crease_func)==1:
                cp = str(point)
                cp_dict.setdefault(cp,point)
            else:
                continue
    for cp in cp_dict.keys():
        crease_point.append(cp_dict[cp])

    dis_points = [] #dis of two points, parent point, child point
    for i in range(len(crease_point)):
        point1 = crease_point[i]
        for j in range(i+1,len(crease_point)):
            point2 = crease_point[j]
            dis = pointsDistance(point1,point2)
            dis_points.append([dis,point1,point2])
    dis_tmp = np.array(dis_points)[:,0]
    dis_tmp = dis_tmp.tolist()
    index = dis_tmp.index(max(dis_tmp))
    point1 = dis_points[index][1]
    point2 = dis_points[index][2]
    return [point1,point2]

def lineToFunction(line):
    "input line[[x1,y1],[x2,y2]], return k,b (ax+by+c=0)"
    # a = y2-y1, b = x1-x2, c=x2*y1-x1*y2
    a = line[1][1] - line[0][1]
    b = line[0][0] - line[1][0]
    c = line[1][0]*line[0][1] - line[0][0]*line[1][1]
    return a,b,c

def reverseLineDirection(line):
    tmp = line[0]
    line[0] = line[1]
    line[1] = tmp
    return line

def ifReverseLineDirection(polygon,crease,facets):
    #determine if the direction of the crease needs to be reversed
    #if facets[0] at the left of the crease, no need to reverse
    # if at the right, reverse line's direction to ensure the root_facet is always at base
    a,b,c = lineToFunction(crease)
    poly = polygon[facets[0]]
    for i in range(len(poly)):
        product = a*poly[i][0]+b*poly[i][1]+c
        if product < 0:
            return crease
        elif product > 0:
            return reverseLineDirection(crease)

def creasePointstoAxis(crease,facets,polygon):
    #return crease_axis
    #reversed facets always on the left of crease axis
    crease = ifReverseLineDirection(polygon,crease,facets)
    dx = crease[1][0]-crease[0][0]
    dy = crease[1][1]-crease[0][1]
    crease_axis = [dx,dy,0]
    crease_axis = np.array(crease_axis)/np.linalg.norm(np.array(crease_axis))
    crease_axis = crease_axis.tolist()
    return crease_axis

def creaseLength(crease):
    point1 = crease[0]
    point2 = crease[1]
    length = pointsDistance(point1,point2)
    return length

def parameter_generation():
    path, stack_step, state_dict = bfs.findPath()
    manipulation_dict = {}
    # information = {}
    for i in range(len(path)-1):
        polygon1 = state_dict[path[i]]["polygen"]
        polygon2 = state_dict[path[i+1]]["polygen"]
        reversed_facets = findReverseFacets(polygon1,polygon2)
        # print "reversed facets",reversed_facets
        crease_func=findCreaseFuncByPolygons(polygon1,polygon2)
        # print "crease func",crease_func
        grasp_info = findFurthestPointInfo(crease_func,polygon1,reversed_facets)
        # print "grasp_info",grasp_info
        grasp = findGraspPointsAndMethods(grasp_info)
        # print "grasp",grasp
        grasp_move = findGraspMoveDis(grasp,crease_func)
        # print "grasp_move",grasp_move
        crease = findCreaseExPoints(crease_func,polygon1,reversed_facets)
        # print "crease",crease
        crease_axis = creasePointstoAxis(crease,reversed_facets,polygon1)
        # print "crease_axis",crease_axis
        crease_length = creaseLength(crease)
        # print "crease length",crease_length
        # grasp_information = findGraspInformation(grasp_move,crease_axis)
        # print "grasp information",grasp_information
        fold = state_dict[path[i+1]]["fold"]
        step_name = "step"+str(i)
        info_tmp={"grasp":grasp_move,"crease_axis":crease_axis,"crease_length":crease_length,"fold":fold}
        # information.setdefault(step_name,info_tmp)
        # whole_info = [grasp_move,crease_axis,crease_length]
        manipulation_dict.setdefault(step_name,info_tmp)
    return manipulation_dict

manipulation_dict = parameter_generation()
# print "manipulation_dict",manipulation_dict
# print "step1 grasp info",manipulation_dict["step1"]["grasp"]
# print "step1 crease info",manipulation_dict["step1"]["crease_axis"],manipulation_dict["step1"]["crease_length"]

def mani_info_temp(manipulation_dict):
    manipulation_dict_temp = copy.deepcopy(manipulation_dict)
    for step in manipulation_dict.keys():
        grasp_info = manipulation_dict[step]["grasp"]
        for i in range(len(grasp_info)):
            point = grasp_info[i][0]
            point = [float(point[0])/1000,float(point[1])/1000]
            manipulation_dict_temp[step]["grasp"][i][0] = point
            move_dis = grasp_info[i][2]
            move_dis = move_dis/1000
            manipulation_dict_temp[step]["grasp"][i][2] = move_dis
        cl = manipulation_dict[step]["crease_length"]
        cl = cl/1000
        manipulation_dict_temp[step]["crease_length"] = cl
    return manipulation_dict_temp

global manipulation_dict_temp
manipulation_dict_temp = mani_info_temp(manipulation_dict)
# print "manipulation dict tmp",manipulation_dict_temp


#################transformation in real world
def transCentertoTag(transCenterTag2Tag,rotCenterTag2Tag):
    #transformation from planning center to assigned tag
    #input[0]:array, input[1]:array, matrix
    pos = transCenterTag2Tag
    rot_center2centerTag = [[0,1,0],
                          [-1,0,0],
                          [0,0,1]]
    rot_mat = np.dot(rotCenterTag2Tag,rot_center2centerTag)
    # print "rot center to tag",rot_mat
    return pos,rot_mat

def pointTransformation(point,pos,rot_mat):
    # point = [float(point[0]),float(point[1]),float(0)]
    # pos = [float(pos[0]),float(pos[1]),float(pos[2])]
    pointt = [point[0],point[1],0.0]
    trans_point = np.dot(rot_mat,pointt)+pos
    return trans_point

def lineTransformation(line,pos,rot_mat):
    point1 = line[0]
    point2 = line[1]
    trans_point1 = pointTransformation(point1,pos,rot_mat)
    trans_point2 = pointTransformation(point2,pos,rot_mat)
    trans_line = [trans_point1,trans_point2]
    return trans_line

def axisTransformation(axis,rot):
    trans_axis = np.dot(rot,axis)
    return trans_axis

def calcAngleofAxises(axis1,axis2):
    #reference is axis2, return angle that axis2 rotate to axis1
    #clockwise:-, counterclockwise:+
    axis1 = axis1 / np.linalg.norm(np.array(axis1))
    axis2 = axis2 / np.linalg.norm(np.array(axis2))
    #dot product
    theta = np.rad2deg(np.arccos(np.dot(axis1,axis2)))
    #cross product
    # rho = np.rad2deg(np.arcsin(np.cross(axis1,axis2)))
    rho = np.cross(axis1,axis2)
    # print "rho",rho
    if rho[2]<0:
        return theta
    else:
        return -theta

def findGraspAngle(grasp_move,crease_axis,gripper_axis=[1.0,0.0,0.0]):
    grasp_angle=[]
    for i in range(len(grasp_move)):
        method = grasp_move[i][1]
        theta = calcAngleofAxises(crease_axis,gripper_axis)
        if method == "flexflip":
            angle = theta + 90
        elif method == "scooping":
            angle = theta - 90
        grasp_angle.append(angle)
    return grasp_angle

def rotatePoint(point,rotation_axis=[1.0,0.0,0.0]):
    #needs to be improved to be applicable to all rotation axis
    new_point = [-point[0],point[1],point[2]]
    return new_point

def get_parameters(trans,rot,step):
    ##########transform parameters
    # manipulation_dict = mani_info_temp()
    # print "manipulation_dict",manipulation_dict
    grasp_move = manipulation_dict_temp[step]["grasp"]
    crease_axis = manipulation_dict_temp[step]["crease_axis"]
    crease_length = manipulation_dict_temp[step]["crease_length"]
    index = 999
    for i in range(len(grasp_move)):
        method = grasp_move[i][1]
        if method == "scooping":
            index=i
            break
    if index == 999:
        index = 0
    grasp_point = pointTransformation(grasp_move[index][0],trans,rot)
    # print "grasp point",grasp_point
    crease_axis = axisTransformation(crease_axis,rot)
    # print "crease axis",crease_axis
    grasp_angle = findGraspAngle(grasp_move,crease_axis)
    print "grasp angle",grasp_angle
    angle = grasp_angle[index]
    print "angle",angle

    if manipulation_dict_temp[step]["fold"] == "valley":
        # print "no need to turn over"
        exec_info = []
        exec_info.append([crease_axis,grasp_move[index][2],grasp_move[index][1],angle,crease_length,grasp_point])
        return exec_info

    elif manipulation_dict_temp[step]["fold"] == "mountain":
        # print "need to turn over!"
        # 3 layer action and info
        exec_info=[]
        #1st layer: scoop and turn
        exec_info.append([crease_axis,grasp_move[index][2],grasp_move[index][1],angle,crease_length,grasp_point])
        #2nd layer: valley fold
        crease_axis = -1*crease_axis
        if angle>0:
            angle=angle-180
        elif angle<=0:
            angle=angle+180
        grasp_point=rotatePoint(grasp_point)
        exec_info.append([crease_axis,grasp_move[index][2],grasp_move[index][1],angle,crease_length,grasp_point])
        #3rd layer: scoop and turn over
        grasp_point = [0]
        exec_info.append([crease_axis,grasp_move[index][2],grasp_move[index][1],angle,crease_length,grasp_point])
        return exec_info
