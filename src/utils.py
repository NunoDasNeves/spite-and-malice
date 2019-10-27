'''
    Utility functions and classes that don't fit elsewhere
'''

def copy_nested(piles, immutable=False):
    '''
        Copy lists or tuples (which may contain more lists or tuples)
        of objects
        Returns a list (of lists) of objects, or tuple of tuples if immutable is True
    '''
    new_piles = list(piles[:])
    for i in range(len(new_piles)):
        # Assume it's a list or tuple, if not a Card
        if isinstance(new_piles[i], (list, tuple)):
            new_piles[i] = copy_nested(new_piles[i], immutable)
    return new_piles if not immutable else tuple(new_piles)