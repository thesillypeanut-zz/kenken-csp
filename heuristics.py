# Look for #IMPLEMENT tags in this file. These tags indicate what has
# to be implemented.

import random
'''
This file will contain different variable ordering heuristics to be used within
bt_search.

var_ordering == a function with the following template
    var_ordering(csp)
        ==> returns Variable 

    csp is a CSP object---the heuristic can use this to get access to the
    variables and constraints of the problem. The assigned variables can be
    accessed via methods, the values assigned can also be accessed.

    var_ordering returns the next Variable to be assigned, as per the definition
    of the heuristic it implements.

val_ordering == a function with the following template
    val_ordering(csp,var)
        ==> returns [Value, Value, Value...]
    
    csp is a CSP object, var is a Variable object; the heuristic can use csp to access the constraints of the problem, and use var to access var's potential values. 

    val_ordering returns a list of all var's potential values, ordered from best value choice to worst value choice according to the heuristic.

'''


def ord_mrv(csp):
    ''' A variable ordering heuristic that chooses the next variable to be assigned
        according to the Minimum- Remaining-Value (MRV) heuristic. Returns the
        variable with the most constrained current domain (i.e., the variable with the
        fewest legal values).'''

    next_var = (None, float("inf"))

    for var in csp.get_all_unasgn_vars():
        cur_dom_size = var.cur_domain_size()
        if cur_dom_size < next_var[1]:
            next_var = (var, cur_dom_size)

    return next_var[0]


def val_lcv(csp, var):
    ''' A value heuristic that, given a variable, chooses the value to be assigned according
       to the Least- Constraining-Value (LCV) heuristic. Returns a list of values
       ordered by the value that rules out the fewest values in the remaining
       variables (i.e., the variable that gives the most flexibility later on) to the value
       that rules out the most.'''

    vals = []

    for d in var.cur_domain():
        var.assign(d)
        n_pruned_vals = 0

        for c in csp.get_cons_with_var(var):
            for var2 in c.get_unasgn_vars():
                for d2 in var2.cur_domain():
                    if not c.has_support(var2, d2):
                        n_pruned_vals += 1

        var.unassign()
        vals.append((n_pruned_vals, d))

    vals.sort()

    return [val[1] for val in vals]
