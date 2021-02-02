from enum import Enum
import random

""" -------------------------------------------------------------------
------------------------------ CONSTANTS ------------------------------
------------------------------------------------------------------- """


input_file = "statistics.txt"
SEC2_LQP_N = 4
SEC2_ITR_N = 10


main_menu = '''
* * * MAIN MENU * * *
1. Part 1: Apply Rule
2. Part 2: 10 iterations of random rules
3. Part 3: Size Estimation (4 random LQP received from part 2)
4. Part 3: Size Estimation (current LQP only)
5. Enter new query
6. Exit

Enter an option: '''

part_one_menu = '''
--- SECTION 1 MENU ---
1. Rule 4: SIGMA_(P1 AND P2) (R) = SIGMA_P1 ( SIGMA_P2 (R) )
2. Rule 4a: SIGMA_P1 ( SIGMA_P2 (R) ) = SIGMA_P2 (SIGMA_P1 (R) )
3. Rule 5a: PI_X [ SIGMA_P (R) ] = SIGMA_P [ PI_X (R) ]  // (P cols subset of X, X subset cols of R)
4. Rule 6: SIGMA_P ( R NJOIN\CARTESIAN S) = [SIGMA_P (R) ] NJOIN\CARTESIAN S  // P cols subset of R
5. Rule 6a: SIGMA_Q ( R NJOIN\CARTESIAN S) = R NJOIN\CARTESIAN [SIGMA_Q (S) ]  // Q cols subset of S
6. Rule 11b: SIGMA_P (R X S) = R TJOIN_P S  // Only if P is equality on all shared cols, creating NJOIN instead
7. Back

Enter an option: '''


class Tables(Enum):
    R = 1
    S = 2
    ALL = 3


class Rules(Enum):
    FOUR = 1
    FOUR_A = 2
    FIVE_A = 3
    SIX = 4
    SIX_A = 5
    ELEVEN_B = 6


class Cols(Enum):
    A = 1
    B = 2
    C = 3
    D = 4
    E = 5
    F = 6
    H = 7


class Operators(Enum):
    CARTESIAN = 1
    SIGMA = 2
    PI = 3
    NJOIN = 4
    TJOIN = 5
    TABLE = 6


class FunctionBorders(Enum):
    Start = 1
    End = 2


""" -------------------------------------------------------------------
--------------------------------- CLASSES -----------------------------
------------------------------------------------------------------- """


class TreeNode:
    def __init__(self, operator_type):
        self.operator_type = operator_type
        self.predicate = None
        self.tableName = None  # relevant when working with the original tables (R, S)
        self.colList = []
        self.rows = 0
        self.inputSchemeOne = None
        self.inputSchemeTwo = None

    def dup(self):
        """ Creates a duplicate of the node, without the 'next' links"""
        new_node = TreeNode(self.operator_type)
        new_node.predicate = self.predicate
        new_node.tableName = self.tableName
        new_node.colList = self.colList.copy()
        new_node.inputSchemeOne = None
        new_node.inputSchemeTwo = None

        return new_node

    def print(self):
        print_op_data(self)


class SchemeData:
    def __init__(self, scheme_name="Scheme1"):
        self.name = scheme_name
        self.N = 0  # number of rows in scheme
        self.rowSize = None # Row size
        self.colList = []  # list of ColData items

    def print(self):
        row_num = self.N
        row_num = str(row_num)
        print("n_" + self.name + " = " + row_num + ", " + "R_" + self.name + " = " + str(self.rowSize))


class ColData:
    def __init__(self):
        self.dataType = None  # INT, STRING, CHAR
        self.name = None  # R.D, R.E, S.F, etc
        self.V = 0

    def data_type_size(self):
        size = 4
        if self.dataType == "INTEGER":
            size = 4
        return size


class AtomicFormula:
    def __init__(self, atomic_formula_string):
        formula_elements = AtomicFormula.analyze_atomic_formula(atomic_formula_string)
        self.leftOperand = formula_elements[0]  # R.B, S.F, etc.
        self.rightOperand = formula_elements[1]  # Either col (e.g. S.G) or number (e.g. 5)
        self.operator = formula_elements[2]

    def analyze_atomic_formula(atomic_formula_string):
        operator_ind = atomic_formula_string.find("=")  # Right now we only support this operator
        ind_after_operator = operator_ind + 1  # Likewise
        left_operand = atomic_formula_string[:operator_ind].strip()
        right_operand = atomic_formula_string[ind_after_operator:].strip()
        return left_operand, right_operand, "="


""" -------------------------------------------------------------------
----------------------- TREE AND SCHEME METHODS -----------------------
------------------------------------------------------------------- """


