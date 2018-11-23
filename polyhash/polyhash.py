import os
from collections import deque, defaultdict

import geohash
from shapely.geometry import Polygon
from shapely.ops import unary_union
from georaptor import compress as gcompress

def geohash_to_polygon(hashcode):
    """Create polygon from a geohash string.

    Given the hashcode for a geohash, this function takes the bounding box
    of the geohash and constructs a Shapely polygon from the coordinates.

    Parameters
    ----------
    hashcode : str
        The string representation of a geohash.

    Returns
    -------
    Shapely polygon
        A Shapely polygon representation of the geohash.

    """
    bbox = geohash.bbox(hashcode)
    n, e, w, s = bbox['n'], bbox['e'], bbox['w'], bbox['s']
    coords = [(w,s), (e,s), (e,n), (w,n), (w,s)]
    return Polygon(coords)


def polygon_to_geohashes(polygon, precision=6, strict=False, compress=False,
                         border_mode='intersect'):
    """Converts a polygon to a neighborhood of geohashes.

    Given a Shapely polygon instance and a precision, identifies which
    geohashes are inside of or intersects the polygon depending on how
    strict the setting is. Resulting geohashes can be further compressed
    by one precision lower.

    Parameters
    ----------
    polygon : Shapely polygon
        Shapely polygon instance.
    precision : int
        Minimum precision of geohashes needed. If compress is True, this
        will become the maximum. The default is 6.
    strict : bool, optional
        If True, geohashes that fall on the border of the polygon are isolated
        from those that completely fall inside the polygon. The default is
        False, which combines the inner polygons with the border polygons.
    compress : bool, optional
        If True, resulting geohashes that completely comprise the members of
        the higher precision geohash they belong to will be discarded in favor
        of their parent.
    border_mode : {'intersect', 'center'}, optional
        If 'center', border geohashes are determined only if their centroid
        falls inside the polygon. The default is 'intersect', which includes
        a geohash if it intersects any point in the polygon.

    Returns
    -------
    dictionary
        Returns a dictionary of lists of inner and outer geohashes. If strict
        is True, an additional list is added for border geohashes.

    """
    envelope = polygon.envelope
    centroid = polygon.centroid

    inner_geohashes = set()
    outer_geohashes = set()
    border_geohashes = set()

    neighborhood = deque()
    neighborhood.append(geohash.encode(centroid.y, centroid.x, precision))

    while neighborhood:
        curr_geohash = neighborhood.popleft()
        not_in_inner = (curr_geohash not in inner_geohashes)
        not_in_outer = (curr_geohash not in outer_geohashes)
        not_in_border = (curr_geohash not in border_geohashes)

        if not_in_inner and not_in_outer and not_in_border:
            curr_polygon = geohash_to_polygon(curr_geohash)
            intersects_envelope = envelope.intersects(curr_polygon)

            if intersects_envelope:
                if border_mode == 'intersect':
                    inside_polygon = polygon.contains(curr_polygon)
                elif border_mode == 'center':
                    centroid = curr_polygon.centroid
                    inside_polygon = polygon.contains(centroid)
                intersects_polygon = polygon.intersects(curr_polygon)
                if strict:
                    if inside_polygon:
                        inner_geohashes.add(curr_geohash)
                    elif intersects_polygon:
                        border_geohashes.add(curr_geohash)
                    else:
                        outer_geohashes.add(curr_geohash)
                else:
                    if intersects_polygon:
                        inner_geohashes.add(curr_geohash)
                    else:
                        outer_geohashes.add(curr_geohash)
                for neighbor in geohash.neighbors(curr_geohash):
                    not_in_inner = (neighbor not in inner_geohashes)
                    not_in_outer = (neighbor not in outer_geohashes)
                    not_in_border = (neighbor not in border_geohashes)
                    if not_in_inner and not_in_outer and not_in_border:
                        neighborhood.append(neighbor)

    if compress and precision > 1:
        minprec = precision - 1
        inner_geohashes = gcompress(inner_geohashes, minprec, precision)
        outer_geohashes = gcompress(outer_geohashes, minprec, precision)
        if len(border_geohashes) > 0:
            border_geohashes = gcompress(border_geohashes, minprec, precision)

    res_dict = {
        'inner': inner_geohashes,
        'outer': outer_geohashes,
        'border': border_geohashes
    }

    return res_dict


def geohashes_to_polygon(neighborhood):
    """Creates a polygon from a list of geohashes.

    Converts a neighborhood of geohashes (doesn't have to be adjacent) to a
    Shapely polygon/multipolygon instance.

    Parameters
    ----------
    neighborhood : list
        List of geohash strings (hashcodes)). Geohashes don't need to be
        adjacent nor should they be of same precision.

    Returns
    -------
    Shapely polygon/multipolygon
        If neighborhood contains contiguously adjacent geohashes, a polygon
        will be returned. Else, a multipolygon instance will be returned.

    """
    return unary_union([geohash_to_polygon(n) for n in neighborhood])


def polygons_to_geohashes(polygons, precision=6, strict=False, compress=False):
    """Creates an enumerate object of geohash lists from multiple polygons.

    The precision, strict, and compress parameters will be applied to all
    polygons in the iterable passed, with the enumeration starting with 0.

    Parameters
    ----------
    polygons : list
        List of Shapely polygons.
    precision : int
        Desired precision of resulting geohashes. The default is 6, and the
        maximum is 12. If compress is True, this becomes the maximum.
    strict : bool, optional
        If True, geohashes that fall on the border of the polygon are isolated
        from those that completely fall inside the polygon. The default is
        False, which combines the inner polygons with the border polygons.
    compress : bool, optional
        If True, resulting geohashes that completely comprise the members of
        the higher precision geohash they belong to will be discarded in favor
        of their parent.

    Returns
    -------
    enumerate object
        Returns an enumerate object that follows the order of the
        iterable passed in for the polygon parameter.
    """

    max_prec = min(precision, 12)
    list_of_geohashes = []
    for polygon in polygons:
        geohashes = polygon_to_geohashes(polygon, max_prec, strict, compress)
        list_of_geohashes.append(geohashes)
    enumerated = enumerate(list_of_geohashes)
    return enumerated
