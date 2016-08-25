from default_marker import DefaultMarker
from triangle_marker import TriangleMarker


def create_marker_from_name(name=None, marker_id=-1):
    if name is None:
        return DefaultMarker(marker_id)
    if name.upper() == "DEFAULT":
        return DefaultMarker(marker_id)
    if name.upper() == "TRIANGLE":
        return TriangleMarker(marker_id)
    return DefaultMarker(marker_id)


def filter_out_contour_from_marker_result_list(marker_result_list):
    """
    Filters out the "contour" key from marker result list.

    :param marker_result_list: Marker result list
    :return: List of dictionaries with "contour" key filtered out
    """
    return [filter_out_contour_from_marker_result(marker_result) for marker_result in marker_result_list]


def filter_out_contour_from_marker_result(marker_result):
    """
    Filters out the "contour" key from marker result.

    :param marker_result: Marker result
    :return: Dictionary with "contour" key filtered out
    """
    return {k: v for k, v in marker_result.iteritems() if k != "contour"}
