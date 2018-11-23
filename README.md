# Polyhash

Python library for converting polygons to geohashes and vice versa. This library was inspired by [polygon-geohasher](https://github.com/Bonsanto/polygon-geohasher). This also requires [python-geohash](https://github.com/hkwi/python-geohash) and [Shapely](https://github.com/Toblerity/Shapely). Additionally, this was taken a step further to include and require [georaptor](https://github.com/ashwin711/georaptor) for the compression of geohashes.

## Prerequisites

- Python >= 3.6
- Shapely >= 1.6.3
- python-geohash >= 0.8.5
- georaptor >= 2.0.3

```
pip install requirements.txt
```

## Installing

```
$ pip install polyhash
```

## Usage

```
$ from polyhash import geohash_to_polygon
$ geohash_to_polygon('www123')
> <shapely.geometry.polygon.Polygon at 0x11f19d588>
$
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details
