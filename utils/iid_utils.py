from exceptions import InvalidIIDError

def parse_iid(iid: str) -> dict:
    """
    Parses a L-SNMPvS IID into its components: structure, object and optional indexes.

    :param iid: String representation of the IID (e.g., "2.1.3" or "2.1.1.3").
    :return: Dictionary with keys: structure, object, indexes (list of 0, 1, or 2 integers)
    """
    parts = iid.split(".")

    if not (2 <= len(parts) <= 4):
        raise InvalidIIDError("IID must contain between 2 and 4 integers.")

    try:
        nums = [int(p) for p in parts]
    except ValueError:
        raise InvalidIIDError("All IID parts must be integers.")

    structure = nums[0]
    if structure <= 0:
        raise InvalidIIDError("Structure ID must be a positive integer.")

    object = nums[1]
    if object < 0:
        raise InvalidIIDError("Object ID must be 0 or positive.")

    indexes = nums[2:]  # may be empty, one or two elements

    return {
        "structure": structure,
        "object": object,
        "indexes": indexes
    }
