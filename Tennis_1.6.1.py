#-*- coding: cp1251 -*-

import os

import cv2
import tkinter
import tkinter.filedialog
from tkinter import simpledialog
from tkinter import messagebox

import numpy as np
import PIL.Image, PIL.ImageTk


class Image(): # image settings
    def __init__(self, frame, fgbg):
        self.fgbg = fgbg
        self.frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        self.detection = False
        self.iter = 0

        if len(Tg.edge_coordinates) == 0:
            self.markerCorners, self.markerIds, self._ = cv2.aruco.detectMarkers(self.frame, Tg.dictionary, parameters=Tg.parameters)
            cv2.aruco.drawDetectedMarkers(self.frame, self.markerCorners) 
            if isinstance(self.markerIds, np.ndarray):
                self.markerIds = [i[0] for i in self.markerIds.tolist()]
                if len(self.markerIds) == 4:
                    self.coordinates = [[ii for ii in i.tolist()[0]][0] for i in list(self.markerCorners)]
                    self.d = dict(zip(self.markerIds, self.coordinates))
                    Tg.edge_coordinates = [self.d[1], self.d[4], self.d[2], self.d[3]]
                    Tg.w_h_count()

        else: #if coordinates entered
            self.M = cv2.getPerspectiveTransform(np.float32(Tg.edge_coordinates),
                                                 Tg.px_coordinates)# delete perspective
            self.frame = cv2.warpPerspective(self.frame,self.M,(500,500))
            self.refers = [500/Tg.w_h_px[0], 500/Tg.w_h_px[1]]

            self.crate_bin_mask() #threshold detection
            self.find_conturs()
            self.find_hit_point()

    def crate_bin_mask(self):
        self.hsv = cv2.cvtColor(self.frame.copy(), cv2.COLOR_RGB2HSV)
        self.mask = self.fgbg.apply(self.frame)
        self.mask = cv2.morphologyEx(self.mask, cv2.MORPH_ELLIPSE, np.ones((5,5),np.uint8))

    def find_conturs(self):
        self.cont,_ = cv2.findContours(self.mask.copy(),cv2.RETR_EXTERNAL, 
                                       cv2.CHAIN_APPROX_SIMPLE)
        self.contours_sizes = [(cv2.contourArea(cnt), cnt) for cnt in self.cont]
        if len(self.contours_sizes)>0: #if the contour is found
            self.larger_countur=max(self.contours_sizes, key = lambda x: x[0])[1]
            if int(cv2.arcLength(self.larger_countur,True)) >= 40: #if the larger contour is greater than 40
                self.M = cv2.moments(self.larger_countur) #the center of the contour
                self.Cx = int(self.M["m10"] / self.M["m00"])
                self.Cy = int(self.M["m01"] / self.M["m00"])
                self.detection = True
                Tg.center_points.append([self.Cx,self.Cy])
                self.iter = 0
                Tg.hit_coord = []
        else:
             self.detection = False

    def find_hit_point(self):
        if len(Tg.hit_coord) == 0:
            if Tg.cam_location == "left":
                for self.Cx,self.Cy in Tg.center_points:
                    if self.Cx == min([i[0] for i in Tg.center_points]):
                        self.frame = cv2.circle(self.frame, (self.Cx,self.Cy), 
                                                8,(255,0,0), -1)
                        Tg.hit_coord = [self.Cx,self.Cy]
                        break
            else:
                for self.Cx,self.Cy in Tg.center_points:
                    if self.Cx == max([i[0] for i in Tg.center_points]):
                        self.frame = cv2.circle(self.frame, (self.Cx,self.Cy), 
                                                8,(255,0,0), -1)
                        Tg.hit_coord = [self.Cx,self.Cy]
                        break
        else:
            if self.iter == 0:  
                Tg.center_points = []
                self.f = open(Tg.save_path + "coords.txt", "w")
                try:
                    self.Cx = Tg.hit_coord[0]
                    self.Cy = Tg.hit_coord[1]
                    x, y = self.count_coord()
                    self.f.write(str([int(x), int(y)])[1:-1])
                finally:
                    self.f.close()

                self.iter +=1
            self.frame = cv2.circle(self.frame, (self.Cx, self.Cy), 
                        8,(255,0,0), -1)

    def count_coord(self):
        return[(Tg.w_h_cm[0]/(Tg.w_h_px[0]/self.Cx))/self.refers[0],
               (Tg.w_h_cm[1]/(Tg.w_h_px[1]/self.Cy))/self.refers[1]]

class Target(): # target settings
    def __init__(self):
        self.edge_coordinates = []
        self.w_h_cm = [100,100] # target size
        self.px_coordinates = np.float32([[0,0],[500,0],[0,500],[500,500]])
        self.center_points = []
        self.cam_location = "left"
        self.dictionary = cv2.aruco.Dictionary_get(cv2.aruco.DICT_4X4_50)
        self.parameters =  cv2.aruco.DetectorParameters_create()
        self.hit_coord = []
        self.save_path = os.getcwd()

    def w_h_count(self):
        self.w_h_px = [abs(self.edge_coordinates[0][0]-self.edge_coordinates[1][0]),abs(self.edge_coordinates[0][1]-self.edge_coordinates[2][1])]

    def reset_target(self):
        self.edge_coordinates = []

