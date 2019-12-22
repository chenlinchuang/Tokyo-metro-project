import tkinter as tk
import time
import datetime
import cv2
from PIL import Image, ImageTk
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
data = dict()
station_dict = dict()
station = list()
with open('lines.csv','r') as fin:
    for line in fin:
        line.strip()
        temp = line.split(';')
        data[temp[0]] = [int(x) for x in temp[3:]]
        station_nodes=list()
        station_dict[temp[0]] = list()
        for i in range(int(temp[1]),int(temp[2])+1):
            station_nodes.append(Node('%s%02d' % (temp[0], i)))
        station_dict[temp[0]].extend(station_nodes)
        #station.extend(station_nodes)

for value in station_dict.values():
    station += value

#add nodes of all stations
for i in range(len(station)):
    station[i] = station[i]
metro_graph = Graph(station)

for key,value in station_dict.items():
    for i in range(1,len(value)):
        metro_graph.connect_node(value[i-1], value[i], data[key][i-1])

with open('transitions.csv', 'r') as fin2:
    for line in fin2:
        temp = line.strip().split(';')
        metro_graph.connect_node(station_dict[temp[0]][int(temp[1])-1 if temp[0] != 'Mb' else int(temp[1])-3],
                                 station_dict[temp[2]][int(temp[3])-1 if temp[2] != 'Mb' else int(temp[3])-3],
                                 int(temp[4]))
        


#get the start station and end station
'''
initial = tk.Tk()
initial.configure(background='white')
initial.title('Tokyo_metro_app')
initial.attributes("-fullscreen", True)
op = Image.open('icon1.png')
op = ImageTk.PhotoImage(op)
c = tk.Canvas(initial, width=initial.winfo_screenwidth(), height=initial.winfo_screenheight(), bg='white')
c.create_text(initial.winfo_screenwidth()/2, initial.winfo_screenheight()/2+100, text='Tokyo Metro', anchor='n', font=('Arial', 20))
c.create_image(initial.winfo_screenwidth()/2, initial.winfo_screenheight()/2+100, anchor='s', image=op)
c.place(x=0, y=0)
initial.after(5000, lambda: initial.destroy()) # Destroy the widget after 30 seconds
initial.mainloop()
'''
root = tk.Tk()
root.configure(background='white')
# Create a frame
app = tk.Frame(root, bg="white")
app.place(x=root.winfo_screenwidth()/2, y=root.winfo_screenheight()/2, anchor='center')
# Create a label in the frame
lmain = tk.Label(app)
lmain.grid()

cap = cv2.VideoCapture('op.mp4')

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

window = tk.Tk()
window.tk.call('wm','iconphoto', window._w, tk.PhotoImage(file='icon.png'))
window.title('Tokyo_metro_app')
window.geometry('640x640')
tk.Label(window, text='From',fg='white', bg='steel blue',
         font=('Arial', 12), height=1, width=6).place(x=0, y=0)
tk.Label(window, text='To',fg='white', bg='medium violet red', 
         font=('Arial', 12), height=1, width=6).place(x=0, y=30)

svar = tk.StringVar()
svar.set('G01')
start_entry = tk.Entry(window, textvariable=svar)
start_entry.place(x=80,y=0)

evar = tk.StringVar()
evar.set('Mb05')
end_entry = tk.Entry(window, textvariable=evar)
end_entry.place(x=80,y=35)

#output=tk.StringVar()
#tk.Label(window, textvariable=output,font=('Arial', 12)).place(x=20,y=400)

start_time = tk.StringVar()
tk.Label(window, textvariable=start_time, font=('Arial', 12)).place(x=200, y=80)

end_time = tk.StringVar()
tk.Label(window, textvariable=end_time, font=('Arial', 12)).place(x=250, y=80)

walk = Image.open('walking.png')
walk = walk.resize((40,40), Image.ANTIALIAS)
walk = ImageTk.PhotoImage(walk)

img = Image.open('change.png')
img = img.resize((40,40), Image.ANTIALIAS)
img=ImageTk.PhotoImage(img)

color_dict = {'G': 'orange', 'M':'red','Mb':'red3','H':'silver', 'T':'skt blue', 'C':'green',
              'Y':'yellow', 'Z':'purple', 'N':'turquoise', 'F':'brown',
              'A':'maroon1', 'I':'blue', 'S':'forest green', 'E':'deep pink'}
relation_dict = {'G': 'Ginza Line', 'M':'Marunouchi Line','Mb':'Marunouchi Line Branch Line','H':'Hibiya Line', 'T':'Tōzai Line', 'C':'Chiyoda Line',
                'Y':'Yūrakuchō Line', 'Z':'Hanzōmon Line', 'N':'Namboku Line', 'F':'Fukutoshin Line',
                'A':'Asakusa Line', 'I':'Mita Line', 'S':'Shinjuku Line', 'E':'Oedo Line'}

class ScrollFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent) # create a frame (self)
        #place canvas on self
        self.canvas = tk.Canvas(self, borderwidth=0)
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
    def __init__(self, root, trans, trans_time):

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