def create_pi_node(string):
    col_list = get_col_list_from_predicate(string)
    node = TreeNode(Operators.PI)
    node.operator_type = Operators.PI
    node.colList = col_list
    return node


def create_sigma_node(string):
    node = TreeNode(Operators.SIGMA)
    node.operator_type = Operators.SIGMA
    node.predicate = string
    return node


def create_original_table_node(table_name):
    node = TreeNode(Operators.TABLE)
    node.operator_type = Operators.TABLE
    node.tableName = table_name.strip()
    if node.tableName == "R":
        node.colList = ["R.A", "R.B", "R.C", "R.D", "R.E"]
    else:
        node.colList = ["S.D", "S.E", "S.F", "S.H", "S.I"]
    return node


def create_njoin_node():
    node = TreeNode(Operators.NJOIN)
    node.operator_type = Operators.NJOIN
    return node


def create_cartesian_node():
    node = TreeNode(Operators.CARTESIAN)
    node.operator_type = Operators.CARTESIAN
    node.inputSchemeOne = None
    node.inputSchemeTwo = None
    return node


def print_op_data(node):
    if node is None:
        return
    if node.operator_type == Operators.TABLE:
        print(node.tableName, end="")
    elif node.operator_type == Operators.CARTESIAN:
        print("CARTESIAN", end="")
    elif node.operator_type == Operators.NJOIN:
        print("NJOIN", end="")
    else:
        op_name = None
        string = None
        if node.operator_type == Operators.SIGMA:
            op_name = "SIGMA"
            string = node.predicate
        if node.operator_type == Operators.PI:
            op_name = "PI"
            string = ", ".join(node.colList)
        if node.operator_type == Operators.TJOIN:
            op_name = "TJOIN"
            string = node.predicate
        print(op_name + "[" + string + "]", end="")


def print_expression_tree(node):
    if node is None:
        return
    print_op_data(node)
    if node.inputSchemeOne is not None:
        print("(", end="")
        print_expression_tree(node.inputSchemeOne)
        if node.inputSchemeTwo is not None:
            print(", ", end="")
            print_expression_tree(node.inputSchemeTwo)
        print(")", end="")


""" -------------------------------------------------------------------
---------------------- PARSE ANALYSIS FUNCTIONS -----------------------
------------------------------------------------------------------- """


def cond_has_outer_parenthesis(string):
    stripped_string = string.strip()
    return stripped_string[0] == '(' and stripped_string[-1] == ')'


def find_operator_ind(string, location_to_look_from):
    and_ind = string.find("AND", location_to_look_from)
    or_ind = string.find("OR", location_to_look_from)
    if and_ind < 0 and or_ind < 0:  # no AND or OR operators in string from given index
        return -1
    else:
        # find first of the two operators:
        if and_ind < or_ind:
            if and_ind >= 0:
                first_operator_ind = and_ind
            else:
                first_operator_ind = or_ind
        else:
            if or_ind >= 0:
                first_operator_ind = or_ind
            else:
                first_operator_ind = and_ind
        return first_operator_ind


def find_ind_after_operator(string, operator_ind):
    if string[operator_ind] == 'A':
        ind_after_operator = operator_ind + 3
    else:  # operator is OR
        ind_after_operator = operator_ind + 2
    return ind_after_operator


def check_simple_cond(string):
    if "(" in string or ")" in string:
        return False
    else:
        return True


def find_main_and_op(string):
    num_of_left_stripped_spaces = 0
    num_of_outer_paren = 0
    if has_wrapper_parentheses(string):
        string, num_of_outer_paren, num_of_left_stripped_spaces = strip_wrapper_parentheses(string)
    location_to_look_from = 0
    last_ind = len(string) - 1
    while location_to_look_from <= last_ind:
        and_ind = string.find("AND", location_to_look_from)
        if and_ind < 0:  # no operator found from given location
            return -1
        ind_after_operator = and_ind + 3
        string_left_of_operator = string[:and_ind]
        string_right_of_operator = string[ind_after_operator:]
        if is_balanced_parentheses(string_left_of_operator) and is_balanced_parentheses(string_right_of_operator):
            return and_ind + num_of_outer_paren + num_of_left_stripped_spaces
        else:
            location_to_look_from = ind_after_operator


""" -------------------------------------------------------------------
--------------------------- RULE FUNCTIONS ----------------------------
------------------------------------------------------------------- """


