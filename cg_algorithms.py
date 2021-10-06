#!/usr/bin/env python
# -*- coding:utf-8 -*-

# 本文件只允许依赖math库
import math


def draw_line(p_list, algorithm):
    """绘制线段

    :param p_list: (list of list of int: [[x0, y0], [x1, y1]]) 线段的起点和终点坐标
    :param algorithm: (string) 绘制使用的算法，包括'DDA'和'Bresenham'，此处的'Naive'仅作为示例，测试时不会出现
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 绘制结果的像素点坐标列表
    """
    x0, y0 = p_list[0]
    x1, y1 = p_list[1]
    result = []
    if algorithm == 'Naive':
        if x0 == x1:
            for y in range(y0, y1 + 1):
                result.append((x0, y))
        else:
            if x0 > x1:
                x0, y0, x1, y1 = x1, y1, x0, y0
            k = (y1 - y0) / (x1 - x0)
            for x in range(x0, x1 + 1):
                result.append((x, int(y0 + k * (x - x0))))

    elif algorithm == 'DDA':
        #pass
        if x0==x1:
            for y in range(min(y0,y1),max(y0,y1)+1):
                result.append([x0,y])
        else:
            k=(y1-y0)/(x1-x0)
            if abs(y1-y0)<abs(x1-x0):
                if x0 > x1:
                    x0, y0, x1, y1 = x1, y1, x0, y0
                y=y0
                for x in range(x0,x1+1):
                    result.append([x,round(y)])
                    y+=k
            else:
                if y0 > y1:
                    x0, y0, x1, y1 = x1, y1, x0, y0
                x=x0
                for y in range(y0,y1+1):
                    result.append([round(x),y])
                    x+=1/k

    elif algorithm == 'Bresenham':
        #pass
        dx,dy=abs(x1-x0),abs(y1-y0)
        flag=0
        if dx<dy:
            dx,dy=dy,dx
            x0,y0,x1,y1=y0,x0,y1,x1
            flag=1
        
        if x0>x1:
            x0,y0,x1,y1=x1,y1,x0,y0

        y=y0

        if y1>=y0:
            t=1
        else:
            t=-1
        p=2*dy-dx
        for x in range(x0,x1+1):
            if flag:
                result.append([y,x])
            else:
                result.append([x,y])
            if p>=0:
                p+=2*dy-2*dx
                y+=t
            else:
                p+=2*dy


    return result


def draw_polygon(p_list, algorithm):
    """绘制多边形

    :param p_list: (list of list of int: [[x0, y0], [x1, y1], [x2, y2], ...]) 多边形的顶点坐标列表
    :param algorithm: (string) 绘制使用的算法，包括'DDA'和'Bresenham'
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 绘制结果的像素点坐标列表
    """
    result = []
    for i in range(len(p_list)):
        line = draw_line([p_list[i - 1], p_list[i]], algorithm)
        result += line
    return result


def draw_ellipse(p_list):
    """绘制椭圆（采用中点圆生成算法）

    :param p_list: (list of list of int: [[x0, y0], [x1, y1]]) 椭圆的矩形包围框左上角和右下角顶点坐标
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 绘制结果的像素点坐标列表
    """
    #pass
    x0,y0=p_list[0]
    x1,y1=p_list[1]
    xc,yc=round((x0+x1)/2),round((y0+y1)/2)
    rx,ry=round(abs(x1-x0)/2),round(abs(y1-y0)/2)
    res=[]
    p=ry**2 - rx**2 *ry + rx**2 /4
    x,y=0,ry
    while x* ry**2 < y* rx**2:
        res.append([xc-x,yc-y])
        res.append([xc-x,yc+y])
        res.append([xc+x,yc-y])
        res.append([xc+x,yc+y])
        if p<=0:
            p+=2 * ry**2 * x + 3 * ry**2
        else:
            p+=2 * ry**2 * x - 2 * rx**2 * y + 2 * rx**2 + 3 * ry**2
            y-=1
        x+=1
    
    p = ry**2 * (x + 1/2)**2 + rx**2 * (y - 1)**2 - rx**2 * ry**2
    while y>=0:
        res.append([xc-x,yc-y])
        res.append([xc-x,yc+y])
        res.append([xc+x,yc-y])
        res.append([xc+x,yc+y])
        if p>=0:
            p+=-2 * rx**2 * y + 3 * rx**2
        else:
            p+=2 * ry**2 * x - 2 * rx**2 * y + 2 * ry**2 + 3 * rx**2
            x+=1
        y-=1

    return res


def mat(p_list,u,i):
    t=[]
    res=[0.0]*2
    t.append(-u**3 + 3*u**2 - 3*u + 1)
    t.append(3*u**3 - 6*u**2 + 4)
    t.append(-3*u**3 + 3*u**2 + 3*u + 1)
    t.append(u**3)

    for j in range(4):
        res[0]+=p_list[j+i][0]*t[j]
        res[1]+=p_list[j+i][1]*t[j]

    res[0]/=6
    res[1]/=6
    return res


