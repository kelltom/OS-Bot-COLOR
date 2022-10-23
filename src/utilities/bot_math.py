import math
import numpy
import utilities.runelite_cv as rcv


def object_detector_closest(center_me, color_object, rect: Rectangle, farthest=False, hardcode_center=None):
    if hardcode_center:
        center = hardcode_center
    else:
        center = center_me
    main_list = rcv.object_list(color_object, rect)
    if center and main_list:
        main_distance = []
        for points in main_list:
            init_distance = [points[0][0], points[0][1]]
            distance = math.sqrt(((center[0] - points[0][0]) ** 2) + ((center[1] - points[0][1]) ** 2))
            init_distance.append(distance)
            main_distance.append(init_distance)
        if farthest:
            closest_distance = sorted(main_distance, key=lambda x: x[2])[-1]
        else:
            closest_distance = sorted(main_distance, key=lambda x: x[2])[0]
        del closest_distance[-1]
        if closest_distance:
            for points in main_list:
                if closest_distance == points[0]:
                    return points
        return []
    else:
        return []
      
      
def pseudo_random(mu, sigma, low, high):
    t = 2 * math.pi * sg.uniform(0.000, 1.000)
    g = mu + (sigma * math.sqrt(-1.955 * math.log(sg.uniform(0.000, 1.000)))) * math.cos(t)
    if g < low:
        g = low
    if g > high:
        g = high
    return int(g)
  
  
def random_start(x_axis, y_axis, width, height):
    if (width % 2) == 0:
        x_axis = x_axis + (width / 2)
        width_b = x_axis - (width / 2)
        width_c = x_axis + (width / 2)
    else:
        x_axis = x_axis + (width / 2 + 0.5)
        width_b = x_axis - (width / 2 + 0.5)
        width_c = x_axis + (width / 2 - 0.5)
    if (height % 2) == 0:
        y_axis = y_axis + (height / 2)
        height_b = y_axis - (height / 2)
        height_c = y_axis + (height / 2)
    else:
        y_axis = y_axis + (height / 2 + 0.5)
        height_b = y_axis - (height / 2 + 0.5)
        height_c = y_axis + (height / 2 - 0.5)
    width_a = (width / 2) * 0.33
    height_a = (height / 2) * 0.33
    end_x = pseudo_random(x_axis, width_a, width_b, width_c)
    end_y = pseudo_random(y_axis, height_a, height_b, height_c)
    return [end_x, end_y]
  
  
  def point_in_normal(center_me, color, farthest=False, hardcode_center=None):
    if hardcode_center:
        main_object = object_detector_closest(center_me, color, farthest=farthest, hardcode_center=hardcode_center)
    else:
        main_object = object_detector_closest(center_me, color, farthest=farthest)
    if main_object:
        while True:
            pixel = random_start(main_object[2][0], main_object[2][1], main_object[1][0], main_object[1][1])
            real_pixel = (main_object[3] == np.array(pixel)).all(axis=1).any()
            if real_pixel:
                return [pixel, main_object[1], main_object[2]]
    else:
        return []
