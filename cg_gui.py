#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys
import cg_algorithms as alg
from typing import Optional
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    qApp,
    QGraphicsScene,
    QGraphicsView,
    QGraphicsItem,
    QListWidget,
    QHBoxLayout,
    QWidget,
    QStyleOptionGraphicsItem)
from PyQt5.QtGui import QPainter, QMouseEvent, QColor
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import math
import numpy as np
from PIL import Image


class MyCanvas(QGraphicsView):
    """
    画布窗体类，继承自QGraphicsView，采用QGraphicsView、QGraphicsScene、QGraphicsItem的绘图框架
    """
    def __init__(self, *args):
        super().__init__(*args)
        self.main_window = None
        self.list_widget = None
        self.item_dict = {}
        self.selected_id = ''

        self.status = ''
        #self.prestatus = ''
        self.temp_algorithm = ''
        self.temp_id = ''
        self.temp_item = None
        self.color = QColor(0,0,0)
        self.pre_pos = None
        self.pre_list = []
        self.center = None
        self.bound = None

    def start_draw_line(self, algorithm, item_id):
        self.status = 'line'
        self.temp_algorithm = algorithm
        self.temp_id = item_id

    def start_draw_polygon(self,algorithm,item_id):
        self.status = 'polygon'
        self.temp_algorithm = algorithm
        self.temp_id = item_id

    def start_draw_ellipse(self,item_id):
        self.status = 'ellipse'
        self.temp_id = item_id

    def start_draw_curve(self,algorithm,item_id):
        self.status = 'curve'
        self.temp_algorithm = algorithm
        self.temp_id = item_id

    def start_free_draw(self,item_id):
        self.status = 'pen'
        self.temp_id = item_id

    def finish_draw(self,flag=False):
        if self.temp_item is not None:
            self.temp_id = self.main_window.get_id(flag)
            self.temp_item = None
            self.center = None

    def start_translate(self):
        self.status = 'translate'

    def start_rotate(self):
        self.status = 'rotate'

    def start_scale(self):
        self.status = 'scale'

    def start_clip(self, algorithm):
        self.status = 'clip'
        self.temp_algorithm = algorithm

    def start_delete(self):
        if self.selected_id != '':
            number = self.list_widget.findItems(self.selected_id, Qt.MatchContains)
            row = self.list_widget.row(number[0])
            temp_id = self.selected_id
            temp_item = self.item_dict[temp_id]
            self.clear_selection()
            self.list_widget.clearSelection()
            self.scene().removeItem(temp_item)
            del self.item_dict[temp_id]
            self.list_widget.takeItem(row)
            self.updateScene([self.sceneRect()])
            self.main_window.changed = True

    def clear_selection(self):
        if self.selected_id != '':
            self.item_dict[self.selected_id].selected = False
            self.selected_id = ''
            self.temp_item = None

    def selection_changed(self, selected):
        self.main_window.check()
        self.main_window.statusBar().showMessage('图元选择： %s' % selected)
        if self.selected_id != '':
            self.item_dict[self.selected_id].selected = False
            self.item_dict[self.selected_id].update()
        self.selected_id = selected
        if selected != '':
            self.item_dict[selected].selected = True
            self.item_dict[selected].update()
        self.status = ''
        self.updateScene([self.sceneRect()])

    def mousePressEvent(self, event: QMouseEvent) -> None:
        pos = self.mapToScene(event.localPos().toPoint())
        x = int(pos.x())
        y = int(pos.y())

        if self.status == 'line':
            self.temp_item = MyItem(self.temp_id, self.status, [[x, y], [x, y]], self.temp_algorithm, self.color)
            self.scene().addItem(self.temp_item)
            self.main_window.changed=True
        elif self.status == 'ellipse':
            self.temp_item = MyItem(self.temp_id, self.status, [[x, y], [x, y]], color=self.color)
            self.scene().addItem(self.temp_item)
            self.main_window.changed=True
        elif self.status == 'polygon' or self.status == 'curve':
            if self.temp_item is None:
                if event.button() == Qt.LeftButton:
                    self.temp_item = MyItem(self.temp_id, self.status, [[x, y]], self.temp_algorithm, self.color)
                    self.scene().addItem(self.temp_item)
            else:
                if event.button() == Qt.RightButton:
                    self.item_dict[self.temp_id] = self.temp_item
                    self.list_widget.addItem(self.temp_id)
                    self.finish_draw()
                    #self.status = ''
                else:
                    self.temp_item.p_list.append([x, y])
            self.main_window.changed=True
        elif self.status == 'pen':
            self.temp_item = MyItem(self.temp_id, self.status, [[x, y]], color=self.color)
            self.scene().addItem(self.temp_item)
            self.main_window.changed=True
        elif self.status == 'translate':
            if self.selected_id != '':
                self.temp_item = self.item_dict[self.selected_id]
                self.pre_pos = pos
                self.pre_list = self.temp_item.p_list
                self.main_window.changed=True
                #if event.button() == Qt.RightButton:
                 #   self.clear_selection()
        elif self.status == 'rotate' or self.status == 'scale':
            if self.selected_id != '':
                self.temp_item = self.item_dict[self.selected_id]
                self.pre_pos = pos
                self.pre_list = self.temp_item.p_list
                x,y = 0,0
                for p in self.pre_list:
                    x += p[0]
                    y += p[1]
                x = int(x/len(self.pre_list))
                y = int(y/len(self.pre_list))
                self.center = [x,y]
                self.main_window.changed=True
                #if event.button() == Qt.RightButton:
                 #   self.clear_selection()
        elif self.status == 'clip':
            if self.selected_id != '':
                self.temp_item = self.item_dict[self.selected_id]
                if self.temp_item.item_type == 'line':
                    self.pre_pos = pos
                    self.pre_list = self.temp_item.p_list
                    self.main_window.changed=True

        self.updateScene([self.sceneRect()])
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        pos = self.mapToScene(event.localPos().toPoint())
        x = int(pos.x())
        y = int(pos.y())
        if self.status == 'line' or self.status == 'ellipse':
            self.temp_item.p_list[1] = [x, y]
        elif self.status == 'polygon' or self.status == 'curve':
            self.temp_item.p_list[len(self.temp_item.p_list)-1] = [x, y]
        elif self.status == 'pen':
            self.temp_item.p_list.append([x, y])
        elif self.status == 'translate':
            if self.selected_id != '':
                dx,dy=x-int(self.pre_pos.x()),y-int(self.pre_pos.y())
                self.temp_item.p_list = alg.translate(self.pre_list,dx,dy)
        elif self.status == 'rotate':
            if self.selected_id != '' and self.temp_item.item_type != 'ellipse':
                pre_x,pre_y=int(self.pre_pos.x()),int(self.pre_pos.y())
                #len1=math.sqrt((pre_x-self.center[0])**2 + (pre_y-self.center[1])**2)
                #len2=math.sqrt((x-self.center[0])**2 + (y-self.center[1])**2)
                r=(math.atan2(y-self.center[1],x-self.center[0])- \
                    math.atan2(pre_y-self.center[1],pre_x-self.center[0]))*180/math.pi
                self.temp_item.p_list = alg.rotate(self.pre_list,self.center[0],self.center[1],r)
        elif self.status == 'scale':
            if self.selected_id != '':
                pre_x,pre_y=int(self.pre_pos.x()),int(self.pre_pos.y())
                len1=math.sqrt((pre_x-self.center[0])**2 + (pre_y-self.center[1])**2)
                len2=math.sqrt((x-self.center[0])**2 + (y-self.center[1])**2)
                if len1!=0:
                    s=len2/len1
                    self.temp_item.p_list=alg.scale(self.pre_list,self.center[0],self.center[1],s)
        elif self.status == 'clip':
            if self.selected_id != '' and self.temp_item.item_type == 'line':
                pre_x,pre_y=int(self.pre_pos.x()),int(self.pre_pos.y())
                x_min,x_max = min(pre_x,x),max(pre_x,x)
                y_min,y_max = min(pre_y,y),max(pre_y,y)
                if self.bound is None:
                    self.bound = QGraphicsRectItem(x_min-1, y_min-1, x_max-x_min+2, y_max-y_min+2)
                    self.bound.setPen(Qt.magenta)
                    self.scene().addItem(self.bound)
                else:
                    self.bound.setRect(x_min-1, y_min-1, x_max-x_min+2, y_max-y_min+2)
        self.updateScene([self.sceneRect()])
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if self.status == 'line' or self.status == 'ellipse' or self.status == 'pen':
            self.item_dict[self.temp_id] = self.temp_item
            self.list_widget.addItem(self.temp_id)
            self.finish_draw()
        elif self.status == 'clip':
            pos = self.mapToScene(event.localPos().toPoint())
            x = int(pos.x())
            y = int(pos.y())
            if self.selected_id != '' and self.temp_item.item_type == 'line':
                pre_x,pre_y=int(self.pre_pos.x()),int(self.pre_pos.y())
                x_min,x_max = min(pre_x,x),max(pre_x,x)
                y_min,y_max = min(pre_y,y),max(pre_y,y)
                t_list = alg.clip(self.pre_list,x_min,y_min,x_max,y_max,self.temp_algorithm)
                if t_list != []:
                    self.temp_item.p_list = t_list
                else:
                    number = self.list_widget.findItems(self.selected_id, Qt.MatchContains)
                    row = self.list_widget.row(number[0])
                    temp_id = self.selected_id
                    temp_item=self.temp_item
                    self.clear_selection()
                    self.list_widget.clearSelection()
                    self.scene().removeItem(temp_item)
                    del self.item_dict[temp_id]
                    self.list_widget.takeItem(row)
                if self.bound is not None:
                    self.scene().removeItem(self.bound)
                    self.bound = None
                self.updateScene([self.sceneRect()])
        '''
        elif self.status == 'polygon' or self.status == 'curve':
            self.item_dict[self.temp_id] = self.temp_item
            if not self.list_widget.findItems(self.temp_id, Qt.MatchContains):
                self.list_widget.addItem(self.temp_id)
        '''

        super().mouseReleaseEvent(event)