def activate_rule_4(node):
    """
    SIGMA_(P1 AND P2) (R) = SIGMA_P1 ( SIGMA_P2 (R) )
    """
    if node is None:
        return node, False
    if node.operator_type == Operators.SIGMA:
        operator_ind = find_main_and_op(node.predicate)
        if operator_ind != -1:
            ind_after_operator = operator_ind + 3
            string_left_of_operator = node.predicate[:operator_ind].strip()
            string_right_of_operator = node.predicate[ind_after_operator:].strip()
            string_left_of_operator, dummy_var, dummy_var = strip_wrapper_parentheses(string_left_of_operator)
            string_right_of_operator, dummy_var, dummy_var = strip_wrapper_parentheses(string_right_of_operator)
            new_node = create_sigma_node(string_right_of_operator)
            node.predicate = string_left_of_operator
            new_node.inputSchemeOne = node.inputSchemeOne
            node.inputSchemeOne = new_node
            return node, True
    node.inputSchemeOne, rule_succeeded = activate_rule_4(node.inputSchemeOne)
    if rule_succeeded:
        return node, True
    node.inputSchemeTwo, rule_succeeded = activate_rule_4(node.inputSchemeTwo)
    return node, rule_succeeded


def activate_rule_4a(node):
    """
    SIGMA_P1 ( SIGMA_P2 (R) ) = SIGMA_P2 (SIGMA_P1 (R) )
    """
    if node is None:
        return node, False
    if node.operator_type == Operators.SIGMA:
        next_node = node.inputSchemeOne
        if next_node is not None and next_node.operator_type == Operators.SIGMA:
            node.inputSchemeOne = next_node.inputSchemeOne
            next_node.inputSchemeOne = node
            return next_node, True
    node.inputSchemeOne, rule_succeeded = activate_rule_4a(node.inputSchemeOne)
    if rule_succeeded:
        return node, True
    node.inputSchemeTwo, rule_succeeded = activate_rule_4a(node.inputSchemeTwo)
    return node, rule_succeeded


def activate_rule_5a(node):
    """
     PI_X [ SIGMA_P (R) ] = SIGMA_P [ PI_X (R) ]
     Where X is attributes subset of R
     And P is attributes subset of X

     SIGMA -> SIGMA -> PI -> SIGMA -> CARTESIAN

    """
    if node is None:
        return node, False
    if node.operator_type == Operators.PI:
        next_node = node.inputSchemeOne
        if next_node is not None and next_node.operator_type == Operators.SIGMA:
            sigma_col_list = get_col_list_from_predicate(next_node.predicate)
            if columns_within_scheme(node.colList, next_node.inputSchemeOne) and \
                    is_subset_columns(sigma_col_list, node.colList):
                node.inputSchemeOne = next_node.inputSchemeOne
                next_node.inputSchemeOne = node
                return next_node, True
    node.inputSchemeOne, rule_succeeded = activate_rule_5a(node.inputSchemeOne)
    if rule_succeeded:
        return node, True
    node.inputSchemeTwo, rule_succeeded = activate_rule_5a(node.inputSchemeTwo)
    return node, rule_succeeded


def get_col_list_from_scheme(node):
    if node is None:
        return None
    if node.operator_type is Operators.TABLE:
        col_list = node.colList.copy()
        return col_list
    col_list_scheme_one = get_col_list_from_scheme(node.inputSchemeOne)
    col_list_scheme_two = get_col_list_from_scheme(node.inputSchemeTwo)
    if col_list_scheme_one is None:
        return col_list_scheme_two
    if col_list_scheme_two is None:
        return col_list_scheme_one
    return col_list_scheme_one + col_list_scheme_two


def find_first_two_operators(r_ind, s_ind):
    if r_ind < s_ind:
        if r_ind >= 0:
            first_col_ind = r_ind
        else:
            first_col_ind = s_ind
    else:
        if s_ind >= 0:
            first_col_ind = s_ind
        else:
            first_col_ind = r_ind
    return first_col_ind


def get_col_list_from_predicate(predicate):
    col_list = []
    location_to_look_from = 0
    last_ind = len(predicate) - 1
    while location_to_look_from <= last_ind:
        r_ind = predicate.find("R.", location_to_look_from)
        s_ind = predicate.find("S.", location_to_look_from)
        if r_ind < 0 and s_ind < 0:  # no columns left from where we're looking
            location_to_look_from = last_ind + 1
        else:
            first_col_ind = find_first_two_operators(r_ind, s_ind)
            col = predicate[first_col_ind:first_col_ind + 3]
            col_list.append(col)
            location_to_look_from = first_col_ind + 1
    return col_list


def is_subset_columns(col_list_to_check, target_col_list):
    for col in col_list_to_check:
        found_in_target_list = False
        for col_in_target_list in target_col_list:
            if col.strip() == col_in_target_list.strip():
                found_in_target_list = True
        if not found_in_target_list:
            return False
    return True


