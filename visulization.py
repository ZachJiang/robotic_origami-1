#!/usr/bin/env python

import numpy as np
import cv2
import matplotlib.pyplot as plt
import copy
from compiler.ast import flatten
# stack1 = [['1','2','3','4','5','6','7','8']]
# #counterclock wise
# polygen1 = {"1":[[50,50],[0,100],[-50,50]],
#             "2":[[-33,0],[-50,50],[-100,0]],
#             "3":[[-33,0],[-50,50],[50,50],[33,0]],
#             "4":[[100,0],[50,50],[33,0]],
#             "5":[[-33,0],[-100,0],[-50,-50]],
#             "6":[[-33,0],[-50,-50],[50,-50],[33,0]],
#             "7":[[100,0],[50,-50],[33,0]],
#             "8":[[50,-50],[0,-100],[-50,-50]]
#             }
# facets1 = {"1":[[[-50,50],[50,50]]],
#            "2":[[[-100,0],[-33,0]],[[-33,0],[-50,50]]],
#            "3":[[[-50,50],[-33,0]],[[-33,0],[33,0]],[[33,0],[50,50]],[[50,50],[-50,50]]],
#            "4":[[[50,50],[33,0]],[[33,0],[100,0]]],
#            "5":[[[-50,-50],[-33,0]],[[-33,0],[-100,0]]],
#            "6":[[[-33,0],[-50,-50]],[[-50,-50],[50,-50]],[[50,-50],[33,0]],[[33,0],[-33,0]]],
#            "7":[[[100,0],[33,0]],[[33,0],[50,-50]]],
#            "8":[[[50,-50],[-50,-50]]]
#            }

#light blue:(230,245,253)
#light blue: (240,255,255) (255,240,245)
def init_canvas(width, height, color=(255,240,245)):
    canvas = np.ones((height, width, 3), dtype="uint8")
    canvas[:] = color
    return canvas

def rotationFromImg(weight,height,hat=0):
    #return rotation matrix
    if hat == 0:
        rot_mat = [[1,0,weight/2],
                   [0,-1,height/2],
                   [0,0,1]]
    else:
        rot_mat = [[0,1,weight/2],
                   [1,0,height/2],
                   [0,0,1]]
    return rot_mat

def PointsinImg(rot_mat,point):
    # return rotated Points
    point.append(1)
    new_point = np.dot(rot_mat,point)
    new_point = new_point[:2]
    return new_point

def PolygoninImag(rot_mat,polygon):
    rot_poly = copy.deepcopy(polygon)
    for facet in rot_poly.keys():
        poly = rot_poly[facet]
        for i in range(len(poly)):
            poly[i] = PointsinImg(rot_mat,poly[i])
    return rot_poly

def LineRotation(rot_mat,line):
    point1 = line[0]
    point2 = line[1]
    new_p1 = PointsinImg(rot_mat,point1)
    new_p2 = PointsinImg(rot_mat,point2)
    new_p1 = new_p1[:2]
    new_p2 = new_p2[:2]
    new_line = [new_p1,new_p2]
    return new_line

def CreaseinImag(rot_mat,crease):
    new_creases = copy.deepcopy(crease)
    for i in range(len(crease)):
        new_crease = LineRotation(rot_mat,crease[i])
        new_creases[i] = new_crease
    return new_creases

def EdgeRotation(rot_mat,edge_dict):
    rot_edge = copy.deepcopy(edge_dict)
    for edge in rot_edge.keys():
        lines = rot_edge[edge]
        for line in lines:
            line = LineRotation(rot_mat,line)
    return rot_edge

def decideOddEven(stack,fold,count):
    #return odd and even facets, used for filling different colors
    # if valley fold, even is dark
    light_facets = []
    dark_facets = []
    # print "count",count
    if fold == "valley":
        for i in range(len(stack)):
            k = i + count
            if k % 2 == 1:
                light_facets.append(stack[i])
            elif k % 2 == 0:
                dark_facets.append(stack[i])
    if fold == "mountain":
        for i in range(len(stack)):
            k = i + count
            if k % 2 == 0:
                dark_facets.append(stack[i])
            elif k % 2 == 1:
                light_facets.append(stack[i])
    if fold == 0:
        for i in range(len(stack)):
            if i % 2 == 0:
                dark_facets.append(stack[i])
            elif i % 2 == 1:
                light_facets.append(stack[i])

    light_facets = flatten(light_facets)
    dark_facets = flatten(dark_facets)
    return light_facets,dark_facets

