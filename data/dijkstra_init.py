#build-in modules
import tkinter as tk
from tkinter import messagebox
import time
import datetime
from functools import partial
import os
import base64
from platform import system
#modules you need to install by pip
import cv2#opencv
from PIL import Image, ImageTk#pillow
from selenium import webdriver
import requests
from tkinter import ttk 
from ttkthemes import ThemedTk

#our own py file
import osmium_version5 as my_osm_data
import near_station
import get_all_station

#current path
if system() == 'Windows':
    current_path = os.getcwd() + '\\'
else:
    current_path = os.getcwd() + '/'
class Node:

    def __init__(self, ref, index = None):
        self.ref = ref
        self.index = index
    
    def __str__(self):
        return self.ref

class Graph:

    def __init__(self, node_list):
        #node_list = [Node(x) for x in node_list]
        #set up the index for nodes
        for i in range(len(node_list)):
            node_list[i].index = i
        #set up a adjacency matrix
        self.adj_mat = [[0]*len(node_list) for _ in range(len(node_list))]
        self.all_nodes = node_list
    #connect node1 and node2
    #update the adjacency matrix
    def connect_node(self, node1, node2, weight=1):
        self.adj_mat[node1.index][node2.index] = weight
        self.adj_mat[node2.index][node1.index] = weight

    #get the all connected nodes from node
    #return value: array of tuples(connected node, weight )
    def connection(self, node):
        return [(self.all_nodes[node], weight) for node, weight in enumerate(self.adj_mat[node.index]) if weight !=0 ]
    
    #get the node object with its index
    def get_node_from_index(self, index):
        return self.all_nodes[index]
    
    def __str__(self):
        matrix = str([x.ref for x in self.all_nodes]) + '\n'
        for i in self.adj_mat:
            matrix += str(i)
            matrix += '\n'
        return matrix
    
    def dijkstra(self, start_node, end):
        #initialize the distance(or the argument we are considering) list keeping track of distance
        #from start_node to other nodes
        #list format: [distance, addititonal argument, [node hops]]
        dist = [None] * len(self.all_nodes)
        for i in range(len(dist)):
            #asign infinity for all nodes but the start_node
            dist[i] = [float('inf')]
            #asign 0 to the additional argument
            dist[i].append(0)
            dist[i].append([start_node])
        #set the start node distance as 0
        dist[start_node.index][0] = 0
        #integers in the queue correspond to indices of node 
        quene = [x for x in range(len(self.all_nodes))]
        #integers in the seen set correspond to indices of node seen so far
        seen = set()
        while len(quene) > 0:
            #get the node in queue that has not yet been seen 
            #and has the smallest distance to the start_node
            min_dist = float('inf')
            min_node = None
            for n in quene:
                if dist[n][0]+dist[n][1] < min_dist and n not in seen:
                    min_dist = dist[n][0]
                    min_node = n
            #add min distance node to seen, and remove it from queue
            quene.remove(min_node)
            seen.add(min_node)
            #get all next hops
            connections = self.connection(self.get_node_from_index(min_node))
            #for each connection, update its path and total distance form
            #start_node if the total distance is less than the current
            #distance in dist array
            for (node, weight) in connections:
                #count the total distance from node to start_node
                tot_dist = weight + min_dist
                if tot_dist < dist[node.index][0]:
                    #update the provision distance
                    dist[node.index][0] = tot_dist
                    #get the hops from start_node to node 
                    dist[node.index][2] = list(dist[min_node][2])
                    dist[node.index][2].append(node)
                    #update the addition argument
                    if len(dist[node.index][2]) > 2:
                        dist[node.index][1] = (len(dist[node.index][2]) - 2)*0.5
            if end.index in seen: return [(weight, addition_time, nodes) for weight, addition_time, nodes in dist if nodes[-1] == end]
        return dist

# read the information of each metro line
station = list()
station_dict=dict()
data=dict()
with open(current_path+'lines.csv','r') as fin:
    for line in fin:
        line.strip()
        temp = line.split(';')
        data[temp[0]] = [float(x) for x in temp[3:]]
        station_nodes=list()
        station_dict[temp[0]] = list()
        for i in range(int(temp[1]),int(temp[2])+1):
            station_nodes.append(Node('%s%02d' % (temp[0], i)))
        station_dict[temp[0]].extend(station_nodes)

for value in station_dict.values():
    station += value

#create Graph instance
metro_graph = Graph(station)

#connect nodes in each line
for key,value in station_dict.items():
    for i in range(1,len(value)):
        metro_graph.connect_node(value[i-1], value[i], data[key][i-1])