def columns_within_scheme(col_list, scheme_node):
    scheme_columns = get_col_list_from_scheme(scheme_node)
    return is_subset_columns(col_list, scheme_columns)


def rule6_update_node_connections(sigma_node, njoin_cartesian_node, rule):
    if rule == Rules.SIX:
        sigma_node.inputSchemeOne = njoin_cartesian_node.inputSchemeOne
        njoin_cartesian_node.inputSchemeOne = sigma_node
    elif rule == Rules.SIX_A:
        sigma_node.inputSchemeOne = njoin_cartesian_node.inputSchemeTwo
        njoin_cartesian_node.inputSchemeTwo = sigma_node
    return njoin_cartesian_node


def rule6_are_cols_within_scheme(col_list, next_node, rule):
    if rule == Rules.SIX:
        scheme = next_node.inputSchemeOne
    elif rule == Rules.SIX_A:
        scheme = next_node.inputSchemeTwo
    return columns_within_scheme(col_list, scheme)


def activate_rule_6_united(node, rule):
    """
    6: SIGMA_P ( R NJOIN\CARTESIAN S) = [SIGMA_P (R) ] NJOIN\CARTESIAN S
        where P is subset of attributes \ columns of R

    6a: SIGMA_Q ( R NJOIN\CARTESIAN S) = R NJOIN\CARTESIAN [SIGMA_Q (S) ]
        where Q is subset of attributes \ columns of S

    1. Find sigma
    2. See if next node is NJOIN or CARTESIAN
    3. If 1 and 2,
        for rule 6: see if predicate in sigma is only on columns of the LEFT scheme in the NJOIN or CARTESIAN
        for rul 6a: see if predicate in sigma is only on columns of the RIGHT scheme in the NJOIN or CARTESIAN
    """
    if node is None:
        return node, False
    if node.operator_type == Operators.SIGMA:
        next_node = node.inputSchemeOne
        if next_node is not None and \
                (next_node.operator_type == Operators.NJOIN or next_node.operator_type == Operators.CARTESIAN):
            col_list = get_col_list_from_predicate(node.predicate)
            if rule6_are_cols_within_scheme(col_list, next_node, rule):
                next_node = rule6_update_node_connections(node, next_node, rule)
                return next_node, True
    node.inputSchemeOne, rule_succeeded = activate_rule_6_united(node.inputSchemeOne, rule)
    if rule_succeeded:
        return node, True
    node.inputSchemeTwo, rule_succeeded = activate_rule_6_united(node.inputSchemeTwo, rule)
    return node, rule_succeeded


def check_table_with_col_exist(str1, predicate, col):
    r_operand_ind = predicate.find(str1)
    if r_operand_ind < 0 or predicate[r_operand_ind + 2] != col:
        return False
    else:
        return True


def predicate_after_equal(str1, predicate, equality_ind):
    return str1 in (predicate[equality_ind - 1], predicate[equality_ind + 1])


def predicate_demands_equality_on_col(predicate, col):
    predicate = predicate.strip()
    if predicate.find("AND") >= 0:
        return False
    equality_ind = predicate.find("=")
    if equality_ind < 1:
        return False
    else:
        predicate_is_smaller = predicate_after_equal("<", predicate, equality_ind)
        predicate_is_bigger = predicate_after_equal(">", predicate, equality_ind)
        table_r_found = check_table_with_col_exist("R.", predicate, col)
        table_s_found = check_table_with_col_exist("S.", predicate, col)
        return table_r_found and table_s_found and not predicate_is_smaller and not predicate_is_bigger


def predicate_demands_equality_on_shared_columns(predicate):
    and_ind = predicate.find("AND")
    if and_ind < 0:
        return False
    ind_after_and = and_ind + 3
    left_string = predicate[:and_ind]
    right_string = predicate[ind_after_and:]
    left_string = left_string.strip()
    right_string = right_string.strip()
    equality_on_d = predicate_demands_equality_on_col(left_string, "D") or \
                    predicate_demands_equality_on_col(right_string, "D")
    equality_on_e = predicate_demands_equality_on_col(left_string, "E") or \
                    predicate_demands_equality_on_col(right_string, "E")
    return equality_on_d and equality_on_e


