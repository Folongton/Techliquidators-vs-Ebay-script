from functools import reduce


def median(lst):
    sorted_lst = sorted(lst)
    lst_len = len(lst)
    index = (lst_len - 1) // 2

    if lst:

        if lst_len % 2:
            return sorted_lst[index]
        else:
            return (sorted_lst[index] + sorted_lst[index + 1]) / 2.0
        # return sorted_lst[index] if lst_len % 2 else (sorted_lst[index] + sorted_lst[index + 1]) / 2.0
    else:
        return 0


def avg(lst):
    return reduce(lambda x, y: x + y, lst) / len(lst) if lst else 0
