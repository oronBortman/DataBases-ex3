from collections import defaultdict, deque


# Class to represent an element
class Element:
    def __init__(self, element_str):
        self.trans_num = element_str[1]
        self.trans_act = element_str[0]
        start_dest = element_str.find("(") + len("(")
        end_dest = element_str.find(")")
        self.trans_scheme = element_str[start_dest:end_dest]


# Class to represent a graph
class Graph:
    def __init__(self):
        self.graph = defaultdict(set)  # dictionary containing adjacency List
        self.V = set()  # verticals

    # function to add an edge to graph
    def add_edge(self, u, v):
        self.graph[u].add(v)

    def add_vert(self, v):
        self.V.add(v)


'''
Algorithm:
1. Split the string into elemnts with ';' as a seperator and add it to list
2. run over the list and for every elemnt:
    2.1 if it is read, check if there is element in list after him with write, different transaction number and same Table
    2.2 if it is write, check if there is clement in list after him with write/read, different transaction number and same Table
    if 2.1 or 2.2 applies then add the source transaction and dest transcation as vertices if they do not exist.
    After that, add the dest transaction vert in the list of the source trans vert.
'''


def check_for_vert_and_add_to_graph(source_elem, tran_list, index_to_look_from, g):
    tran_list = tran_list[index_to_look_from:]
    for dest_elem in tran_list:
        if source_elem.trans_act == 'R' and dest_elem.trans_act == 'W' or dest_elem.trans_act == 'W':
            if source_elem.trans_scheme == dest_elem.trans_scheme and source_elem.trans_num != dest_elem.trans_num:
                g.add_edge(source_elem.trans_num, dest_elem.trans_num) #Adding edge
                g.add_vert(source_elem.trans_num) # add source transaction as vert
                g.add_vert(dest_elem.trans_num) # add destination transaction as vert


def build_graph(elem_list, g):
    index = 0
    for e in elem_list:
        check_for_vert_and_add_to_graph(e, elem_list, index + 1, g)
        index = index + 1


def topological_sort(g):
    queue = deque([])
    in_degree = {}

    for v in g.V:
        in_degree[v] = 0

    for s_vert, d_vert_list in g.graph.items():
        for d_vert in d_vert_list:
            in_degree[d_vert] = in_degree[d_vert] + 1

    for v in g.V:
        if in_degree[v] == 0:
            queue.append(v)

    while len(queue) != 0:
        u = queue.pop()

        for v in g.graph[u]:
            in_degree[v] = in_degree[v] - 1
            if in_degree[v] == 0:
                queue.append(v)

        if len(queue) == 0:
            print("T{0}".format(u), end='')
        else:
            print("T{0}->".format(u), end='')

    for v in g.V:
        if in_degree[v] != 0:
            print("No")
            return


graph = Graph()
#transaction = "R2(A);R1(B);W2(A);R2(B);R3(A);W1(B);W3(A);W2(B)" # Bad
transaction = "R2ׂׂ(A);R1(B);W2(A);R3(A);W1(B);W3(A);R2(B);W2(B)" # Good
transaction_list = transaction.split(";")
element_list = []
for t in transaction_list:
    element_list.append(Element(t))
build_graph(element_list, graph)
topological_sort(graph)