#read data for transfering
with open(current_path +'transitions.csv', 'r') as fin2:
    for line in fin2:
        temp = line.strip().split(';')
        metro_graph.connect_node(station_dict[temp[0]][int(temp[1])-1 if temp[0] != 'Mb' else int(temp[1])-3],
                                 station_dict[temp[2]][int(temp[3])-1 if temp[2] != 'Mb' else int(temp[3])-3],
                                 int(temp[4]))

        


#opening animation

root = tk.Tk()
root.configure(background='white')
root.config(cursor='starting')
# Create a frame
app = tk.Frame(root, bg="white")
app.place(x=root.winfo_screenwidth()/2, y=root.winfo_screenheight()/2, anchor='center')
# Create a label in the frame
lmain = tk.Label(app)
lmain.grid()

cap = cv2.VideoCapture(current_path +'op.mp4')

# function for video streaming
def video_stream():
    _, frame = cap.read()
    cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
    img = Image.fromarray(cv2image)
    imgtk = ImageTk.PhotoImage(image=img)
    lmain.imgtk = imgtk
    lmain.configure(image=imgtk, bg = 'white')
    lmain.after(1, video_stream) 

video_stream()
root.attributes("-fullscreen", True)
root.after(6000, lambda: root.destroy())
root.mainloop()




#open main window
window = ThemedTk(theme="clearlooks")
#window.configure(bg='#40E0D0')
window.tk.call('wm','iconphoto', window._w, tk.PhotoImage(file=current_path +'icon.png'))
window.title('Tokyo_metro_app')
window.geometry('640x720')



#for api key
client_key = tk.StringVar()
k = ''
fin = open(current_path +'times.txt', 'r')
raw_times = fin.readline().strip()
times = int(base64.b64decode(raw_times).decode('UTF-8'))
raw_key=fin.readline().strip()
raw_key = raw_key.encode('UTF-8')
default_key = base64.b64decode(raw_key).decode("UTF-8")
key = default_key
fin.close()

def callbutton(win):
    global k
    if len(client_key.get().strip()) > 10:
        k = client_key.get().strip()
        win.destroy()
    elif 0 < len(client_key.get()) < 10:
        client_key.set('')
        tk.Label(win, text='unavailable key!').grid(row=6,column=0)
    else:
        win.destroy()
def google_api(link, event):
    '''
    open brower to show more information for each station
    '''
    driverpath=current_path +'geckodriver.exe'
    browser = webdriver.Firefox(executable_path = driverpath)
    browser.set_window_position(0,0) 
    browser.get(link)

def API():
    key_window = tk.Toplevel(window)
    key_window.tk.call('wm','iconphoto', key_window._w, tk.PhotoImage(file=current_path +'icon.png'))
    tk.Label(key_window, text='Warning', font=('Verdana', 20),fg='red').grid(row=0, column=0,sticky='w',columnspan=2)
    tk.Label(key_window, text='Your only have limit times to use the feature of entering arbitary location.', 
                font=('Arial', 13)).grid(row=1, column=0,sticky='w',columnspan=2)
    tk.Label(key_window, text='remaining times: %d' % times, font=('Arial', 13),fg='green').grid(row=2, column=0,sticky='w',columnspan=2)
    tk.Label(key_window, text='''If you want get unlimited times to use the feature of entering arbitary location,''', font=('Arial', 13)).grid(row=3, column=0,sticky='w',columnspan=2)
    tk.Label(key_window, text= 'please enter your google api key', font=('Arial', 13)).grid(row=4, column=0,sticky='w',columnspan=2)
    ttk.Entry(key_window, textvariable=client_key, width=50).grid(row=5, column=0,sticky='w')

    ok_button = ttk.Button(key_window, text='finish', command=partial(callbutton, key_window))
                            #bg='deep sky blue', font=('Arial',13),
                            #fg='white')
    ok_button.grid(row=6, column=0,sticky='w')
    more = tk.Label(key_window, text='What is google api key?', fg='blue')
    more.bind('<Enter>', lambda e:more.config(cursor='hand2'))
    more.bind('<Leave>', lambda e: more.config(cursor=''))
    more.bind('<Button-1>', partial(google_api, 'https://cloud.google.com/apis/docs/overview?hl=zh-TW'))
    more.grid(row=5,column=1,sticky='w')

API()

#add menu
menu = tk.Menu(window)
submenu = tk.Menu(menu, tearoff = 0)
submenu.add_command(label='About', command=lambda :os.startfile(current_path +'User_Guide_for_Tokyo_Metro_App.pdf'))
submenu.add_command(label='API', command = API)
menu.add_cascade(label='Help', menu=submenu)
window.config(menu=menu)