class MyItem(QGraphicsItem):
    """
    自定义图元类，继承自QGraphicsItem
    """
    def __init__(self, item_id: str, item_type: str, p_list: list, algorithm: str = '', 
                 color=QColor(0,0,0),parent: QGraphicsItem = None):
        """

        :param item_id: 图元ID
        :param item_type: 图元类型，'line'、'polygon'、'ellipse'、'curve'等
        :param p_list: 图元参数
        :param algorithm: 绘制算法，'DDA'、'Bresenham'、'Bezier'、'B-spline'等
        :param parent:
        """
        super().__init__(parent)
        self.id = item_id           # 图元ID
        self.item_type = item_type  # 图元类型，'line'、'polygon'、'ellipse'、'curve'等
        self.p_list = p_list        # 图元参数
        self.algorithm = algorithm  # 绘制算法，'DDA'、'Bresenham'、'Bezier'、'B-spline'等
        self.selected = False
        self.color = color

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: Optional[QWidget] = ...) -> None:
        painter.setPen(self.color)
        if self.item_type == 'line':
            item_pixels = alg.draw_line(self.p_list, self.algorithm)
            for p in item_pixels:
                painter.drawPoint(*p)

        elif self.item_type == 'polygon':
            #pass
            item_pixels = alg.draw_polygon(self.p_list, self.algorithm)
            for p in item_pixels:
                painter.drawPoint(*p)

        elif self.item_type == 'ellipse':
            #pass
            item_pixels = alg.draw_ellipse(self.p_list)
            for p in item_pixels:
                painter.drawPoint(*p)

        elif self.item_type == 'curve':
            #pass
            item_pixels = alg.draw_curve(self.p_list, self.algorithm)
            for p in item_pixels:
                painter.drawPoint(*p)
            for p in self.p_list:
                painter.drawPoint(*p)

        elif self.item_type == 'pen':
            for p in self.p_list:
                painter.drawPoint(*p)

        if self.selected:
            painter.setPen(QColor(255, 0, 0))
            painter.drawRect(self.boundingRect())

    def boundingRect(self) -> QRectF:
        if self.item_type == 'line' or self.item_type == 'ellipse':
            x0, y0 = self.p_list[0]
            x1, y1 = self.p_list[1]
            x = min(x0, x1)
            y = min(y0, y1)
            w = max(x0, x1) - x
            h = max(y0, y1) - y
            return QRectF(x - 1, y - 1, w + 2, h + 2)
        elif self.item_type == 'polygon' or self.item_type == 'curve' or self.item_type == 'pen':
            #pass
            x_min,y_min=self.p_list[0]
            x_max,y_max=self.p_list[0]
            for p in self.p_list:
                x_min=min(x_min,p[0])
                x_max=max(x_max,p[0])
                y_min=min(y_min,p[1])
                y_max=max(y_max,p[1])
            w,h=x_max-x_min,y_max-y_min
            return QRectF(x_min - 1, y_min - 1, w + 2, h + 2)