def activate_rule_11b(node):
    """
    SIGMA_P (R X S) = R TJOIN_P S

    * Note: in this assignment we don't support TJOIN, only NJOIN
            so we check that P demands equality on all shared columns,
            in order to ensure it's NJOIN, and thus create:
            R NJOIN S

    1.
        find if there's a predicate demanding equality on all shared columns
        e.g. R.D = S.D AND R.E = S.E (Q: are we searching specifically for this predicate?)
    2.
        check if next node is cartesian

    3. If succeeded in 1 and 2:
        Create 1 new node of NJOIN to replace both previous nodes
        Form all node connections
        New node's left child is cartesian's left child, and likewise with right child
    """
    if node is None:
        return node, False
    if node.operator_type == Operators.SIGMA:
        next_node = node.inputSchemeOne
        if next_node is not None and next_node.operator_type == Operators.CARTESIAN:
            if predicate_demands_equality_on_shared_columns(node.predicate):
                new_node = create_njoin_node()
                new_node.inputSchemeOne = next_node.inputSchemeOne
                new_node.inputSchemeTwo = next_node.inputSchemeTwo
                return new_node, True
    node.inputSchemeOne, rule_succeeded = activate_rule_11b(node.inputSchemeOne)
    if rule_succeeded:
        return node, True
    node.inputSchemeTwo, rule_succeeded = activate_rule_11b(node.inputSchemeTwo)
    return node, rule_succeeded


def has_wrapper_parentheses(string):
    string = string.strip()
    if string[0] == '(' and string[-1] == ')':
        string = string[1:-1]  # strip the outer parenthesis and re-check the trimmed string
        return is_balanced_parentheses(string)
    return False


def strip_wrapper_parentheses(string):
    """
    :param string:
    :return: stripped version of the string without outer parentheses, alongside number of outer parentheses
    """
    num_of_left_spaces = len(string) - len(string.lstrip())
    num_of_left_spaces_stripped = 0
    string = string.strip()
    outer_par_count = 0
    if has_wrapper_parentheses(string):
        string = string[1:-1]
        string, outer_par_count, num_of_left_spaces_stripped = strip_wrapper_parentheses(string)
        outer_par_count = outer_par_count + 1
    return string, outer_par_count, num_of_left_spaces + num_of_left_spaces_stripped


def is_balanced_parentheses(string):
    stack = []
    for i in string:
        if i == "(":
            stack.append(i)
        elif i == ")":
            if len(stack) > 0 and stack[len(stack) - 1] == "(":
                stack.pop()
            else:
                return False
    if len(stack) == 0:
        return True
    else:
        return False


""" -------------------------------------------------------------------
------------------------- SECTION 2 FUNCTIONS -------------------------
------------------------------------------------------------------- """


def print_old_expression(expression_root):
    print("Old expression: ", end="")
    print_expression_tree(expression_root)
    print()


def print_rule_outcome(expression_root, rule_succeeded):
    print("New expression: ", end="")
    print_expression_tree(expression_root)
    print()
    if rule_succeeded:
        print("Rule succeeded.")
    else:
        print("Rule not succeeded.")
    print()


def apply_chosen_rule(expression_root, num):
    if num == 1:
        print("Activating rule 4: SIGMA_(P1 AND P2) (R) = SIGMA_P1 ( SIGMA_P2 (R) )")
        print_old_expression(expression_root)
        expression_root, rule_succeeded = activate_rule_4(expression_root)
    if num == 2:
        print("Activating rule 4a: SIGMA_P1 ( SIGMA_P2 (R) ) = SIGMA_P2 (SIGMA_P1 (R) )")
        print_old_expression(expression_root)
        expression_root, rule_succeeded = activate_rule_4a(expression_root)
    if num == 3:
        print("Activating rule 5a: PI_X [ SIGMA_P (R) ] = SIGMA_P [ PI_X (R) ]")
        print("(Where X is attributes subset of R, and P is attributes subset of X)")
        print_old_expression(expression_root)
        expression_root, rule_succeeded = activate_rule_5a(expression_root)
    if num == 4:
        print("Activating rule 6: SIGMA_P ( R NJOIN\CARTESIAN S) = [SIGMA_P (R) ] NJOIN\CARTESIAN S")
        print("(Where P is subset of attributes \ columns of R)")
        print_old_expression(expression_root)
        expression_root, rule_succeeded = activate_rule_6_united(expression_root, Rules.SIX)
    if num == 5:
        print("Activating rule 6a: SIGMA_Q ( R NJOIN\CARTESIAN S) = R NJOIN\CARTESIAN [SIGMA_Q (S) ]")
        print("(Where Q is subset of attributes \ columns of S)")
        print_old_expression(expression_root)
        expression_root, rule_succeeded = activate_rule_6_united(expression_root, Rules.SIX_A)
    if num == 6:
        print("Activating rule 11b: SIGMA_P (R X S) = R TJOIN_P S")
        print("(Where P is equality on all shared columns, thus creating NJOIN instead of TJOIN)")
        print_old_expression(expression_root)
        expression_root, rule_succeeded = activate_rule_11b(expression_root)
    print_rule_outcome(expression_root, rule_succeeded)
    return expression_root


