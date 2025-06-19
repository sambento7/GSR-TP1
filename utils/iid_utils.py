from exceptions import InvalidIIDError

def parse_iid(iid: list[int]) -> dict:
    """
    Parses a L-SNMPvS IID into its components: structure, object and optional indexes.

    :param iid: List of integers representing the IID (e.g., [2, 1, 3] or [2, 1, 1, 3]).
    :return: Dictionary with keys: structure, object, indexes (list of 0, 1, or 2 integers)
    """
    if not (2 <= len(iid) <= 4):
        raise InvalidIIDError("IID must contain between 2 and 4 integers.")

    if not all(isinstance(x, int) for x in iid):
        raise InvalidIIDError("All IID parts must be integers.")

    structure = iid[0]
    if structure <= 0:
        raise InvalidIIDError("Structure ID must be a positive integer.")

    obj = iid[1]
    if obj < 0:
        raise InvalidIIDError("Object ID must be 0 or positive.")

    indexes = iid[2:]  # may be empty, one or two elements

    return {
        "structure": structure,
        "object": obj,
        "indexes": indexes
    }