def draw_curve(p_list, algorithm):
    """绘制曲线

    :param p_list: (list of list of int: [[x0, y0], [x1, y1], [x2, y2], ...]) 曲线的控制点坐标列表
    :param algorithm: (string) 绘制使用的算法，包括'Bezier'和'B-spline'（三次均匀B样条曲线，曲线不必经过首末控制点）
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 绘制结果的像素点坐标列表
    """
    #pass
    res=[]
    if algorithm =='Bezier':
        n=len(p_list)
        res.append(p_list[0])
        if n>1:
            loc=[[0]*2 for i in range(n-1)]
            for uu in range(1,1000*n+1):
                u=uu/(1000*n)
                for i in range(n-1):
                    loc[i][0]=p_list[i][0]*(1-u)+p_list[i+1][0]*u
                    loc[i][1]=p_list[i][1]*(1-u)+p_list[i+1][1]*u
                for i in range(n-2):
                    for j in range(n-i-2):
                        loc[j][0]=loc[j][0]*(1-u)+loc[j+1][0]*u
                        loc[j][1]=loc[j][1]*(1-u)+loc[j+1][1]*u
                res.append([round(loc[0][0]),round(loc[0][1])])

    elif algorithm == 'B-spline':
        n=len(p_list)-1
        k=3
        u=0.0
        while u<=1:
            for i in range(n-k+1):
                x,y=mat(p_list,u,i)
                res.append([round(x),round(y)])
            u+=0.001/(n+1)

    return res

def translate(p_list, dx, dy):
    """平移变换

    :param p_list: (list of list of int: [[x0, y0], [x1, y1], [x2, y2], ...]) 图元参数
    :param dx: (int) 水平方向平移量
    :param dy: (int) 垂直方向平移量
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 变换后的图元参数
    """
    #pass
    res=[]
    for v in p_list:
        res.append([v[0]+dx,v[1]+dy])
    return res


def rotate(p_list, x, y, r):
    """旋转变换（除椭圆外）

    :param p_list: (list of list of int: [[x0, y0], [x1, y1], [x2, y2], ...]) 图元参数
    :param x: (int) 旋转中心x坐标
    :param y: (int) 旋转中心y坐标
    :param r: (int) 顺时针旋转角度（°）
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 变换后的图元参数
    """
    #pass
    radian=float(r*math.pi/180)
    res=[]
    for p in p_list:
        dx,dy=p[0]-x,p[1]-y
        nx=round(x+dx*math.cos(radian)-dy*math.sin(radian))
        ny=round(y+dx*math.sin(radian)+dy*math.cos(radian))
        res.append([nx,ny])
    return res


def scale(p_list, x, y, s):
    """缩放变换

    :param p_list: (list of list of int: [[x0, y0], [x1, y1], [x2, y2], ...]) 图元参数
    :param x: (int) 缩放中心x坐标
    :param y: (int) 缩放中心y坐标
    :param s: (float) 缩放倍数
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 变换后的图元参数
    """
    #pass
    res=[]
    for v in p_list:
        nx=round(x+s*(v[0]-x))
        ny=round(y+s*(v[1]-y)) #half adjust
        res.append([nx,ny])
    return res


def getcode(x_min,y_min,x_max,y_max,x,y)->int:
    res=0
    if x<x_min:
        res+=1
    elif x>x_max:
        res+=2
    if y<y_min:
        res+=4
    elif y>y_max:
        res+=8
    return res

def clip(p_list, x_min, y_min, x_max, y_max, algorithm):
    """线段裁剪

    :param p_list: (list of list of int: [[x0, y0], [x1, y1]]) 线段的起点和终点坐标
    :param x_min: 裁剪窗口左上角x坐标
    :param y_min: 裁剪窗口左上角y坐标
    :param x_max: 裁剪窗口右下角x坐标
    :param y_max: 裁剪窗口右下角y坐标
    :param algorithm: (string) 使用的裁剪算法，包括'Cohen-Sutherland'和'Liang-Barsky'
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1]]) 裁剪后线段的起点和终点坐标
    """
    #pass
    x0,y0=p_list[0]
    x1,y1=p_list[1]
    if algorithm == 'Cohen-Sutherland':
        code0=getcode(x_min,y_min,x_max,y_max,x0,y0)
        code1=getcode(x_min,y_min,x_max,y_max,x1,y1)
        while True:
            if not code0 and not code1:
                return [[round(x0),round(y0)],[round(x1),round(y1)]]
            if code0&code1:
                return []
            if code0==0:
                x0,y0,x1,y1=x1,y1,x0,y0
                code0,code1=code1,code0
            if code0&1:
                y0+=(y1-y0)*(x_min-x0)/(x1-x0)
                x0=x_min
            elif code0&2:
                y0+=(y1-y0)*(x_max-x0)/(x1-x0)
                x0=x_max
            elif code0&4:
                x0+=(x1-x0)*(y_min-y0)/(y1-y0)
                y0=y_min
            elif code0&8:
                x0+=(x1-x0)*(y_max-y0)/(y1-y0)
                y0=y_max
            code0=getcode(x_min,y_min,x_max,y_max,x0,y0)
            code1=getcode(x_min,y_min,x_max,y_max,x1,y1)

    elif algorithm == 'Liang-Barsky':
        p=[x0-x1,x1-x0,y0-y1,y1-y0]
        q=[x0-x_min,x_max-x0,y0-y_min,y_max-y0]
        u1,u2=0,1

        for i in range(4):
            if p[i]==0 and q[i]<0:
                return []
            elif p[i]<0:
                u1=max(u1,q[i]/p[i])
            elif p[i]>0:
                u2=min(u2,q[i]/p[i])
            if u1>u2:
                return []
        res=[[round(x0+u1*(x1-x0)),round(y0+u1*(y1-y0))],
             [round(x0+u2*(x1-x0)),round(y0+u2*(y1-y0))]]
        return res