def apply_random_rules(expression_root):
    print()
    print()
    print("Starting loop:")
    print()
    for i in range(SEC2_ITR_N):
        num = random.randrange(1, 7)
        print("Iteration", i + 1, end=". ")
        expression_root = apply_chosen_rule(expression_root, num)
    return expression_root


def duplicate_expression(node):
    if node is None:
        return None
    new_node = node.dup()
    new_node.inputSchemeOne = duplicate_expression(node.inputSchemeOne)
    new_node.inputSchemeTwo = duplicate_expression(node.inputSchemeTwo)

    return new_node


def part_two_aux(round, org_expr, lqp):
    name = "PART 2 - RANDOM RULES ACTIVATION (Round " + str(round) + ")"
    print_function_borders(name, FunctionBorders.Start)
    print("Original expression:")
    print_expression_tree(org_expr)
    lqp = apply_random_rules(lqp)
    print_function_borders(name, FunctionBorders.End)

    return lqp


def run_part_two(expression_root_input):
    lqp_list = [None] * SEC2_LQP_N
    for i in range(SEC2_LQP_N):
        lqp_list[i] = duplicate_expression(expression_root_input)
        lqp_list[i] = part_two_aux(i + 1, expression_root_input, lqp_list[i])

    print("----------------- FINAL RESULTS -----------------")
    print("Original: ", end="")
    print_expression_tree(expression_root_input)
    print()
    for i in range(SEC2_LQP_N):
        print("Version " + str(i + 1) + ": ", end="")
        print_expression_tree(lqp_list[i])
        print()
    print()
    print()

    return lqp_list


""" -------------------------------------------------------------------
------------------------- SECTION 3 FUNCTIONS -------------------------
------------------------------------------------------------------- """


def analyze_column_data_line(column_data):
    column_data = column_data.strip()
    scheme_name = column_data[0]
    columns = column_data[2:-1]  # get the string without beginning name and parentheses
    columns = columns.split(",")
    col_list = []
    for col in columns:
        data = col.split(":")  # each item is of the format NAME:TYPE, e.g. D:INTEGER
        col_data = ColData()
        data_name = scheme_name + "." + data[0]
        col_data.name = data_name
        col_data.dataType = data[1]
        col_list.append(col_data)
    return col_list


def get_scheme_data_from_file(table_name):
    table_name = table_name.strip()
    if table_name != "R" and table_name != "S":
        return None
    file = open(input_file)
    found_starting_line = False
    line_to_compare = "Scheme " + table_name
    while not found_starting_line:  # Search in file for "Scheme R" or "Scheme S"
        line = file.readline()
        found_starting_line = line.find(line_to_compare) >= 0
    scheme_data = SchemeData(table_name)
    column_data = file.readline()
    col_list = analyze_column_data_line(column_data)
    list_len = len(col_list)
    n_scheme = file.readline().strip()
    scheme_data.N = int(n_scheme[4:])
    for i in range(list_len):
        col_data_line = file.readline().strip()  # read some form of V(col) data, e.g. V(D)=8
        for col in col_list:
            if col.name[2] == col_data_line[2]: # The code supports only one char named columns
                col.V = col_data_line[5:]
                break
    scheme_data.colList = col_list.copy()
    scheme_data.rowSize = len(col_list) * 4
    file.close()
    return scheme_data


def cartesian_scheme_output(input_scheme1_data, input_scheme2_data):
    if input_scheme1_data is None or input_scheme2_data is None:
        return None
    output_scheme_data = SchemeData()
    output_scheme_data.N = int(input_scheme1_data.N) * int(input_scheme2_data.N)
    output_scheme_data.rowSize = int(input_scheme1_data.rowSize) + int(input_scheme2_data.rowSize)
    output_scheme_data.colList = input_scheme1_data.colList + input_scheme2_data.colList

    return output_scheme_data


def pi_scheme_output(node, input_scheme_data):
    if node is None or input_scheme_data is None:
        return None
    output_scheme_data = SchemeData()
    output_scheme_data.N = input_scheme_data.N
    row_size = 0
    output_scheme_data.rowSize = row_size
    for col in node.colList:
        col = col.strip()
        for col2 in input_scheme_data.colList:
            if col == col2.name:
                output_scheme_data.colList.append(col2)
                row_size = row_size + 4
                break
    output_scheme_data.rowSize = row_size
    return output_scheme_data


