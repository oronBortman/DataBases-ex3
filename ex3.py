from collections import defaultdict


# Class to represent an element
class Element:
    def __init__(self, element_str):
        self.trans_num = element_str[1]
        self.trans_act = element_str[0]
        start_dest = element_str.find("(") + len("(")
        end_dest = element_str.find(")")
        self.tran_scheme = element_str[start_dest:end_dest]


# Class to represent a graph
class Graph:
    def __init__(self):
        self.graph = defaultdict(list)  # dictionary containing adjacency List
        self.V = None  # No. of vertices

    # function to add an edge to graph
    def add_edge(self, u, v):
        self.graph[u].append(v)




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
            if source_elem.tans_scheme == dest_elem.tans_scheme and source_elem.trans_num != dest_elem.tran_num_dest:
                g.add_edge(source_elem.trans_num, dest_elem.tran_num_dest)


def build_graph(elem_list, g):
    index = 0
    for e in elem_list:
        check_for_vert_and_add_to_graph(e, elem_list, index + 1, g)
        index = index + 1


#def topological_sort(g):


graph = Graph()
transaction = "R2(A);R1(B);W2(A);R2(B);R3(A);W1(B);W3(A);W2(B)"
transaction_list = transaction.split(";")
element_list = []
for t in transaction_list:
    element_list.add(Element(t))
build_graph(element_list, graph)
