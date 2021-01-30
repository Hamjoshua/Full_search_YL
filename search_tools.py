def calculate_spn(pos, lowerCorner, upperCorner):
    float_pos = eval(pos)
    float_lowerCorner = eval(lowerCorner)
    float_upperCorner = eval(upperCorner)

    spn_x, spn_y = round(abs(float_upperCorner[0] - float_lowerCorner[0]) / 20, 4) + 0.005,\
                   round(abs(float_upperCorner[1] - float_lowerCorner[1]) / 20, 4) + 0.005
    return f"{spn_x},{spn_y}"


def join_coords(string_coords):
    return ",".join(string_coords.split(' '))