def break_predicate_to_atomic_formulas(predicate):
    predicate = predicate.replace("(", " ").replace(")", " ")
    atomic_formulas = []
    curr_ind = 0
    last_ind = len(predicate) - 1
    while curr_ind <= last_ind:
        and_ind = predicate.find("AND", curr_ind)
        if and_ind < 0:
            atomic_formula = predicate[curr_ind:].strip()
            curr_ind = last_ind + 1
        else:
            atomic_formula = predicate[curr_ind:and_ind]
            curr_ind = and_ind + 3
        atomic_formulas.append(AtomicFormula(atomic_formula))
    atomic_formulas = remove_duplicate_conditions(atomic_formulas)
    return atomic_formulas


def calculate_formula_probability(atomic_formula, input_scheme_data):
    probability = 1
    if atomic_formula.leftOperand == atomic_formula.rightOperand:
        return probability
    for col in input_scheme_data.colList:
        if col.name.strip() == atomic_formula.leftOperand.strip():
            # Check if second operand is a number, or another column:
            if atomic_formula.rightOperand.isdigit() is False:  # second operand is another column
                for other_col in input_scheme_data.colList:
                    if other_col.name.strip() == atomic_formula.rightOperand.strip():
                        maxV = int(max(int(col.V), int(other_col.V)))
                        return float(probability) * float(1 / maxV)
            return float(1/int(col.V))
    return probability


def remove_duplicate_conditions(atomic_formula_list):
    unique_values_formula_list = []
    value_exists = False
    for formula in atomic_formula_list:
        for new_formula in unique_values_formula_list:
            if formula.leftOperand == new_formula.leftOperand and formula.rightOperand == new_formula.rightOperand:
                value_exists = True
        if not value_exists:
            unique_values_formula_list.append(AtomicFormula(str(formula.leftOperand) + "=" + str(formula.rightOperand)))
            value_exists = False
    return unique_values_formula_list


def sigma_scheme_output(node, input_scheme_data):
    if node is None or input_scheme_data is None:
        return None
    output_scheme_data = SchemeData()
    atomic_formula_list = break_predicate_to_atomic_formulas(node.predicate) # e.g for atomic formula: R.A = 5
    predicate_probability = 1
    for atomic_formula in atomic_formula_list:
        probability_for_formula = calculate_formula_probability(atomic_formula, input_scheme_data)
        predicate_probability = float(predicate_probability) * float(probability_for_formula)
    num_of_rows = float(predicate_probability * float(input_scheme_data.N))
    if 1 > num_of_rows > 0:
        num_of_rows = 1
    else:
        num_of_rows = int(num_of_rows)
    output_scheme_data.N = num_of_rows
    output_scheme_data.colList = input_scheme_data.colList.copy()
    output_scheme_data.rowSize = input_scheme_data.rowSize
    return output_scheme_data


def njoin_scheme_output(input_scheme1_data, input_scheme2_data):
    if input_scheme1_data is None or input_scheme2_data is None:
        return None
    # Creating Cartesian node for the formula
    cartesian_scheme = cartesian_scheme_output(input_scheme1_data, input_scheme2_data)
    # Creating sigma node for the formula
    sigma_node = create_sigma_node("R.D=S.D AND R.E=S.E")
    # Creating the NJOIN node
    output_scheme_data = sigma_scheme_output(sigma_node, cartesian_scheme)
    output_scheme_data.rowSize = output_scheme_data.rowSize - 8
    return output_scheme_data


def get_output_scheme_data(node, scheme_data1, scheme_data2):
    output_scheme_data = None
    if node is not None:
        if node.operator_type == Operators.CARTESIAN:
            output_scheme_data = cartesian_scheme_output(scheme_data1, scheme_data2)
        elif node.operator_type == Operators.SIGMA:
            output_scheme_data = sigma_scheme_output(node, scheme_data1)
        elif node.operator_type == Operators.PI:
            output_scheme_data = pi_scheme_output(node, scheme_data1)
        elif node.operator_type == Operators.NJOIN:
            output_scheme_data = njoin_scheme_output(scheme_data1, scheme_data2)
    return output_scheme_data


def estimate_size_rec(node):
    output_scheme_data = None
    if node is not None:
        if node.operator_type is Operators.TABLE:
            output_scheme_data = get_scheme_data_from_file(node.tableName)
        else:
            scheme_data1 = estimate_size_rec(node.inputSchemeOne)
            scheme_data2 = estimate_size_rec(node.inputSchemeTwo)
            print()
            node.print()
            print()
            if scheme_data1:
                print("Input 1: ", end="")
                scheme_data1.print()
            if scheme_data2:
                print("Input 2: ", end="")
                scheme_data2.print()
            output_scheme_data = get_output_scheme_data(node, scheme_data1, scheme_data2)
            print("Output: ", end="")
            output_scheme_data.print()
    return output_scheme_data