def drawPolygon(polygon,stack1,canvas,rot_mat,fold,count):
    rot_poly = PolygoninImag(rot_mat,polygon)
    odd, even = decideOddEven(stack1,fold,count)
    # print "odd",odd
    # print "even",even
    for i in range(len(stack1)):
        for j in range(len(stack1[i])):
            facet = stack1[i][j]
            # print "poly",rot_poly[facet]
            # print "facet",facet
            cv2.polylines(canvas,[np.array(rot_poly[facet])],True,(139,58,98),thickness=8) #green:(61,139,110) gold:(76,129,139) purple:(139,102,139)
            if facet in odd:
                cv2.fillPoly(canvas,[np.array(rot_poly[facet])],(255,181,197)) #green:(193,255,193) gold:(139,236,255) purple:(255,187,255)
            elif facet in even:
                cv2.fillPoly(canvas,[np.array(rot_poly[facet])],(205,96,144)) #green:(90,205,162) gold:(112,190,205) purple:(205,150,205)

    # cv2.imshow('poly', canvas)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    return canvas

def drawline(img,pt1,pt2,color,thickness=3,style='dotted',gap=10):
    dist =((pt1[0]-pt2[0])**2+(pt1[1]-pt2[1])**2)**.5
    pts= []
    for i in np.arange(0,dist,gap):
        r=i/dist
        x=int((pt1[0]*(1-r)+pt2[0]*r)+.5)
        y=int((pt1[1]*(1-r)+pt2[1]*r)+.5)
        p = (x,y)
        pts.append(p)

    if style=='dotted':
        for p in pts:
            cv2.circle(img,p,thickness,color,-1)
    else:
        s=pts[0]
        e=pts[0]
        i=0
        for p in pts:
            s=e
            e=p
            if i % 2==1:
                cv2.line(img,s,e,color,thickness)
            i+=1

def drawPolygonwithCrease(polygon,stack1,canvas,rot_mat,fold,count,min_crease,feasible_crease,reflect=0):
    rot_min_creases = CreaseinImag(rot_mat,min_crease)
    rot_feasible_creases = CreaseinImag(rot_mat,feasible_crease)
    rot_poly = PolygoninImag(rot_mat,polygon)
    odd, even = decideOddEven(stack1,fold,count)
    # print "odd",odd
    # print "even",even
    for i in range(len(stack1)):
        for j in range(len(stack1[i])):
            facet = stack1[i][j]
            # print "poly",rot_poly[facet]
            # print "facet",facet
            cv2.polylines(canvas,[np.array(rot_poly[facet])],True,(61,139,110),thickness=8) #green:(61,139,110) pink:(139,58,98) gold:(76,129,139) purple:(139,102,139)
            if facet in odd:
                cv2.fillPoly(canvas,[np.array(rot_poly[facet])],(193,255,193)) #green:(193,255,193) pink:(255,181,197) gold:(139,236,255) purple:(255,187,255)
            elif facet in even:
                cv2.fillPoly(canvas,[np.array(rot_poly[facet])],(90,205,162)) #green:(90,205,162) pink:(205,96,144) gold:(112,190,205) purple:(205,150,205)
    for i in range(len(rot_min_creases)):
        p1 = rot_min_creases[i][0]
        p2 = rot_min_creases[i][1]
        drawline(canvas,p1,p2,(255,99,71))
    for i in range(len(rot_feasible_creases)):
        p1 = rot_feasible_creases[i][0]
        p2 = rot_feasible_creases[i][1]
        p1 = (p1[0],p1[1])
        p2 = (p2[0],p2[1])
        cv2.line(canvas,p1,p2,color=(255,99,71),thickness=7)
    # cv2.imshow('poly', canvas)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    return canvas

def drawOneFig(img):
    title = "node"
    plt.imshow(img)
    plt.title(title,fontsize=12)
    plt.xticks([])
    plt.yticks([])
    plt.show()
# drawPolygon(polygen1,stack1,rot_mat)
# img = drawPolygon(polygen1,stack1,canvas,rot_mat)

def drawMultiFigs(imgs,column,row,img_num):
    for i in range(column):
        for j in range(row):
            index = i*column + j+i
            # print "index",index
            if index >= img_num:
                break
            title = "step" + str(index+1)
            plt.subplot(column,row,index+1)
            plt.imshow(imgs[index])
            plt.title(title,fontsize=12) #,fontweight='bold'
            plt.xticks([])
            plt.yticks([])