def enter():
    back = tk.Label(window,width=640, height=2000)
    back.place(x=20,y=110)
    s_info = start_entry.get()
    e_info = end_entry.get()
    if s_info[1] == 'b':
        start = station_dict[s_info.strip()[0:2]][int(s_info.strip()[2:])-3]
    else:
        start = station_dict[s_info.strip()[0]][int(s_info.strip()[1:])-1]
    if e_info[1] == 'b':
        end = station_dict[e_info.strip()[0:2]][int(e_info.strip()[2:])-3]
    else:
        end = station_dict[e_info.strip()[0]][int(e_info.strip()[1:])-1]

    result = metro_graph.dijkstra(start, end)
    

    tot_time = result[0][0] + result[0][1]
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

    if len(trans) == 2:
        transf='No Transfer'
    elif len(trans) == 3:
        transf='Transfer: 1'
    else:
        transf='Transfers: %d' % ((len(trans)-2)/2)
    
    #t_var = tk.StringVar()
    #tk.Label(window, textvariable = t_var, font=('Arial', 12)).place(x=20,y=300)
    print(str([x.ref for x in trans]))

    # time
    cur_time = datetime.datetime.now()
    final_time=cur_time+datetime.timedelta(minutes=result[0][0]+result[0][1])
    start_time.set('%02d:%02d' % (cur_time.hour,  cur_time.minute))
    end_time.set('%02d:%02d' % (final_time.hour, final_time.minute))
    print(str([('total time: about %.2f min' % (weight+time), [n.ref for n in node]) for (weight, time, node) in metro_graph.dijkstra(start, end) if node[-1] == end]))

    top_canvas = tk.Canvas(window, width=400, height=68, bg='white')
    top_canvas.create_text(70,19,text=s_info,anchor='w',fill='black', font=('Arial', 12))
    top_canvas.create_text(70,50,text=e_info, anchor='w',fill='black', font=('Arial', 12))
    top_canvas.create_text(360,45, text=str(int(tot_time)),anchor='se',fill='black', font=('Arial', 25))
    top_canvas.create_text(365,43, text='min', anchor='sw', fill='black', font=('Arial', 15))
    top_canvas.create_text(395,45, text=transf, anchor='ne', fill='green', font=('Arial', 10))
    top_canvas.place(x=20,y=120)
    s_label = tk.Label(window, text='From', fg='white', bg='steel blue', height=1, width=6)
    s_label.place(x=30,y=130)
    e_label = tk.Label(window, text='To', fg='white', bg='medium violet red', height=1, width=6)
    e_label.place(x=30,y=160)
    
    Usage(window, trans, trans_time).place(x=20, y=200)

    '''
    count = 0
    start_is_trans = False
    if trans[0] == trans[1]:
        c = tk.Canvas(sub_window, width=400, height = 50)
        c.create_image(60,5, anchor='nw', image=walk)
        for t in range(5):
            c.create_rectangle(20,0+t*10,40,5+t*10, outline='black', fill='black')
        c.create_text(120, 25, anchor='w', text='Walk to %s platform' % (trans[2].ref), fill='grey', font=('Arial', 15))
        c.place(x=20,y=200)
        start_is_trans = True
        trans = trans[2:]

    
    
    for i in range(len(trans)//2):
        canvas= tk.Canvas(sub_window, width = 400, height=165, bg='white')
        canvas.create_rectangle(20,20,40,150,outline=color_dict[trans[count].ref[0]],fill=color_dict[trans[count].ref[0]])
        canvas.create_oval(17,7,43,33, outline=color_dict[trans[count].ref[0]], fill='white')
        canvas.create_oval(17,137,43,163, outline=color_dict[trans[count].ref[0]], fill='white')
        canvas.create_text(70,20, text=trans[count], fill='black',font=('Purisa', 17))
        canvas.create_text(75,150,text=trans[count+1], fill='black',font=('Purisa', 17))
        if start_is_trans:
            canvas.place(x=20, y=250+i*215)
        else:
            canvas.place(x=20, y=200+i*215)
        count += 2
        if i != (len(trans)//2)-1:
            interval = tk.Canvas(sub_window, width = 400, height = 50)
            interval.create_image(60,5, anchor='nw', image=walk)
            interval.create_text(120, 25, anchor='w', text='Walk to %s platform' % (trans[count].ref), fill='grey', font=('Arial', 15))
            for t in range(5):
                interval.create_rectangle(20,0+t*10,40,5+t*10, outline='black', fill='black')
            if start_is_trans:
                interval.place(x=20, y=415+i*215)
            else:
                interval.place(x=20, y=365+i*215)
            
    if trans[-1] == trans[-2]:
        c = tk.Canvas(sub_window, width=400, height = 200)
        if start_is_trans:
            c.place(x=20,y=465+(i-1)*215)
        else:
            c.place(x=20,y=415+(i-1)*215)'''
        

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
insert_button = tk.Button(window, text='search', bg='deep sky blue', font=('Arial',13),
                          fg='white', command=enter, width=9)
insert_button.place(x=110, y=60)

clear_button = tk.Button(window, text='clear', width=9, font=('Arial',13),
                          bg='lavender', command=clear)
clear_button.place(x=10,y=60)

switch_button = tk.Button(window,image=img, width=40, height=40, command=switch, anchor='nw')
switch_button.place(x=250, y=5)





window.mainloop()



