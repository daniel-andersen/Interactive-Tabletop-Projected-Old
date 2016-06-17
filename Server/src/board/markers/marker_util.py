from default_marker import DefaultMarker
from triangle_marker import TriangleMarker


def create_marker_from_name(name):
    if name is None:
        return DefaultMarker()
    if name.upper() == "DEFAULT":
        return DefaultMarker()
    if name.upper() == "TRIANGLE":
        return TriangleMarker()
    return DefaultMarker()