tk.Label(window, text='From',fg='white', bg='steel blue',
         font=('Arial', 12), height=1, width=6).place(x=0, y=0)
tk.Label(window, text='To',fg='white', bg='medium violet red', 
         font=('Arial', 12), height=1, width=6).place(x=0, y=30)


#entry for start and end
svar = tk.StringVar()
svar.set('G01')
start_entry = ttk.Entry(window, textvariable=svar)
start_entry.place(x=70,y=3, anchor='nw')

evar = tk.StringVar()
evar.set('淺草寺')
end_entry = ttk.Entry(window, textvariable=evar)
end_entry.place(x=70,y=32,anchor='nw')

#walk image
walk = Image.open(current_path +'walking.png')
walk = walk.resize((40,40), Image.ANTIALIAS)
walk = ImageTk.PhotoImage(walk)
#switch image
img = Image.open(current_path +'change.png')
img = img.resize((40,40), Image.ANTIALIAS)
img=ImageTk.PhotoImage(img)

# for network map image
cooridnates=list()
with open(current_path +'station_coordinate.txt', 'r') as fin:
    count = 0
    station_ravel = get_all_station.station_ravel()
    for line in fin:
        temp = [int(x) for x in line.strip().split()] + [station_ravel[count]]
        count += 1
        cooridnates.append(temp)

#get link of each station
with open(current_path +'station_link.csv', 'r', encoding='utf8') as link_file:
    count = 0
    for line in link_file:
        temp = line.strip().split(',')
        cooridnates[count].extend(temp[1:])
        count += 1
    
#addition information for line Mb
cooridnates[287].extend(['https://zh.wikipedia.org/wiki/%E6%96%B9%E5%8D%97%E7%94%BA%E7%AB%99', '方南町駅'])
cooridnates[288].extend(['https://zh.wikipedia.org/wiki/%E4%B8%AD%E9%87%8E%E5%AF%8C%E5%A3%AB%E8%A6%8B%E7%94%BA%E7%AB%99', '中野富士見町駅'])
cooridnates[289].extend(['https://zh.wikipedia.org/wiki/%E4%B8%AD%E9%87%8E%E6%96%B0%E6%A9%8B%E7%AB%99', '中野新橋駅'])
color_dict = {'G': 'orange', 'M':'red','Mb':'red3','H':'silver', 'T':'sky blue', 'C':'green',
              'Y':'yellow', 'Z':'purple', 'N':'turquoise', 'F':'brown',
              'A':'maroon1', 'I':'blue', 'S':'forest green', 'E':'deep pink'}
relation_dict = {'G': 'Ginza Line', 'M':'Marunouchi Line','Mb':'Marunouchi Line Branch Line','H':'Hibiya Line', 'T':'Tōzai Line', 'C':'Chiyoda Line',
                'Y':'Yūrakuchō Line', 'Z':'Hanzōmon Line', 'N':'Namboku Line', 'F':'Fukutoshin Line',
                'A':'Asakusa Line', 'I':'Mita Line', 'S':'Shinjuku Line', 'E':'Oedo Line'}

class ScrollFrame(tk.Frame):
    '''
    create a scrollable frame
    '''
    def __init__(self, parent):
        super().__init__(parent) # create a frame (self)
        #place canvas on self
        self.canvas = tk.Canvas(self, borderwidth=0, height=300)
        #place a frame on the canvas, this frame will hold the child widgets 
        self.viewPort = tk.Frame(self.canvas)
        #place a scrollbar on self
        self.vsb = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)         
        self.canvas.configure(yscrollcommand=self.vsb.set)
        #pack scrollbar to right of self
        self.vsb.pack(side="left", fill="y")
        #pack canvas to left of self and expand to fil
        self.canvas.pack(side="left", fill="both", expand=True)
        #add view port frame to canvas
        self.canvas_window = self.canvas.create_window((4,4), window=self.viewPort, anchor="nw", tags="self.viewPort")
        #bind an event whenever the size of the viewPort frame changes.
        self.viewPort.bind("<Configure>", self.onFrameConfigure)
        self.canvas.bind("<Configure>", self.onCanvasConfigure)
        #perform an initial stretch on render, otherwise the scroll region has a tiny border until the first resize
        self.onFrameConfigure(None)

    def onFrameConfigure(self, event):                                              
        '''Reset the scroll region to encompass the inner frame'''
        #whenever the size of the frame changes, alter the scroll region respectively.
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def onCanvasConfigure(self, event):
        '''Reset the canvas window to encompass inner frame when required'''
        canvas_width = event.width
        #whenever the size of the canvas changes alter the window region respectively.
        self.canvas.itemconfig(self.canvas_window, width = canvas_width)

