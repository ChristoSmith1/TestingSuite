import math

def circle_intersection_area(r1: float, r2: float, d: float) -> float:
    """
    Calculate the area of the intersection of two circles with radii r1 and r2,
    where the centers are separated by a distance d.

    Parameters:
    - r1 (float): Radius of the first circle.
    - r2 (float): Radius of the second circle.
    - d (float): Distance between the centers of the two circles.

    Returns:
    float: Area of the intersection of the two circles.
    """
    # Check if circles do not intersect
    if d >= r1 + r2:
        return 0.0
    
    # Check if one circle is completely inside the other
    if d <= abs(r1 - r2):
        return math.pi * min(r1, r2) ** 2.0

    # Calculate the area of the intersection using the law of cosines
    a = (r1 ** 2 - r2 ** 2 + d ** 2) / (2 * d)
    b = d - a
    A1 = r1 ** 2 * math.acos(a / r1) - a * math.sqrt(r1 ** 2 - a ** 2)
    A2 = r2 ** 2 * math.acos(b / r2) - b * math.sqrt(r2 ** 2 - b ** 2)

    # Return the sum of the areas of the two segments
    return A1 + A2

if __name__ == "__main__":
    # Example 1: Circles do not intersect
    r1 = 5.0
    r2 = 5.0
    d = 20.0
    print(f"Example 1: Circles do not intersect.")
    print(f"r1 = {r1:.5f}, r2 = {r2:.5f}, d = {d:.5f}")
    intersection_area = circle_intersection_area(r1, r2, d)
    print(f"Intersection Area: {intersection_area:.5f}\n")

    # Example 2: One circle completely inside the other
    r1 = 4.0
    r2 = 2.5
    d = 1.0
    print(f"Example 2: One circle completely inside the other.")
    print(f"r1 = {r1:.5f}, r2 = {r2:.5f}, d = {d:.5f}")
    intersection_area = circle_intersection_area(r1, r2, d)
    print(f"Intersection Area: {intersection_area:.5f}\n")

    # Example 3: Standard case - Circles intersect
    r1 = 5.0
    r2 = 3.0
    d = 7.0
    print(f"Example 3: Standard case - Circles intersect.")
    print(f"r1 = {r1:.5f}, r2 = {r2:.5f}, d = {d:.5f}")
    intersection_area = circle_intersection_area(r1, r2, d)
    print(f"Intersection Area: {intersection_area:.5f}\n")

    # Example 4: Larger circles with partial intersection
    r1 = 8.5
    r2 = 7.0
    d = 5.0
    print(f"Example 4: Larger circles with partial intersection.")
    print(f"r1 = {r1:.5f}, r2 = {r2:.5f}, d = {d:.5f}")
    intersection_area = circle_intersection_area(r1, r2, d)
    print(f"Intersection Area: {intersection_area:.5f}\n")
