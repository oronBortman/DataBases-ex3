from collections import defaultdict, deque

""" -------------------------------------------------------------------
-------------------------- Class Decelerations ------------------------
------------------------------------------------------------------- """


# Class to represent a transaction
class Transaction:
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


""" -------------------------------------------------------------------
------------------------------ Graph Functions ------------------------
------------------------------------------------------------------- """


def build_precedence_graph(elem_list, g):
    index = 0
    for e in elem_list:
        check_for_vert_and_add_to_graph(e, elem_list, index + 1, g)
        index = index + 1


def check_for_vert_and_add_to_graph(source_elem, tran_list, index_to_look_from, g):
    tran_list = tran_list[index_to_look_from:]
    for dest_elem in tran_list:
        if source_elem.trans_act == 'R' and dest_elem.trans_act == 'W' or dest_elem.trans_act == 'W':
            if source_elem.trans_scheme == dest_elem.trans_scheme and source_elem.trans_num != dest_elem.trans_num:
                g.add_edge(source_elem.trans_num, dest_elem.trans_num)  # Adding edge
                g.add_vert(source_elem.trans_num)  # add source transaction as vert
                g.add_vert(dest_elem.trans_num)  # add destination transaction as vert


""" -------------------------------------------------------------------
---------------------- Topological Order Functions --------------------
------------------------------------------------------------------- """


def print_trans_by_queue_state(u, queue):
    if len(queue) == 0:
        print("T{0}".format(u), end='')
    else:
        print("T{0}->".format(u), end='')


def check_if_there_is_cycle(g, in_degree):
    for v in g.V:
        if in_degree[v] != 0:
            print("No")
            return


def init_in_degree_by_vertices(g, in_degree):
    for v in g.V:
        in_degree[v] = 0


def update_in_degree_by_edges(g, in_degree):
    for s_vert, d_vert_list in g.graph.items():
        for d_vert in d_vert_list:
            in_degree[d_vert] = in_degree[d_vert] + 1


def add_to_queue_vertices_with_zero_in_degree(g, in_degree, queue):
    for v in g.V:
        add_to_queue_vert_if_with_zero_in_degree(v, in_degree, queue)


def add_to_queue_vert_if_with_zero_in_degree(v, in_degree, queue):
    if in_degree[v] == 0:
        queue.append(v)


def main_loop_of_topological_sort(g, in_degree, queue):
    while len(queue) != 0:
        u = queue.pop()
        for v in g.graph[u]:
            in_degree[v] = in_degree[v] - 1
            add_to_queue_vert_if_with_zero_in_degree(v, in_degree, queue)
        print_trans_by_queue_state(u, queue)


def topological_sort(g):
    queue = deque([])
    in_degree = {}

    # INIT
    init_in_degree_by_vertices(g, in_degree)
    update_in_degree_by_edges(g, in_degree)
    add_to_queue_vertices_with_zero_in_degree(g, in_degree, queue)

    # Main loop
    main_loop_of_topological_sort(g, in_degree, queue)

    # Check all nodes reached
    check_if_there_is_cycle(g, in_degree)


""" -------------------------------------------------------------------
--------------------------------- MAIN --------------------------------
------------------------------------------------------------------- """

'''
Algorithm:

1. Create a list of transactions elements by splitting the transactions string 
   into transaction elements with ';' as a separator.

2. Build precedence graph:

    2.1 For every transaction in the list:

        2.1.1 if it's action is read, check if there is transaction in list after him with the action write, 
              different transaction number and same Table.
    
        2.1.2 If it's action is write, check if there is transaction in list after him with action write/read,
              different transaction number and same Table
    
        2.1.3 If 2.1.1 or 2.1.2 applies:
              2.1.3.1 If the source and dest transaction vertices doesnt exist in the precedence graph,
                      create them.
              2.1.3.2 Add the edge (source transaction vert, dest transaction vert) to the precedence graph.
    
3. Run topological sort algorithm and print 'No' if there is cycle.
   If there is no cycle, print the topological order.
'''

# Get input of transactions and processes it
transactions_str = input("Enter transactions: ")
transaction_str_list = transactions_str.split(";")
transaction_list = []
for t in transaction_str_list:
    transaction_list.append(Transaction(t))

# Runs the algorithm
graph = Graph()
build_precedence_graph(transaction_list, graph)
topological_sort(graph)
