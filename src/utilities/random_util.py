import math
import random
import secrets
from datetime import datetime
from typing import List


class RandomUtil:
    @staticmethod
    def random_seeds(mod: int = 0, start: int = 8, stop: int = 12):
        """
        Generates a set of random seeds.
        Args:
            mod: The modifier to add to a numeric representation of the current date.
                 Default is 0. E.g., if the date is 2022-01-01, and the mod is 5, the
                 random seeds will be based on random.seed(20220106).
            start: The minimum number of seeds to generate. Default is 8.
            stop: The maximum number of seeds to generate. Default is 12.
        Returns:
            A list of random seeds.
        """
        sg = secrets.SystemRandom()
        date = int(datetime.now().strftime("%Y%m%d"))
        random.seed(date + mod)
        return [[random.uniform(0.000, 1.000), random.uniform(0.000, 1.000)] for _ in range(sg.randrange(start, stop))]

    @staticmethod
    def random_point_in(x, y, width, height, seeds: List[List[int]]) -> List[int]:
        """
        Returns a random pixel within some bounding box based on a list of seeds.
        Args:
            x: The left-most coordinate of the bounding box.
            y: The top-most coordinate of the bounding box.
            width: The width of the bounding box.
            height: The height of the bounding box.
            seeds: A list of seeds to use for the randomization.
        Returns:
            A random [x, y] coordinate within the bounding box.
        """
        sg = secrets.SystemRandom()
        if sg.randrange(0, 101) > 75:
            return RandomUtil.__random_from(x, y, width, height)
        offset_percentage = sg.uniform(0.150, 0.350)
        start_inner_x = round(width * offset_percentage + x)
        start_inner_y = round(height * offset_percentage + y)
        start_x_percent = round(width * (1.000 - (offset_percentage * 2)))
        start_y_percent = round(height * (1.000 - (offset_percentage * 2)))
        random_index = sg.randrange(0, len(seeds))
        init_ratio_x = round(start_x_percent * seeds[random_index][0])
        init_ratio_y = round(start_y_percent * seeds[random_index][1])
        real_start_x, real_start_y = (
            start_inner_x + init_ratio_x,
            start_inner_y + init_ratio_y,
        )
        start_fix_width, end_fix_width = real_start_x - x, width - init_ratio_x
        start_fix_height, end_fix_height = real_start_y - y, height - init_ratio_y
        real_width = start_fix_width if start_fix_width <= end_fix_width else end_fix_width
        if start_fix_height <= end_fix_height:
            real_height = start_fix_height
        else:
            real_height = end_fix_width
        return RandomUtil.__random_from(real_start_x, real_start_y, real_width, real_height, center=True)

    @staticmethod
    def __random_from(x_min, y_min, width, height, center: bool = False) -> List[int]:
        if not center:
            x_min = x_min + math.ceil(width / 2)
            y_min = y_min + math.ceil(height / 2)

        width_min = x_min - math.ceil(width / 2)
        width_max = x_min + math.ceil(width / 2)

        height_min = y_min - math.ceil(height / 2)
        height_max = y_min + math.ceil(height / 2)

        sigma_x = (width / 2) * 0.33
        sigma_y = (height / 2) * 0.33
        end_x = int(RandomUtil.truncated_normal_sample(width_min, width_max, x_min, sigma_x))
        end_y = int(RandomUtil.truncated_normal_sample(height_min, height_max, y_min, sigma_y))
        return [end_x, end_y]

    @staticmethod
    def truncated_normal_sample(lower_bound, upper_bound, mean, standard_deviation) -> float:
        """
        Generate a random sample from the normal distribution using the Box-Muller method.
        Args:
            lower_bound: The lower bound of the truncated normal distribution.
            upper_bound: The upper bound of the truncated normal distribution.
            mean: The mean of the normal distribution.
            standard_deviation: The standard deviation of the normal distribution.
        Returns:
            A random float from the truncated normal distribution.
        """
        sg = secrets.SystemRandom()
        u1 = sg.uniform(0, 1)
        u2 = sg.uniform(0, 1)
        z1 = math.sqrt(-2 * math.log(u1)) * math.cos(2 * math.pi * u2)
        sample = mean + standard_deviation * z1

        if sample < lower_bound:
            return lower_bound
        elif sample > upper_bound:
            return upper_bound
        else:
            return sample
