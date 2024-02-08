def hypotenuse(a:float,b:float)->float:
    """Pythagorean Theroem

    Args:
        a (float): leg 1
        b (float): leg 2

    Returns:
        float: hypotenoose 
    """
    a_squared = a*a
    b_squared = b*b
    summation = a_squared+b_squared
    c = summation ** 0.5
    return c 


hyp = hypotenuse("10",-10)
print(hyp)