def estimate_size(node, round):
    name = "SIZE ESTIMATION (Round " + str(round) + ")"
    print_function_borders(name, FunctionBorders.Start)
    print("LQP: ", end="")
    print_expression_tree(node)
    print()
    output_scheme_data = estimate_size_rec(node)
    print()
    print_function_borders(name, FunctionBorders.End)

    return output_scheme_data


""" -------------------------------------------------------------------
----------------------- MAIN AND MENU FUNCTIONS -----------------------
------------------------------------------------------------------- """


def print_function_borders(func_name, borders):
    string = None
    if borders == FunctionBorders.Start:
        string = " STARTS"
        left_edge = "╔"
        right_edge = "╗"
        print()
    else:
        string = " FINISHED"
        left_edge = "╚"
        right_edge = "╝"
    print(left_edge + "═════════════════ " + func_name + string + " ═════════════════" + right_edge)
    print()


def run_menu_part1(expression_root_input):
    while True:
        print()
        print("Current expression: ", end="")
        print_expression_tree(expression_root_input)
        print()
        rule_choice_num = input(part_one_menu)
        if rule_choice_num == "7":
            return
        print_old_expression(expression_root_input)
        if rule_choice_num == "1":
            expression_root_input, rule_succeeded = activate_rule_4(expression_root_input)
        if rule_choice_num == "2":
            expression_root_input, rule_succeeded = activate_rule_4a(expression_root_input)
        if rule_choice_num == "3":
            expression_root_input, rule_succeeded = activate_rule_5a(expression_root_input)
        if rule_choice_num == "4":
            expression_root_input, rule_succeeded = activate_rule_6_united(expression_root_input, Rules.SIX)
        if rule_choice_num == "5":
            expression_root_input, rule_succeeded = activate_rule_6_united(expression_root_input, Rules.SIX_A)
        if rule_choice_num == "6":
            expression_root_input, rule_succeeded = activate_rule_11b(expression_root_input)
        print_rule_outcome(expression_root_input, rule_succeeded)


def run_part_three(list_of_random_lqp):
    round_num = 1
    for lqp in list_of_random_lqp:
        estimate_size(lqp, round_num)
        round_num = round_num + 1
    print()


def run_main_menu(query_input, expression_root_input):
    print()
    print("Original query: ", query_input)
    list_of_random_lqp = []
    while True:
        print("Current algebraic expression: ", end="")
        print_expression_tree(expression_root_input)
        print()
        main_menu_choice = input(main_menu)
        if main_menu_choice == "1":
            run_menu_part1(expression_root_input)
        elif main_menu_choice == "2":
            list_of_random_lqp = run_part_two(expression_root_input)
        elif main_menu_choice == "3":
            run_part_three(list_of_random_lqp)
        elif main_menu_choice == "4":
            estimate_size(expression_root_input, 1)
        elif main_menu_choice == "5":
            query_input = read_query()
            expression_root_input = get_expr_from_query(query_input)
        elif main_menu_choice == "6":
            print("Program exiting. Have a good day!")
            return


def get_expr_from_query(query):
    location_of_SELECT = query.find("SELECT")
    location_after_SELECT = location_of_SELECT + 6
    location_of_FROM = query.find("FROM")
    location_after_FROM = location_of_FROM + 4
    location_of_WHERE = query.find("WHERE")
    location_after_WHERE = location_of_WHERE + 5
    string_after_select = query[location_after_SELECT:location_of_FROM]
    string_after_from = query[location_after_FROM:location_of_WHERE]
    string_after_where = query[location_after_WHERE:]
    expression_root_input = create_pi_node(string_after_select)
    expression_root_input.inputSchemeOne = create_sigma_node(string_after_where)
    expression_root_input.inputSchemeOne.inputSchemeOne = create_cartesian_node()
    schemes_list = string_after_from.split(sep=",")
    first_scheme_name = schemes_list[0].strip()
    second_scheme_name = schemes_list[1].strip()
    first_scheme_node = create_original_table_node(first_scheme_name)
    second_scheme_node = create_original_table_node(second_scheme_name)
    expression_root_input.inputSchemeOne.inputSchemeOne.inputSchemeOne = first_scheme_node
    expression_root_input.inputSchemeOne.inputSchemeOne.inputSchemeTwo = second_scheme_node

    return expression_root_input


def read_query():
    query_input = input("Enter a query:\n")
    query_input = query_input.strip()
    if query_input.endswith(";"):
        query_input = query_input[:-1]
    return query_input


query = read_query()
expressionRoot = get_expr_from_query(query)
run_main_menu(query, expressionRoot)
