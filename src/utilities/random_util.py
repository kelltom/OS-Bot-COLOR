import math
import random
import secrets
from datetime import datetime
from typing import List, Union

import numpy as np


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

    if sg.randrange(0, 101) > 75:
        # Generate a random pixel within the full bounding box.
        return __random_from(x_min, y_min, width, height)

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
    inner_inner_height = start_fix_height if start_fix_height <= end_fix_height else end_fix_height

    # Generate a random pixel within the bounding box within the inner bounding box.
    return __random_from(start_x, start_y, inner_inner_width, inner_inner_height, centered=False)


def __random_from(x_min, y_min, width, height, centered: bool = True) -> List[int]:
    """
    Helper function to generate a random pixel within some bounding box. The bounding box can be
    centered on the x_min and y_min coordinates, or the bounding box can be offset from the x_min
    and y_min coordinates (i.e., x_min and y_min are the top-left corner of the bounding
    box).
    Args:
        x_min: The left-most coordinate of the bounding box.
        y_min: The top-most coordinate of the bounding box.
        width: The width of the bounding box.
        height: The height of the bounding box.
        centered: Whether or not the bounding box is centered on the x_min and y_min coordinates.
    """
    if centered:
        # The bounding box to search is to be centered on the x_min and y_min coordinates
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
    x = int(truncated_normal_sample(x_min_bound, x_max_bound, x_min, sigma_x))
    y = int(truncated_normal_sample(y_min_bound, y_max_bound, y_min, sigma_y))
    return [x, y]


def truncated_normal_sample(lower_bound, upper_bound, mean=None, std=None) -> float:
    """
    Generate a random sample from a normal distribution using the Box-Muller method.
    Args:
        lower_bound: The lower bound of the truncated normal distribution.
        upper_bound: The upper bound of the truncated normal distribution.
        mean: The mean of the normal distribution (default is mid-point between bounds).
        std: The standard deviation of the normal distribution (default is auto-generated).
    Returns:
        A random float from the truncated normal distribution.
    Examples:
        100,000 x `truncated_normal_sample(0, 100)` graphed: https://i.imgur.com/8W12RZX.png
    """
    if mean is None:
        mean = (lower_bound + upper_bound) / 2
    if std is None:
        std = (upper_bound - lower_bound) / 9
    # Keep generating samples until we get one that falls within the specified bounds
    while True:
        # Generate two independent standard normal samples
        x1, x2 = np.random.normal(0, 1), np.random.normal(0, 1)
        z = x1**2 + x2**2
        if z >= 0 and z <= 1:
            # Use the Box-Muller transform to generate a sample from the normal distribution
            sample = mean + std * x1 * np.sqrt(-2 * np.log(z) / z)
            if sample < lower_bound:
                continue
            if sample > upper_bound:
                continue
            return sample


def fancy_normal_sample(lower_bound, upper_bound) -> float:
    """
    Generate a random sample from a truncated normal distribution with randomly-selected means.
    This produces a more "fancy" distribution than a standard normal distribution, which could emulate
    randomness in human gameplay activity. This function is a work in progress.
    Args:
        lower_bound: The lower bound of the truncated normal distribution.
        upper_bound: The upper bound of the truncated normal distribution.
    Returns:
        A random float from a truncated normal distribution with randomly-selected means.
    Examples:
        100,000 x `truncated_normal_sample(0, 100)` graphed: https://i.imgur.com/XP4Loff.png
    """
    # Default will be two means, one at 1/3rd and one at 2/3 of the range
    means = [lower_bound + (upper_bound - lower_bound) * 0.33, lower_bound + (upper_bound - lower_bound) * 0.66]
    # Generate probabilities for each mean proportional to the index
    p = [(i + 1) ** 2 / sum((i + 1) ** 2 for i in range(len(means))) for i in range(len(means))][::-1]
    # Select a mean from the list with a probability proportional to the index
    index = np.random.choice(range(len(means)), p=p)
    mean = means[index]
    # Retrieve a sample from the truncated normal distribution
    return truncated_normal_sample(lower_bound, upper_bound, mean=mean)


def chisquared_sample(df: int, min: float = 0, max: float = np.inf) -> float:
    """
    Generate a random sample from a Chisquared distribution. Contraining the maximum will produce abnormal means.
    Args:
        df: Degrees of freedom (approximately the average result).
        min: Minimum allowable output (default is 0)
        max: Maximum allowable output (default is infinity).
    Returns:
        A random float from a Chisquared distribution.
    Examples:
        For 100,000 samples of chisquared_sample(average = 25, min = 3):
        - Average = 24.98367264407156
        - Maximum = 67.39469215530804
        - Minimum = 3.636904524316633
        - Graphed: https://i.imgur.com/9re2ezf.png
    """
    if max is None:
        max = np.inf
    while True:
        x = np.random.chisquare(df)
        if x >= min and x <= max:
            return x


def random_chance(probability: float) -> bool:
    """
    Returns true or false based on a probability.
    Args:
        probability: The probability of returning true (between 0 and 1).
    Returns:
        True or false.
    """
    # ensure probability is between 0 and 1
    if not isinstance(probability, float):
        raise TypeError("Probability must be a float")
    if probability < 0.000 or probability > 1.000:
        raise ValueError("Probability must be between 0 and 1")
    return secrets.SystemRandom().random() < probability


if __name__ == "__main__":
    import matplotlib.pyplot as plt

    # Truncated normal distribution
    samples = [truncated_normal_sample(lower_bound=0, upper_bound=100) for _ in range(100000)]
    print("Truncated normal distribution")
    print(f"Average output = {sum(samples) / len(samples)}")
    print(f"Maximum output = {max(samples)}")
    print(f"Minimum output = {min(samples)}")
    print()
    plt.hist(samples, bins=600)
    plt.title("Truncated normal distribution")
    plt.show()

    # Fancy normal distribution
    samples = [fancy_normal_sample(lower_bound=0, upper_bound=100) for _ in range(100000)]
    print("Truncated normal distribution")
    print(f"Average output = {sum(samples) / len(samples)}")
    print(f"Maximum output = {max(samples)}")
    print(f"Minimum output = {min(samples)}")
    print()
    plt.hist(samples, bins=600)
    plt.title("Fancy normal distribution")
    plt.show()

    # Chi-squared distribution
    samples = [chisquared_sample(df=25) for _ in range(100000)]
    print("Chi-squared distribution")
    print(f"Average output = {sum(samples) / len(samples)}")
    print(f"Maximum output = {max(samples)}")
    print(f"Minimum output = {min(samples)}")
    plt.hist(samples, bins=600)
    plt.title("Chi-squared distribution")
    plt.show()
