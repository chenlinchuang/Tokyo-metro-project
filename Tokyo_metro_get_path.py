class Node:
  
    def __init__(self, data, indexloc = None):
        self.data = data
        self.index = indexloc

    def __str__(self):
        return self.data
        
       
class Graph:

    @classmethod
    def create_from_nodes(self, nodes):
        return Graph(len(nodes), len(nodes), nodes)

  
    def __init__(self, row, col, nodes = None):
        # set up an adjacency matrix
        self.adj_mat = [[0] * col for _ in range(row)]
        self.nodes = nodes
        for i in range(len(self.nodes)):
            self.nodes[i].index = i

    # Conncects from node1 to node2
    # Note row is source, column is destination
    # Updated to allow weighted edges (supporting dijkstra's alg)
    def connect_dir(self, node1, node2, weight = 1):
        node1, node2 = self.get_index_from_node(node1), self.get_index_from_node(node2)
        self.adj_mat[node1][node2] = weight
  
    # Optional weight argument to support dijkstra's alg
    def connect(self, node1, node2, weight = 1):
        self.connect_dir(node1, node2, weight)
        self.connect_dir(node2, node1, weight)

    # Get node row, map non-zero items to their node in the self.nodes array
    # Select any non-zero elements, leaving you with an array of nodes
    # which are connections_to (for a directed graph)
    # Return value: array of tuples (node, weight)
    def connections_from(self, node):
        node = self.get_index_from_node(node)
        return [(self.nodes[col_num], self.adj_mat[node][col_num]) for col_num in range(len(self.adj_mat[node])) if self.adj_mat[node][col_num] != 0]

    # Map matrix to column of node
    # Map any non-zero elements to the node at that row index
    # Select only non-zero elements
    # Note for a non-directed graph, you can use connections_to OR
    # connections_from
    # Return value: array of tuples (node, weight)
    def connections_to(self, node):
        node = self.get_index_from_node(node)
        column = [row[node] for row in self.adj_mat]
        return [(self.nodes[row_num], column[row_num]) for row_num in range(len(column)) if column[row_num] != 0]
     
  
    def print_adj_mat(self):
        for row in self.adj_mat:
            print(row)
  
    def node(self, index):
        return self.nodes[index]
    
  
    def remove_conn(self, node1, node2):
        self.remove_conn_dir(node1, node2)
        self.remove_conn_dir(node2, node1)
   
    # Remove connection in a directed manner (nod1 to node2)
    # Can accept index number OR node object
    def remove_conn_dir(self, node1, node2):
        node1, node2 = self.get_index_from_node(node1), self.get_index_from_node(node2)
        self.adj_mat[node1][node2] = 0   
  
    # Can go from node 1 to node 2?
    def can_traverse_dir(self, node1, node2):
        node1, node2 = self.get_index_from_node(node1), self.get_index_from_node(node2)
        return self.adj_mat[node1][node2] != 0  
  
    def has_conn(self, node1, node2):
        return self.can_traverse_dir(node1, node2) or self.can_traverse_dir(node2, node1)
  
    def add_node(self,node):
        self.nodes.append(node)
        node.index = len(self.nodes) - 1
        for row in self.adj_mat:
            row.append(0)     
        self.adj_mat.append([0] * (len(self.adj_mat) + 1))

    # Get the weight associated with travelling from n1
    # to n2. Can accept index numbers OR node objects
    def get_weight(self, n1, n2):
        node1, node2 = self.get_index_from_node(n1), self.get_index_from_node(n2)
        return self.adj_mat[node1][node2]
  
    # Allows either node OR node indices to be passed into 
    def get_index_from_node(self, node):
        if not isinstance(node, Node) and not isinstance(node, int):
            raise ValueError("node must be an integer or a Node object")
        if isinstance(node, int):
            return node
        else:
            return node.index
    def dijkstra(self, node, end):
        # Get index of node (or maintain int passed in)
        nodenum = self.get_index_from_node(node)
        # Make an array keeping track of distance from node to any node
        # in self.nodes. Initialize to infinity for all nodes but the 
        # starting node, keep track of "path" which relates to distance.
        # Index 0 = distance, index 1 = node hops
        dist = [None] * len(self.nodes)
        for i in range(len(dist)):
            dist[i] = [float("inf")]
            dist[i].append([self.nodes[nodenum]])
        
        dist[nodenum][0] = 0
        # Queue of all nodes in the graph
        # Note the integers in the queue correspond to indices of node
        # locations in the self.nodes array
        queue = [i for i in range(len(self.nodes))]
        # Set of numbers seen so far
        seen = set()
        while len(queue) > 0:
            # Get node in queue that has not yet been seen
            # that has smallest distance to starting node
            min_dist = float("inf")
            min_node = None
            for n in queue: 
                if dist[n][0] < min_dist and n not in seen:
                    min_dist = dist[n][0]
                    min_node = n
            
            # Add min distance node to seen, remove from queue
            queue.remove(min_node)
            seen.add(min_node)
            # Get all next hops 
            connections = self.connections_from(min_node)
            # For each connection, update its path and total distance from 
            # starting node if the total distance is less than the current distance
            # in dist array
            for (node, weight) in connections: 
                tot_dist = weight + min_dist
                if tot_dist < dist[node.index][0]:
                    dist[node.index][0] = tot_dist
                    dist[node.index][1] = list(dist[min_node][1])
                    dist[node.index][1].append(node)
            if end.index in seen: return dist
        return dist

# read the information of each metro line
data = list()
station = list()
with open('lines.csv','r') as fin:
    for line in fin:
      line.strip()
      temp = line.split(';')
      data.append(temp[3:])
      station_nodes=list()
      for i in range(int(temp[1]),int(temp[2])+1):
          station_nodes.append('%s%02d' % (temp[0], i))
      station.append(station_nodes)

#read the information about transfer station
trans_data = []
def index_2D(list_2d, x):
    for i, li in enumerate(list_2d):
        if x in li:
            return(i,li.index(x))
with open('transitions.csv', 'r') as fin2:
    for line in fin2:
        temp = line.strip().split(';')
        trans_data.append([index_2D(station,temp[0]+temp[1]),index_2D(station,temp[2]+temp[3]),temp[4]])

#get the start station and end station
start = index_2D(station, input('start station: '))
end = index_2D(station, input('end station: '))

#add nodes of all stations
for i in range(len(station)):
    for j in range(len(station[i])):
        station[i][j] = Node(station[i][j])

#setup the adjacent matrix
station_ravel = list()
for s in station:
    station_ravel += s
metro_graph = Graph.create_from_nodes(station_ravel)

#setup all connections between stations
for i in range(len(data)):
    for j in range(len(data[i])):
        metro_graph.connect(station[i][j], station[i][j+1], int(data[i][j]))

#setup transfer time between two platform in each transfer station
for trans in trans_data:
    metro_graph.connect(station[trans[0][0]][trans[0][1]], station[trans[1][0]][trans[1][1]], int(trans[2]))

s = station[start[0]][start[1]]
e = station[end[0]][end[1]]

#get the result
print([('total time: about %d min' % weight, [n.data for n in node]) for (weight, node) in metro_graph.dijkstra(s, e) if node[-1] == e])