class VideoCapture():# videosourse
    def __init__(self, videocapture):
        self.Vid = cv2.VideoCapture(videocapture, cv2.CAP_DSHOW)

        if not self.Vid.isOpened():
            raise ValueError("Unable to open video source", 1)

        self.width = self.Vid.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.height = self.Vid.get(cv2.CAP_PROP_FRAME_HEIGHT)

    def get_frame(self, fgbg):
        if self.Vid.isOpened():
            ret, frame = self.Vid.read()
            if ret:
                self.Img = Image(frame, fgbg)
                return (True, self.Img.frame)
            else:
                raise ValueError("Unable to open video source", 1)
                return (False, None)
        else:
            raise ValueError("Unable to open video source", 1)
            return (False, None)

    def __del__(self):
        if self.Vid.isOpened():
            self.Vid.release()

class App():# app
    def __init__(self, window):
        #If You have any questions about this
        # code, please email me, ve_r_es@mail.ru
        # or rusanovgleb02@mail.ru 

        self.window = window
        self.cam_1 = tkinter.PhotoImage(file = "cam_1.png")
        self.cam_0 = tkinter.PhotoImage(file = "cam_0.png")
        self.swc_right = tkinter.PhotoImage(file = "right.png")
        self.swc_left = tkinter.PhotoImage(file = "left.png")

        self.Vid = VideoCapture(0) 
        self.fgbg = cv2.createBackgroundSubtractorMOG2(detectShadows = True) 

        self.text = False
        self.cam = 0 
        self.cam_location = "left"

        self.window_settings()

        self.window_update()
        self.window.mainloop()

    def window_settings(self):
        #Если у Вас появились вопросы по этому коду,
        # пишите мне, ve_r_es@mail.ru
        # или rusanovgleb02@mail.ru 

        self.window.title("Tennis")  # create the window
        self.window.geometry("800x900")

        self.mainmenu = tkinter.Menu(self.window) 
        self.window.config(menu=self.mainmenu) 

        self.filemenu = tkinter.Menu(self.mainmenu, tearoff=0)
        self.filemenu.add_command(label='Сохранять координаты в ...',
                                 command = self.save_to)
        self.filemenu.add_command(label='Размер мишени', 
                                  command = self.set_target_size)

        self.mainmenu.add_cascade(label="Файл",
                     menu=self.filemenu)


        self.helpmenu = tkinter.Menu(self.mainmenu, tearoff=0)
        self.helpmenu.add_command(label="Связь с разработчиками", command = self.connection)
        self.mainmenu.add_cascade(label="Справка",
                                  menu=self.helpmenu)

        self.canvas = tkinter.Canvas(self.window, width = self.Vid.width + 100, 
                                     height = self.Vid.height + 100)
        self.canvas.pack()

        self.tg_reset = tkinter.Button(self.window, text="Сбросить минень", 
                                        width=20, command=Tg.reset_target,
                                        font=('Helvetica 12 bold'))# reset button
        self.tg_reset.pack(pady = 20, padx = 60, side=tkinter.LEFT)

        self.cam_swc = tkinter.Button(self.window, image=self.cam_0,
                                      bd = 0, command = self.cam_switch)# 1 or 2 video sourse
        self.cam_swc.pack(padx = 10, side=tkinter.LEFT)

        self.rl_cam_swc = tkinter.Button(self.window, image=self.swc_left,
                                      bd = 0, command = self.cam_loc_switch)# right or left cam
        self.rl_cam_swc.pack(padx = 10, side=tkinter.LEFT)

        self.indicator_oval = self.canvas.create_oval(500, 500, 550, 550 ,fill="red")

    def window_update(self):
        self.ret, self.frame = self.Vid.get_frame(self.fgbg)
        if self.ret:
            self.photo = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(self.frame))
            self.canvas.create_image(0, 0, image = self.photo, anchor = tkinter.NW) 
        else:
            raise ValueError("Unable to open video source", 1)

        if self.Vid.Img.detection == True:
            self.count_coord()

        if len(Tg.edge_coordinates) == 4:
            self.canvas.itemconfig(self.indicator_oval, fill="green")

        self.window.after(1, self.window_update)

    def cam_switch(self):
        self.cam = abs(self.cam - 1)
        self.Vid = VideoCapture(self.cam)

        if self.cam == 0:
            self.cam_swc.config(image = self.cam_1)
        else:
            self.cam_swc.config(image = self.cam_0)

    def cam_loc_switch(self):
        if self.cam_location == "left":
            self.cam_location = "right"
            self.Tg.cam_location = "right"
            self.rl_cam_swc.config(image = self.swc_right)
        else:
            self.cam_location = "left"
            self.Tg.cam_location = "left"
            self.rl_cam_swc.config(image = self.swc_left)

    def count_coord(self):
        x,y = self.Vid.Img.count_coord()
        if self.text!= False:
            self.canvas.delete(self.text)
        self.text=self.canvas.create_text(600, 100, text= str([int(x), int(y)]),font=('Helvetica 20 bold'))
        self.canvas.pack()

    def set_target_size(self):
        self.w = simpledialog.askinteger("Ширина", "Ширина мишени",
                                parent = self.window, minvalue = 0) 
        Tg.w_h_cm = [self.w, self.w]

    def save_to(self):
        Tg.save_path = tkinter.filedialog.askdirectory()
        print(Tg.save_path)

    def connection(self):
        self.msg = "Почта для связи ve_r_es@mail.ru \n или rusanovgleb02@mail.ru"
        messagebox.showinfo("Связь", self.msg)


if __name__=="__main__":
    Tg = Target()
    App(tkinter.Tk())
