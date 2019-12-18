import tkinter as tk
import datetime

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
window = tk.Tk()
window.title('Tokyo_metro_app')
window.geometry('640x480')
tk.Label(window, text='start station name:', font=('Arial', 12)).place(x=90, y=0)
tk.Label(window, text='end station name:', font=('Arial', 12)).place(x=90, y=20)

svar = tk.StringVar()
svar.set('please enter start station')
start_entry = tk.Entry(window, textvariable=svar)
start_entry.pack()

evar = tk.StringVar()
evar.set('please enter end station')
end_entry = tk.Entry(window, textvariable=evar)
end_entry.pack()

output=tk.StringVar()
tk.Label(window, textvariable=output,font=('Arial', 12)).pack()

start_time = tk.StringVar()
tk.Label(window, textvariable=start_time, font=('Arial', 12)).pack()

end_time = tk.StringVar()
tk.Label(window, textvariable=end_time, font=('Arial', 12)).pack()

def enter():
    s_info = start_entry.get()
    e_info = end_entry.get()
    svar.set('')
    evar.set('')
    if s_info[1] == 'b':
        start = station_dict[s_info.strip()[0:2]][int(s_info.strip()[2:])-3]
    else:
        start = station_dict[s_info.strip()[0]][int(s_info.strip()[1:])-1]
    if e_info[1] == 'b':
        end = station_dict[e_info.strip()[0:2]][int(e_info.strip()[2:])-3]
    else:
        end = station_dict[e_info.strip()[0]][int(e_info.strip()[1:])-1]

    result = metro_graph.dijkstra(start, end)

    cur_time = str(datetime.datetime.now())
    cur_time = [float(t) for t in cur_time[cur_time.index(' '):].split(':')]
    start_time.set('%02d:%02d' % (cur_time[0], cur_time[1]))
    final_time = cur_time[:]
    final_time[1] += (result[0][0] + result[0][1])
    if final_time[1] >= 60:
        final_time[0] += divmod(final_time[1],60)[0]
        final_time[1] = divmod(final_time[1],60)[1]
    end_time.set('%02d:%02d' % (final_time[0], final_time[1]))
    output.set(str([('total time: about %.2f min' % (weight+time), [n.ref for n in node]) for (weight, time, node) in metro_graph.dijkstra(start, end) if node[-1] == end]))

b1 = tk.Button(window, text='insert point', width=10,
               height=2, command=enter)
b1.pack()
window.mainloop()



