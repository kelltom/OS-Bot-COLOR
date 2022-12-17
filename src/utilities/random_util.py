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
    def random_point_in(x_min, y_min, width, height, seeds: List[List[int]]) -> List[int]:
        """
        Returns a random pixel within some bounding box based on a list of seeds.
        Args:
            x_min: The left-most coordinate of the bounding box.
            y_min: The top-most coordinate of the bounding box.
            width: The width of the bounding box.
            height: The height of the bounding box.
            seeds: A list of seeds to use for the randomization.
        Returns:
            A random [x, y] coordinate within the bounding box.
        """
        sg = secrets.SystemRandom()

        # Generate a random pixel within the full bounding box with a 25% probability.
        if sg.randrange(0, 101) > 75:
            return RandomUtil.__random_from(x_min, y_min, width, height)

        # Calculate the dimensions and position of an inner bounding box within the full bounding box.
        offset_percentage = sg.uniform(0.150, 0.350)
        inner_x_min = round(width * offset_percentage + x_min)
        inner_y_min = round(height * offset_percentage + y_min)
        inner_width = round(width * (1.000 - (offset_percentage * 2)))
        inner_height = round(height * (1.000 - (offset_percentage * 2)))

        # Select a random seed from the list of seeds.
        random_index = sg.randrange(0, len(seeds))
        ratio_x = round(inner_width * seeds[random_index][0])
        ratio_y = round(inner_height * seeds[random_index][1])

        # Calculate the dimensions and position of a bounding box within the inner bounding box.
        start_x, start_y = inner_x_min + ratio_x, inner_y_min + ratio_y
        start_fix_width, end_fix_width = start_x - x_min, width - ratio_x
        start_fix_height, end_fix_height = start_y - y_min, height - ratio_y

        # Determine the dimensions of the bounding box within the inner bounding box.
        inner_inner_width = start_fix_width if start_fix_width <= end_fix_width else end_fix_width
        inner_inner_height = start_fix_height if start_fix_height <= end_fix_height else end_fix_width

        # Generate a random pixel within the bounding box within the inner bounding box.
        return RandomUtil.__random_from(start_x, start_y, inner_inner_width, inner_inner_height, center=True)

    @staticmethod
    def __random_from(x_min, y_min, width, height, center: bool = False) -> List[int]:
        # If center is not set to True, shift x_min and y_min to the center of the region
        if not center:
            x_min = x_min + math.ceil(width / 2)
            y_min = y_min + math.ceil(height / 2)

        # Calculate the minimum and maximum values for x and y within the region
        x_min_bound = x_min - math.ceil(width / 2)
        x_max_bound = x_min + math.ceil(width / 2)
        y_min_bound = y_min - math.ceil(height / 2)
        y_max_bound = y_min + math.ceil(height / 2)

        # Calculate the standard deviation for x and y based on the region's dimensions
        sigma_x = (width / 2) * 0.33
        sigma_y = (height / 2) * 0.33

        # Generate a random x and y value within the region using truncated normal sampling
        x = int(RandomUtil.truncated_normal_sample(x_min_bound, x_max_bound, x_min, sigma_x))
        y = int(RandomUtil.truncated_normal_sample(y_min_bound, y_max_bound, y_min, sigma_y))
        return [x, y]

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
