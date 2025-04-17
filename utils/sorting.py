

def is_ascending_ordered(items_list, case_insensitive=True):
    items_list = list(map(lambda item: item.lower(), items_list)) if case_insensitive else items_list
    total_items = len(items_list)

    for i in range(0,  total_items - 1):
        if items_list[i] > items_list[i + 1]:
            return False
    return True


def is_descending_ordered(items_list, case_insensitive=True):
    items_list = list(map(lambda item: item.lower(), items_list)) if case_insensitive else items_list
    total_items = len(items_list)

    for i in range(0,  total_items - 1):
        if items_list[i] < items_list[i + 1]:
            return False
    return True
