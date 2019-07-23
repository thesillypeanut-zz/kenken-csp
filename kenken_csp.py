# Look for #IMPLEMENT tags in this file.
'''
All models need to return a CSP object, and a list of lists of Variable objects
representing the board. The returned list of lists is used to access the
solution.

For example, after these three lines of code

    csp, var_array = kenken_csp_model(board)
    solver = BT(csp)
    solver.bt_search(prop_FC, var_ord)

var_array[0][0].get_assigned_value() should be the correct value in the top left
cell of the KenKen puzzle.

The grid-only models do not need to encode the cage constraints.

1. binary_ne_grid (worth 10/100 marks)
    - A model of a KenKen grid (without cage constraints) built using only
      binary not-equal constraints for both the row and column constraints.

2. nary_ad_grid (worth 10/100 marks)
    - A model of a KenKen grid (without cage constraints) built using only n-ary
      all-different constraints for both the row and column constraints.

3. kenken_csp_model (worth 20/100 marks)
    - A model built using your choice of (1) binary binary not-equal, or (2)
      n-ary all-different constraints for the grid.
    - Together with KenKen cage constraints.

'''
from cspbase import *
import itertools


def binary_ne_grid(kenken_grid):
    list_vars = []
    sat_tuples = []
    vars = []
    N = kenken_grid[0][0]
    check_cons = []
    csp = CSP("binary_ne_model")

    # include the 1-N domain
    domain = [i+1 for i in range(N)]

    # add all combination of NxN variables(each cell name)
    for row in domain:
        row_list = []

        for column in domain:
            new_var_name = str(row) + str(column)
            new_var = Variable(new_var_name, domain)
            row_list.append(new_var)
            list_vars.append(new_var)
            csp.add_var(new_var)

            # make the satisfying tuples, (1-N,1-N) Where each element is distinct
            if row != column:
                sat_tuple = (row, column)
                sat_tuples.append(sat_tuple)

        vars.append(row_list)

    # make each constraint for rows and columns
    for i in list_vars:
        var1 = i.name

        for j in list_vars:
            var2 = j.name

            if var1 != var2:
                if ((var1[0] == var2[0]) or (var1[1] == var2[1])) and ((var1, var2) not in check_cons and (var2, var1) not in check_cons):
                    tuple_name = var1 + "," + var2
                    cons = Constraint(tuple_name, [i, j])
                    cons.add_satisfying_tuples(sat_tuples)
                    check_cons.append((var1, var2))
                    csp.add_constraint(cons)

    return csp, vars


def nary_ad_grid(kenken_grid):
    list_vars = []
    vars = []
    sat_tuples = []
    N = kenken_grid[0][0]
    csp = CSP("nary_ad_model")

    # include the 1-N domain
    domain = [i+1 for i in range(N)]

    # init two empty lists of lists of N elements to hold all elements in each row and column
    all_row = [[] for i in range(N)]
    all_col = [[] for i in range(N)]

    # add all combination of NxN variables(each cell name)
    # define the scope of constraints for each row and col
    for row in domain:
        row_list = []

        for column in domain:
            new_var_name = str(row) + str(column)
            new_var = Variable(new_var_name, domain)
            all_row[row-1].append(new_var)
            all_col[column-1].append(new_var)
            list_vars.append(new_var)
            csp.add_var(new_var)
            row_list.append(new_var)

        vars.append(row_list)

    # all-diff requires all different permutation of 1-N element for either row or col as satisfying tuple
    sat_tuples = list(itertools.permutations(domain, N))

    # construct row and col constraints
    for i in domain:
        row_name = "R" + str(i)
        row_cons = Constraint(row_name, all_row[i-1])
        row_cons.add_satisfying_tuples(sat_tuples)
        csp.add_constraint(row_cons)

        col_name = "C" + str(i)
        col_cons = Constraint(col_name, all_col[i-1])
        col_cons.add_satisfying_tuples(sat_tuples)
        csp.add_constraint(col_cons)

    return csp, vars


def kenken_csp_model(kenken_grid):
    list_vars = []
    sat_tuples = []
    all_cons = []
    vars = []
    check_cons = []
    N = kenken_grid[0][0]
    csp = CSP("kenken_csp_model")

    # include the 1-N domain
    domain = [i+1 for i in range(N)]

    # add all combination of NxN variables(each cell name)
    for row in domain:
        row_list = []

        for column in domain:
            new_var_name = str(row) + str(column)
            new_var = Variable(new_var_name, domain)
            csp.add_var(new_var)
            row_list.append(new_var)
            list_vars.append(new_var)

            # make the satisfying tuples, (1-N,1-N) Where each element is distinct
            # this is same as binary_ne_grid
            if row != column:
                sat_tuple = (row, column)
                sat_tuples.append(sat_tuple)

        vars.append(row_list)

    for cage in kenken_grid[1:]:
        all_cell = []
        all_domain = []
        cage_sat_tuples = []

        if len(cage) == 2:
            target_value = cage[1]
            cell = str(cage[0])
            row_index = int(cell[0]) - 1
            col_index = int(cell[1]) - 1
            vars[row_index][col_index].assign(target_value)

        else:
            target_value = cage[-2]
            operation = cage[-1]

            for i in range(len(cage)-2):
                row_index = int(str(cage[i])[0]) - 1
                col_index = int(str(cage[i])[1]) - 1
                all_domain.append(vars[row_index][col_index].domain())
                all_cell.append(vars[row_index][col_index])

            cons_name = "Cage" + str(kenken_grid.index(cage))
            cons = Constraint(cons_name, all_cell)
            comb_domain = list(itertools.product(*all_domain))

            for d in comb_domain:
                # Addition
                if operation == 0:
                    sum = 0

                    for val in d:
                        sum = sum + val

                    if sum == target_value:
                        cage_sat_tuples.append(d)

                # Subtraction
                elif (operation == 1):
                    permut_d = list(itertools.permutations(d))

                    for val in permut_d:
                        sub = val[0]

                        for i in range(1, len(val)):
                            sub = sub - val[i]

                        if sub == target_value:
                            cage_sat_tuples.append(d)

                # Division
                elif (operation == 2):
                    permut_d = list(itertools.permutations(d))

                    for val in permut_d:
                        div = val[0]

                        for n in range(1, len(val)):
                            div = div/val[n]

                        if (div == target_value):
                            cage_sat_tuples.append(d)

                # Multiplication
                elif (operation == 3):
                    Mult = 1

                    for val in d:
                        Mult = Mult * val

                    if (Mult == target_value):
                        cage_sat_tuples.append(d)

            cons.add_satisfying_tuples(cage_sat_tuples)
            all_cons.append(cons)

    # Now Add the row and col binary constrains
    for i in list_vars:
        var1 = i.name

        for j in list_vars:
            var2 = j.name

            # same as binary_ne_grid
            if var1 != var2:
                if ((var1[0] == var2[0]) or (var1[1] == var2[1])) and ((var1, var2) not in check_cons and (var2, var1) not in check_cons):
                    tuple_name = var1 + "," + var2
                    cons = Constraint(tuple_name, [i, j])
                    cons.add_satisfying_tuples(sat_tuples)
                    check_cons.append((var1, var2))
                    all_cons.append(cons)

    # All cage + row,col constraints are now added to the CSP
    for c in all_cons:
        csp.add_constraint(c)

    return csp, vars