class MainWindow(QMainWindow):
    """
    主窗口类
    """
    def __init__(self):
        super().__init__()
        self.item_cnt = 0

        # 使用QListWidget来记录已有的图元，并用于选择图元。注：这是图元选择的简单实现方法，更好的实现是在画布中直接用鼠标选择图元
        self.list_widget = QListWidget(self)
        self.list_widget.setMinimumWidth(200)

        # 使用QGraphicsView作为画布
        self.length = 1500
        self.height = 1000
        self.scene = QGraphicsScene(self)
        self.scene.setSceneRect(0, 0, self.length, self.height)
        self.canvas_widget = MyCanvas(self.scene, self)
        self.canvas_widget.setFixedSize(1500, 1000)
        self.canvas_widget.main_window = self
        self.canvas_widget.list_widget = self.list_widget
        self.changed = False

        # 设置菜单栏
        menubar = self.menuBar()
        file_menu = menubar.addMenu('文件')
        set_pen_act = file_menu.addAction('设置画笔')
        reset_canvas_act = file_menu.addAction('重置画布')
        save_canvas_act = file_menu.addAction('保存画布')
        exit_act = file_menu.addAction('退出')
        draw_menu = menubar.addMenu('绘制')
        line_menu = draw_menu.addMenu('线段')
        line_naive_act = line_menu.addAction('Naive')
        line_dda_act = line_menu.addAction('DDA')
        line_bresenham_act = line_menu.addAction('Bresenham')
        polygon_menu = draw_menu.addMenu('多边形')
        polygon_dda_act = polygon_menu.addAction('DDA')
        polygon_bresenham_act = polygon_menu.addAction('Bresenham')
        ellipse_act = draw_menu.addAction('椭圆')
        curve_menu = draw_menu.addMenu('曲线')
        curve_bezier_act = curve_menu.addAction('Bezier')
        curve_b_spline_act = curve_menu.addAction('B-spline')
        pen_act = draw_menu.addAction('画笔')
        edit_menu = menubar.addMenu('编辑')
        translate_act = edit_menu.addAction('平移')
        rotate_act = edit_menu.addAction('旋转')
        scale_act = edit_menu.addAction('缩放')
        clip_menu = edit_menu.addMenu('裁剪')
        clip_cohen_sutherland_act = clip_menu.addAction('Cohen-Sutherland')
        clip_liang_barsky_act = clip_menu.addAction('Liang-Barsky')
        delete_act = edit_menu.addAction('删除')

        # 连接信号和槽函数
        set_pen_act.triggered.connect(self.set_pen_action)
        exit_act.triggered.connect(self.myquit)

        save_canvas_act.triggered.connect(self.save_canvas_action) #canvas
        save_canvas_act.setShortcut('Ctrl+S')
        reset_canvas_act.triggered.connect(self.reset_canvas_action)
        reset_canvas_act.setShortcut('Ctrl+R')

        line_naive_act.triggered.connect(self.line_naive_action) #line
        line_dda_act.triggered.connect(self.line_DDA_action)
        line_bresenham_act.triggered.connect(self.line_bresenham_action)

        polygon_dda_act.triggered.connect(self.polygon_DDA_action) #polygon
        polygon_bresenham_act.triggered.connect(self.polygon_bresenham_action)

        ellipse_act.triggered.connect(self.ellipse_action) #ellipse

        curve_bezier_act.triggered.connect(self.curve_bezier_action) #curve
        curve_b_spline_act.triggered.connect(self.curve_b_spline_action)

        pen_act.triggered.connect(self.pen_action)

        translate_act.triggered.connect(self.translate_action) #translate
        rotate_act.triggered.connect(self.rotate_action) #rotate
        scale_act.triggered.connect(self.scale_action) #scale

        clip_cohen_sutherland_act.triggered.connect(self.clip_cohen_sutherland_action) #clip
        clip_liang_barsky_act.triggered.connect(self.clip_liang_barsky_action)

        delete_act.triggered.connect(self.delete_action)
        delete_act.setShortcut('Shift+Del')

        self.list_widget.currentTextChanged.connect(self.canvas_widget.selection_changed)

        # 设置主窗口的布局
        self.hbox_layout = QHBoxLayout()
        self.hbox_layout.addWidget(self.canvas_widget)
        self.hbox_layout.addWidget(self.list_widget, stretch=1)
        self.central_widget = QWidget()
        self.central_widget.setLayout(self.hbox_layout)
        self.setCentralWidget(self.central_widget)
        self.statusBar().showMessage('空闲')
        self.resize(1800, 1400)
        self.setWindowTitle('zjh\'s CG')

    def check(self):
        if self.canvas_widget.status == 'polygon' or self.canvas_widget.status == 'curve':
            if self.canvas_widget.temp_item is not None:
                self.canvas_widget.item_dict[self.canvas_widget.temp_id]=self.canvas_widget.temp_item
                self.canvas_widget.list_widget.addItem(self.canvas_widget.temp_id)
                self.canvas_widget.finish_draw()
            #else:
             #   self.canvas_widget.finish_draw(True)

    def set_pen_action(self):
        color=QColorDialog.getColor()
        if color.isValid():
            self.canvas_widget.color=color

    def myquit(self):
        self.check()
        if self.changed:
            reply = QMessageBox.question(self, 'Message',
                "Do you want to save your work?", QMessageBox.Yes | 
                QMessageBox.No | QMessageBox.Cancel, QMessageBox.Yes)
            if reply == QMessageBox.Yes:
                self.save_canvas_action()
                qApp.quit()
            elif reply == QMessageBox.No:
                qApp.quit()
        else:
            qApp.quit()

    def closeEvent(self,a: QCloseEvent):
        self.check()
        if self.changed:
            reply = QMessageBox.question(self, 'Message',
                "Do you want to save your work?", QMessageBox.Yes | 
                QMessageBox.No | QMessageBox.Cancel, QMessageBox.Yes)
            if reply == QMessageBox.Yes:
                self.save_canvas_action()
                a.accept()
            elif reply == QMessageBox.No:
                a.accept()
            else:
                a.ignore()
        else:
            a.accept()

    def save_canvas_action(self):
        self.check()
        path = QFileDialog.getSaveFileName(caption='保存画布', filter='BMP图像 (*.bmp)')
        if path!='':
            canvas = np.zeros([self.height, self.length, 3], np.uint8)
            canvas.fill(255)
            for item in self.canvas_widget.item_dict.values():
                if item.item_type == 'line':
                    pixels = alg.draw_line(item.p_list, item.algorithm)
                elif item.item_type == 'polygon':
                    pixels = alg.draw_polygon(item.p_list,item.algorithm)
                elif item.item_type == 'ellipse':
                    pixels = alg.draw_ellipse(item.p_list)
                elif item.item_type == 'curve':
                    pixels = alg.draw_curve(item.p_list,item.algorithm)
                elif item.item_type == 'pen':
                    pixels = item.p_list
                for x, y in pixels:
                    if x>=0 and x<self.length and y>=0 and y<self.height:
                        color=[int(item.color.red()),int(item.color.green()),int(item.color.blue())]
                        canvas[y, x] = np.array(color)
            if path[0] != '':
                Image.fromarray(canvas).save(path[0], 'bmp')
                self.changed=False

    def reset_canvas_action(self):
        self.check()
        self.length,flag1 = QInputDialog.getInt(self,'input','length',1500,500,2000)
        self.height,flag2 = QInputDialog.getInt(self,'input','height',1000,300,1500)
        if flag1 and flag2:
            self.list_widget.clearSelection()
            self.list_widget.clear()
            self.canvas_widget.clear_selection()
            self.canvas_widget.item_dict.clear()
            self.canvas_widget.scene().clear()
            self.item_cnt = 0
            self.changed = False
            self.canvas_widget.status = ''
            self.scene.setSceneRect(0, 0, self.length, self.height)
            self.canvas_widget.setFixedSize(self.length,self.height)

    def get_id(self,flag=True):
        if not flag:
            self.item_cnt += 1
        _id = str(self.item_cnt)
        return _id

    def line_naive_action(self):
        self.check()
        self.canvas_widget.start_draw_line('Naive', self.get_id())
        self.statusBar().showMessage('Naive算法绘制线段')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    def line_DDA_action(self):
        self.check()
        self.canvas_widget.start_draw_line('DDA', self.get_id())
        self.statusBar().showMessage('DDA算法绘制线段')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()
    
    def line_bresenham_action(self):
        self.check()
        self.canvas_widget.start_draw_line('Bresenham', self.get_id())
        self.statusBar().showMessage('Bresenham算法绘制线段')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()
    
    def polygon_DDA_action(self):
        self.check()
        self.canvas_widget.start_draw_polygon('DDA', self.get_id())
        self.statusBar().showMessage('DDA算法绘制多边形')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    def polygon_bresenham_action(self):
        self.check()
        self.canvas_widget.start_draw_polygon('Bresenham', self.get_id())
        self.statusBar().showMessage('Bresenham算法绘制多边形')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    def ellipse_action(self):
        self.check()
        self.canvas_widget.start_draw_ellipse(self.get_id())
        self.statusBar().showMessage('绘制椭圆')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    def curve_bezier_action(self):
        self.check()
        self.canvas_widget.start_draw_curve('Bezier',self.get_id())
        self.statusBar().showMessage('绘制Bezier曲线')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    def curve_b_spline_action(self):
        self.check()
        self.canvas_widget.start_draw_curve('B-spline',self.get_id())
        self.statusBar().showMessage('绘制B-spline曲线')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    def pen_action(self):
        self.check()
        self.canvas_widget.start_free_draw(self.get_id())
        self.statusBar().showMessage('画笔绘图')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    def translate_action(self):
        self.check()
        self.canvas_widget.start_translate()
        self.statusBar().showMessage('平移图元')

    def rotate_action(self):
        self.check()
        self.canvas_widget.start_rotate()
        self.statusBar().showMessage('旋转图元')

    def scale_action(self):
        self.check()
        self.canvas_widget.start_scale()
        self.statusBar().showMessage('缩放图元')

    def clip_cohen_sutherland_action(self):
        self.check()
        self.canvas_widget.start_clip('Cohen-Sutherland')
        self.statusBar().showMessage('Cohen-Sutherland算法裁剪')
        
    def clip_liang_barsky_action(self):
        self.check()
        self.canvas_widget.start_clip('Liang-Barsky')
        self.statusBar().showMessage('Liang-Barsky算法裁剪')

    def delete_action(self):
        self.check()
        self.canvas_widget.start_delete()
        self.statusBar().showMessage('删除图元')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mw = MainWindow()
    mw.show()
    sys.exit(app.exec_())
