import osmium


class CounterHandler(osmium.SimpleHandler):
    node_list = []
    def __init__(self):
        osmium.SimpleHandler.__init__(self)
        self.num_nodes = 0
        self.way_nodes = 0

    def node(self, n):
        self.num_nodes += 1
        if self.num_nodes == 1:
            print(n.tags['ref'])

        #print(type(n))

    def way(self, x):
        self.way_nodes += 1
        CounterHandler.node_list.append(x)
        '''if self.way_nodes == 1:
            print(CounterHandler.node_list)
        #print(type(x))'''
    
if __name__ == '__main__':

    h = CounterHandler()

    h.apply_file("export.osm")
    print(h.node_list[0].id)
    print("Number of nodes: %d" % h.num_nodes)