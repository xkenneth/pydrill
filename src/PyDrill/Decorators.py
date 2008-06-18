def contract(func):
    """A decorator that makes sure a contract returns either a true or false value."""
    def inner_func(*args,**kwargs):
        res = func(*args,**kwargs)
        if res is True or res is False:
            return res
        else:
            raise ValueError("Contract did not specify a correct result!")
			
    return inner_func
