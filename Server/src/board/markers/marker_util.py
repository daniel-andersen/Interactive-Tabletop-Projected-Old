from board.markers.default_marker import DefaultMarker
from board.markers.triangle_marker import TriangleMarker


def create_marker_from_name(name=None, marker_id=-1):
    if name is None:
        return DefaultMarker(marker_id)
    if name.upper() == "DEFAULT":
        return DefaultMarker(marker_id)
    if name.upper() == "TRIANGLE":
        return TriangleMarker(marker_id)
    return DefaultMarker(marker_id)


def marker_result_list_to_server_output(marker_result_list):
    """
    Transforms marker results to usable server output.

    :param marker_result_list: Marker result list
    :return: List of transformed dictionaries
    """
    return [marker_result_to_server_output(marker_result) for marker_result in marker_result_list]


def marker_result_to_server_output(marker_result):
    """
    Transforms marker result to usable server output.

    :param marker_result: Marker result
    :return: Transformed dictionary
    """
    return {k: v for k, v in marker_result.items() if k != "rawContour"}
