class BinaryTree:
    def __init__(self, node=[]):
        self.list_all_node = node

    def root(self):
        return self.list_all_node[0]

    def me(self, i):
        return self.list_all_node[i]
    
    def parent(self, i):
        if i == 0: 
            raise IndexError ('it is the root!')
        return self.list_all_node[(i-1)//2]

    def index_leftchild(self, i):
        return 2*i +1

    def left_children(self, i):
        if 2*i+1 >= len(self.list_all_node):
            raise IndexError ('it is the leaf')
        return self.list_all_node[self.index_leftchild(i)]
    
    def index_rightchild(self, i):
        return 2*i+2
    
    def right_children(self, i):
        if 2*i+2 >= len(self.list_all_node):
            raise IndexError ('it is the leaf')
        return self.list_all_node[self.index_rightchild(i)]
    
    def size(self):
        return len(self.list_all_node)

class Heap(BinaryTree):
    def __init__(self, node):
        super().__init__(node)
        self.min_heap()

    def min_heap_subtree(self, i):
        if self.index_rightchild(i) < self.size:
            if self.me(i) > self.left_children(i):
                self.list_all_node[i], self.list_all_node[self.index_leftchild(i)] =  self.list_all_node[self.index_leftchild(i)], self.list_all_node[i]
            if self.me(i) > self.right_children(i):
                self.list_all_node[i], self.list_all_node[self.index_rightchild(i)] = self.list_all_node[self.index_rightchild(i)], self.list_all_node[i]

    def min_heap(self):
        for i in range(self.size, -1, -1):
            self.min_heap_subtree(i)