class Usage(tk.Frame):
    '''
    class inherited from ScrollFrame
    '''

    def __init__(self, root, trans, trans_time,s,e):

        tk.Frame.__init__(self, root)
        self.scrollFrame = ScrollFrame(self) # add a new scrollable frame.
        self.trans = trans
        self.trans_time = trans_time
        # add some controls to the scrollframe. 
        # the child controls are added to the view port (scrollFrame.viewPort, NOT scrollframe itself)



        count = 0
        start_is_trans = False
        if trans[0] == trans[1]:
            c = tk.Canvas(self.scrollFrame.viewPort, width=400, height = 45)
            c.create_image(60,5, anchor='nw', image=walk)
            for t in range(5):
                c.create_rectangle(20,0+t*10,40,5+t*10, outline='black', fill='black')
            c.create_text(120, 25, anchor='w', text='Walk to %s platform' % (trans[2].ref), fill='gray', font=('Arial', 13))
            c.create_text(350,25, anchor='e', text=str(trans_time[0]), fill='gray53', font=('Arial', 13))
            c.grid(row=0, column = 0)
            start_is_trans = True
            trans = trans[2:]
            trans_time=trans_time[1:]

        for i in range(len(trans)//2):
            if i == (len(trans)//2)-1 and trans[-1] == trans[-2]:
                break
            canvas= tk.Canvas(self.scrollFrame.viewPort, width = 400, height=165, bg='white')
            canvas.create_rectangle(20,20,40,150,outline=color_dict[trans[count].ref[0]],fill=color_dict[trans[count].ref[0]])
            canvas.create_oval(17,7,43,33, outline=color_dict[trans[count].ref[0]], fill='white')
            canvas.create_oval(17,137,43,163, outline=color_dict[trans[count].ref[0]], fill='white')
            canvas.create_text(50,5, text=trans[count], anchor='nw', fill='black',font=('Verdana', 17))
            canvas.create_text(50,95,text=relation_dict[trans[count].ref[0]], anchor='sw', fill='gray75', font=('Tahoma', 14))
            canvas.create_text(350,95, text=int(trans_time[count]), anchor='se', fill='gray75', font=('Tahoma', 14))
            canvas.create_text(350,95, text='min', anchor='sw', fill='gray75', font=('Tahoma', 11))
            canvas.create_text(50,135,text=trans[count+1], anchor='nw', fill='black',font=('Verdana', 17))
            
            canvas.grid(row=int(start_is_trans)+i*2, column = 0)
            count += 2
            if i != (len(trans)//2)-1:
                interval = tk.Canvas(self.scrollFrame.viewPort, width = 400, height = 45)
                interval.create_image(60,5, anchor='nw', image=walk)
                interval.create_text(120, 33, anchor='sw', text='Walk to %s platform' % (trans[count].ref), fill='gray53', font=('Arial', 13))
                interval.create_text(350,33, anchor='se', text=str(trans_time[count-1]), fill='gray53', font=('Arial', 13))
                interval.create_text(350,33, text='min', anchor='sw', fill='gray53', font=('Arial', 10))
                for t in range(5):
                    interval.create_rectangle(20,0+t*10,40,5+t*10, outline='black', fill='black')
                if start_is_trans:
                    interval.grid(row=i*2+1+1, column=0)
                else:
                    interval.grid(row=i*2+1, column = 0)

        # when packing the scrollframe, we pack scrollFrame itself (NOT the viewPort)
        self.scrollFrame.pack(side="top", fill="both", expand=True)




def check_internet():
    '''
    check whether your computer is connected to the Internet
    '''
    url='http://www.google.com/'
    timeout=5
    try:
        _ = requests.get(url, timeout=timeout)
        return True
    except requests.ConnectionError:
        #print("No Internet")
        return False


def enter():
    '''
    function being called when the search 'button' was clicked
    '''
    window.config(cursor='wait')
    cover = tk.Label(window,width=640, height=2000)
    cover.place(x=20,y=110)
    s_info = start_entry.get().strip()
    e_info = end_entry.get().strip()
    if s_info == '':
        messagebox.showwarning('Tokyo_metro_app', 'your start location can not be blank')
        window.config(cursor='')
        return None
    if e_info == '':
        messagebox.showwarning('Tokyo_metro_app', 'your end location can not be blank')
        window.config(cursor='')
        return None
    
    def guide(s, s_instruction, e, e_instruction):
        if s == None and e == None:
            window.config(cursor='')
            return None
        guide_window = tk.Toplevel(window)
        guide_window.tk.call('wm','iconphoto', guide_window._w, tk.PhotoImage(file=current_path +'icon.png'))
        if s != None:
            tk.Label(guide_window, text = 'From %s to the nearest station %s' % (s[0], s[1]), font=('Arial', 15)).grid(row=0,column=0,sticky="w",columnspan=2)
            for i in range(len(s_instruction)):
                tk.Label(guide_window, text = 'step %d' % (i+1), font=('Tahoma', 12),fg='blue').grid(row=i+1, column=0,sticky='w')
                tk.Label(guide_window, text = s_instruction[i], font=('Arial', 12)).grid(row = i+1, column =1,sticky="w")
        if e!= None:
            tk.Label(guide_window, text = 'From %s to %s' % (e[1], e[0]), font=('Arial', 15)).grid(row=0,column=0,sticky="w",columnspan=2)
            for i in range(len(e_instruction)):
                tk.Label(guide_window, text = 'step %d' % (i+1), font=('Tahoma', 12),fg='blue').grid(row=i+1, column=0,sticky='w')
                tk.Label(guide_window, text = e_instruction[i], font=('Arial', 12)).grid(row = i+1, column =1,sticky="w")

    def main(s_info, e_info, all_from_to_list, tot_time, s=False, e=False):
        if s_info[1] == 'b':
            start = station_dict[s_info.strip()[0:2]][int(s_info.strip()[2:])-3]
        else:
            start = station_dict[s_info.strip()[0]][int(s_info.strip()[1:])-1]
        if e_info[1] == 'b':
            end = station_dict[e_info.strip()[0:2]][int(e_info.strip()[2:])-3]
        else:
            end = station_dict[e_info.strip()[0]][int(e_info.strip()[1:])-1]

        result = metro_graph.dijkstra(start, end)
        if s == False and e == True:
            tot_time.insert(0, result[0][0] + result[0][1])
        else:
            tot_time.insert(1, result[0][0] + result[0][1])

        trans = [result[0][2][0]]
        index_count=0
        for i in range(1, len(result[0][2])):
            if result[0][2][i].ref[0] != trans[index_count].ref[0]:
                trans.append(result[0][2][i-1])
                trans.append(result[0][2][i])
                index_count += 2
            elif result[0][2][i].ref[1] == 'b' and trans[index_count].ref[1] != 'b':
                trans.append(result[0][2][i-1])
                trans.append(result[0][2][i])
                index_count += 2
            elif result[0][2][i].ref[0:2] != 'Mb' and trans[index_count].ref[1] == 'b':
                trans.append(result[0][2][i-1])
                trans.append(result[0][2][i])
                index_count += 2
        else:
            trans.append(result[0][2][-1])
    
        trans_time = list()
        if trans[0] == trans[1]:
            if trans[-1] == trans[-2]:
                for i in range(2, len(trans)-1):
                    temp = metro_graph.dijkstra(trans[i-1], trans[i])
                    trans_time.append(temp[0][0] + temp[0][1])
            else:
                for i in range(2, len(trans)):
                    temp = metro_graph.dijkstra(trans[i-1], trans[i])
                    trans_time.append(temp[0][0] + temp[0][1])
        elif trans[-1] == trans[-2]:
            for i in range(1, len(trans)-1):
                temp = metro_graph.dijkstra(trans[i-1], trans[i])
                trans_time.append(temp[0][0] + temp[0][1])
        else:
            for i in range(1, len(trans)):
                temp = metro_graph.dijkstra(trans[i-1], trans[i])
                trans_time.append(temp[0][0] + temp[0][1])
        #print(trans_time)
        if len(trans) == 2:
            transf='No Transfer'
        elif len(trans) == 3:
            transf='Transfer: 1'
        else:
            transf='Transfers: %d' % ((len(trans)-2)/2)

        #fare
        def get_fare(trans):
            ''' give a list containing all starts and ends
            return fart'''
            fare_list = [170,200,240,280,310]
            distance = 0
            print([x.ref for x in trans])
            for stat in range(len(trans)-1):
                
                try:
                    distance += my_osm_data.count_way_distance(trans[stat].ref, trans[stat+1].ref)
                except UnboundLocalError:
                    distance+=0
                print(distance)
            distance = distance/1000
            if distance <= 6:
                return fare_list[0]
            elif distance <=11:
                return fare_list[1]
            elif distance <=19:
                return fare_list[2]
            elif distance <=27:
                return fare_list[3]
            else:
                return fare_list[4]


        # time
        start_time_list= list()
        end_time_list=list()
        cur_time = datetime.datetime.now()
        start_time_list.append(cur_time)
        if s and e:
            start_time_list.insert(1, start_time_list[0]+datetime.timedelta(minutes=tot_time[0]))
            start_time_list.insert(2,start_time_list[1]+ datetime.timedelta(minutes=tot_time[1]))
            end_time_list.insert(0, start_time_list[1])
            end_time_list.insert(1, start_time_list[2])
            end_time_list.insert(2, start_time_list[2]+datetime.timedelta(minutes=tot_time[2]))
        elif e:
            start_time_list.insert(1, cur_time+datetime.timedelta(minutes=tot_time[0]))
            end_time_list.insert(0, start_time_list[1])
            end_time_list.insert(1,start_time_list[1]+ datetime.timedelta(minutes=tot_time[1]))
        elif s :
            start_time_list.insert(1, cur_time+ datetime.timedelta(minutes=tot_time[0]))
            end_time_list.insert(0, start_time_list[1])
            end_time_list.insert(1, start_time_list[1] + datetime.timedelta(minutes=tot_time[1]))
        else:
            end_time_list.append(cur_time + datetime.timedelta(minutes=tot_time[0]))
        #start_time.set('%02d:%02d' % (cur_time.hour,  cur_time.minute))
        #end_time.set('%02d:%02d' % (final_time.hour, final_time.minute))
        #print(str([('total time: about %.2f min' % (weight+time), [n.ref for n in node]) for (weight, time, node) in metro_graph.dijkstra(start, end) if node[-1] == end]))
        for i in range(1+s+e):
            top_canvas = tk.Canvas(window, width=400, height=78, bg='white')
            top_canvas.create_text(70,19,text=all_from_to_list[i][0],anchor='w',fill='black', font=('Arial', 12))
            top_canvas.create_text(70,50,text=all_from_to_list[i][1], anchor='w',fill='black', font=('Arial', 12))
            top_canvas.create_text(360,45, text=str(int(tot_time[i])),anchor='se',fill='black', font=('Arial', 25))
            top_canvas.create_text(365,43, text='min', anchor='sw', fill='black', font=('Arial', 15))
            if s and i == 1:
                top_canvas.create_text(395,45, text=transf, anchor='ne', fill='green', font=('Arial', 10))
                top_canvas.create_text(395,60, text=str(get_fare(trans))+'yen', anchor='ne', fill='green', font=('Arial', 10))
            elif not s and e and i == 0:
                top_canvas.create_text(395,45, text=transf, anchor='ne', fill='green', font=('Arial', 10))
                top_canvas.create_text(395,60, text=str(get_fare(trans))+'yen', anchor='ne', fill='green', font=('Arial', 10))
            elif not s and not e:
                top_canvas.create_text(395,45, text=transf, anchor='ne', fill='green', font=('Arial', 10))
                top_canvas.create_text(395,60, text=str(get_fare(trans))+'yen', anchor='ne', fill='green', font=('Arial', 10))
            top_canvas.create_text(250, 19, text='%02d:%02d' % (start_time_list[i].hour,  start_time_list[i].minute), anchor='w', fill='gray',font=('Arial', 12))
            top_canvas.create_text(250, 50, text='%02d:%02d' % (end_time_list[i].hour, end_time_list[i].minute), anchor='w', fill='gray',font=('Arial', 12))
            top_canvas.place(x=20,y=120+90*i)
            s_label = tk.Label(window, text='From', fg='white', bg='steel blue', height=1, width=6)
            s_label.place(x=30,y=130+90*i)
            e_label = tk.Label(window, text='To', fg='white', bg='medium violet red', height=1, width=6)
            e_label.place(x=30,y=160+90*i)

        Usage(window, trans, trans_time,s,e).place(x=20, y=210+90*i)
        window.config(cursor='')
        
        
    
    all_from_to_list = list()
    tot_time = list()
    global times, key, k
    if s_info not in get_all_station.station_ravel():
        if k!= '':
            key = k
        elif times > 1:
            times -= 1
        elif times == 1:
            times -= 1
        if key != 'None':
            if check_internet() == True:
                my_start, start_instr = near_station.nearest_stations(s_info,key)
                if my_start == None and start_instr== None:
                    messagebox.showwarning('Tokyo_metro_app', "sorry! we can't find %s\nor %s is not in Tokyo" % (s_info, s_info))
                    svar.set('')
                    window.config(cursor='')
                    return None
                if direct.get():
                    guide(my_start,start_instr,None,None)
                if html.get():
                    near_station.plot(s_info, my_start[1], key)
                all_from_to_list.append((my_start[0], my_start[1]))
                s_info = my_osm_data.get_ref_from_name(my_start[1])[0]
                if type(s_info) == list:
                    s_info = s_info[0]
                s = True
                tot_time.append(my_start[2])
            else:
                messagebox.showwarning('Tokyo_metro_app', 'NO INTERNET\nyou should enter station name.')
                svar.set('')
                window.config(cursor='')
                return None
            if times == 0:
                key = 'None'
        else:
            messagebox.showwarning('Tokyo_metro_app', 'remaining times for useing the feature of entering arbitary location is 0!')
            svar.set('')
            window.config(cursor='')
            return None
    else:
        s=False
    
    if e_info not in get_all_station.station_ravel():
        if k!= '':
            key = k
        elif times > 1:
            times -= 1
        elif times == 1:
            times -= 1
        if key != 'None':
            if check_internet() == True:
                my_end, end_instr = near_station.nearest_stations(e_info,key)
                if my_end == None and end_instr== None:
                    messagebox.showwarning('Tokyo_metro_app', "sorry! we can't find %s\nor %s is not in Tokyo" % (e_info, e_info))
                    evar.set('')
                    window.config(cursor='')
                    return None
                if direct.get():
                    guide(None,None, my_end,end_instr)
                if html.get():
                    near_station.plot(e_info, my_end[1],key)
                all_from_to_list.append((my_end[1],my_end[0]))
                e_info = my_osm_data.get_ref_from_name(my_end[1])[0]
                e = True
                tot_time.append(my_end[2])
            else:
                messagebox.showwarning('Tokyo_metro_app', 'NO INTERNET\nyou should enter end name.')
                evar.set('')
                window.config(cursor='')
                return None
            if times == 0:
                key = 'None'
        else:
            messagebox.showwarning('Tokyo_metro_app', 'remaining times of using the feature of entering arbitary location is 0!')
            evar.set('')
            window.config(cursor='')
            return None
    else:
        e=False
    
    if s == False and e == True:
        all_from_to_list.insert(0,(s_info,e_info))
    if s==True and e==True:
        all_from_to_list.insert(1,(s_info,e_info))
    if s==False and e==False:
        all_from_to_list.append((s_info, e_info))
    if s == True and e==False:
        all_from_to_list.append((s_info, e_info))
    


    main(s_info, e_info, all_from_to_list, tot_time, s, e)
        
    
def switch():
    s_info = start_entry.get()
    e_info = end_entry.get()
    svar.set(e_info)
    evar.set(s_info)

def clear():
    s_info = start_entry.get()
    e_info = end_entry.get()
    svar.set('')
    evar.set('')

click_ref = list()



def network_map():
    '''
    function being called when the 'network map' button was clicked
    '''
    img_window = tk.Toplevel(window)
    img_window.tk.call('wm','iconphoto', img_window._w, tk.PhotoImage(file=current_path +'icon.png'))
    img_window.geometry('640x640')
    event2canvas = lambda e, c: (c.canvasx(e.x), c.canvasy(e.y))

    #setting up a tkinter canvas with scrollbars
    frame = tk.Frame(img_window, bd=2, relief=tk.SUNKEN)
    frame.grid_rowconfigure(0, weight=1)
    frame.grid_columnconfigure(0, weight=1)
    xscroll = tk.Scrollbar(frame, orient=tk.HORIZONTAL)
    xscroll.grid(row=1, column=0, sticky=tk.E+tk.W)
    yscroll = tk.Scrollbar(frame)
    yscroll.grid(row=0, column=1, sticky=tk.N+tk.S)
    canvas = tk.Canvas(frame, bd=0, xscrollcommand=xscroll.set, yscrollcommand=yscroll.set, bg='white')
    canvas.grid(row=0, column=0, sticky=tk.N+tk.S+tk.E+tk.W)
    xscroll.config(command=canvas.xview)
    yscroll.config(command=canvas.yview)
    frame.pack(fill=tk.BOTH,expand=1)

    #adding the image
    img = tk.PhotoImage(file=current_path +'all.png')
    img_window.map = img
    canvas.create_text(10,10,text='try', anchor='w')
    canvas.create_image(10,10,image=img,anchor="nw")
    canvas.config(scrollregion=canvas.bbox(tk.ALL))
     
    
    def set_start(ref, event):
        svar.set(ref)
    
    def set_end(ref, event):
        evar.set(ref)
    
    def open_browser(link, event):
        '''
        open brower to show more information for each station
        '''
        driverpath=current_path +'geckodriver.exe'
        browser = webdriver.Firefox(executable_path = driverpath)
        browser.set_window_position(0,0) 
        browser.get(link)
    
    #get the coordinate for each station in network map
    #and write coordinate in txt
    '''
    fin = open('station_coordinate.txt', 'a')
    def get_coordinate(event):
        temp_new =[]
        cx, cy = event2canvas(event, canvas)
        cx1 = cx - 15
        cx2 = cx + 15
        cy1 = cy - 20
        cy2 = cy + 20
        fin.write('%d %d %d %d\n' % (cx1, cy1, cx2, cy2))
    '''
    

    def show_information(event):
        global click_ref
        #outputting x and y coords to console
        cx, cy = event2canvas(event, canvas)
        x_move = 0
        y_move = 0
        win_centerx=img_window.winfo_width()/2
        win_centery=img_window.winfo_height()/2
        if event.x <= win_centerx:
            if event.y <= win_centery:
                x_move = 1
                y_move = 1
                anc = 'nw'
            else:
                x_move = 1
                y_move = -41
                anc = 'sw'
        else:
            if event.y <= win_centery:
                x_move = -31
                y_move = 1
                anc = 'ne'
            else:
                x_move = -31
                y_move = -41
                anc = 'se'
        for coor in cooridnates:
            if coor[0] <= cx <= coor[2] and coor[1] <= cy <=coor[3]:
                inframe = tk.Frame(img_window)
                ref = tk.Canvas(inframe, bg='white', width=220,height=100 ,relief=tk.RIDGE, highlightthickness=2, highlightbackground="gray")
                canvas.create_window(coor[2]+x_move,coor[3]+y_move,anchor=anc, window=inframe, tag=coor[4])
                ref.create_text(10,10,text=coor[4], anchor='nw', font=('Tahoma',17), fill='black')
                ref.create_text(210,13,text=coor[6], anchor='ne', font=('Arial',15), fill='black')
                ref.create_text(10,70,text='Start Here', anchor='sw', tag='start', font=('Arial',12), fill='deep sky blue')
                ref.create_text(10,75,text='End Here', anchor='nw', tag='end',font=('Arial',12), fill='deep sky blue')
                ref.create_text(170,75,text='more', anchor='nw', tag='info',font=('Tahoma',12), fill='red')
                ref.pack()
                ref.tag_bind('start', '<Button-1>', partial(set_start, coor[4]))
                ref.tag_bind('end', '<Button-1>', partial(set_end, coor[4]))
                ref.tag_bind('info', '<Button-1>', partial(open_browser, coor[5]))
                ref.tag_bind('start', '<Enter>', lambda e:ref.config(cursor='hand2'))
                ref.tag_bind('start', '<Leave>', lambda e: ref.config(cursor=''))
                ref.tag_bind('end', '<Enter>', lambda e:ref.config(cursor='hand2'))
                ref.tag_bind('end', '<Leave>', lambda e: ref.config(cursor=''))
                ref.tag_bind('info', '<Enter>', lambda e:ref.config(cursor='hand2'))
                ref.tag_bind('info', '<Leave>', lambda e: ref.config(cursor=''))
                click_ref.append(coor[4])
                break
            else:
                for t in click_ref:
                    canvas.delete(t)
                click_ref=list()

        #print ("(%d, %d)" % (cx,cy))
    #mouseclick event
    canvas.bind("<ButtonPress-1>",show_information)

direct=tk.IntVar()
html = tk.IntVar()
checkbox_dir = tk.Checkbutton(window, text='show directions',variable=direct
                                ,font=('Arial',13),activeforeground='deep sky blue')

checkbox_map = tk.Checkbutton(window, text='show map',variable=html
                                ,font=('Arial',13),activeforeground='medium violet red')

if check_internet():
    checkbox_dir.place(x=300, y=0, anchor='nw')
    checkbox_map.place(x=300, y=27, anchor='nw')
map_img=tk.Button(window, text='network map', font=('Arial', 13), command=network_map).place(x=220, y=60, anchor='nw')

insert_button = tk.Button(window, text='search', bg='deep sky blue', font=('Arial',13),
                          fg='white', command=enter, width=9)
insert_button.place(x=110, y=60)

clear_button = tk.Button(window, text='clear',command=clear, width=9,
                          bg='lavender', font=('Arial',13))
clear_button.place(x=10,y=60)

switch_button = tk.Button(window,image=img, width=40, height=40, command=switch, anchor='nw')
switch_button.place(x=230, y=5)


window.mainloop()
if times == 0:
    with open(current_path +'times.txt', 'w+') as fin:
        encoded_times = base64.b64encode(str(times).encode('UTF-8'))
        fin.write(encoded_times.decode('UTF-8')+'\n')
        encoded_key=base64.b64encode('None'.encode("UTF-8"))
        fin.write(encoded_key.decode('UTF-8'))
else:
    with open(current_path +'times.txt', 'w+') as fin:
        encoded_times = base64.b64encode(str(times).encode('UTF-8'))
        fin.write(encoded_times.decode('UTF-8')+'\n')
        encoded_key=base64.b64encode(default_key.encode("UTF-8"))
        fin.write(encoded_key.decode('UTF-8'))


