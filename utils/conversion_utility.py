import re


def convert_rgba_to_hex(rgba_value):
    """
    :param rgba_value: takes a tuple of integer values in RGBA format
    :return:    returns HEX value after converting RGBA values
    """
    if type(rgba_value) is str:
        color_map = map(lambda color_value: int(re.sub('\\D+', '', color_value)), rgba_value.split(','))
        color_values_tuple = tuple(color_map)
        return '#{0:02x}{1:02x}{2:02x}'.format(*color_values_tuple)
    elif type(rgba_value) is tuple:
        return '#{0:02x}{1:02x}{2:02x}'.format(*rgba_value)


# def convert_rgba_to_hex(r, g, b):
#     """
#     :param rgba_value: takes integer values in RGBA format
#     :return:    returns HEX value after converting RGBA values
#     """
#     return '#{0:02x}{1:02x}{2:02x}'.format(r, g, b)
