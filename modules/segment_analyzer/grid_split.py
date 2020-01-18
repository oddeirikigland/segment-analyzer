from math import cos


def split_bound_area(bounds):
    sw_lat, sw_lng, ne_lat, ne_lng = bounds
    lat_split_grid = sw_lat + ((ne_lat - sw_lat) / 2)
    bounds1 = [sw_lat, sw_lng, lat_split_grid, ne_lng]
    bounds2 = [lat_split_grid, sw_lng, ne_lat, ne_lng]
    return bounds1, bounds2


def smaller_grid_generator(big_bound, splits=3):
    out_bounds = [big_bound]
    if splits <= 1:
        return big_bound
    for _ in range(splits):
        to_split = out_bounds.pop(0)
        out_bounds += split_bound_area(to_split)
    return out_bounds


def get_degrees(value, radius):
    return radius * (360 / (cos(value) * 40075))


def create_square_around_point(latitude, longitude, radius=10):
    latitude_degrees = get_degrees(latitude, radius)
    longitude_degrees = get_degrees(longitude, radius)

    sw_lat = latitude - latitude_degrees
    sw_lng = longitude + longitude_degrees
    ne_lng = longitude - longitude_degrees
    ne_lat = latitude + latitude_degrees
    return sw_lat, sw_lng, ne_lat, ne_lng


def main():
    res = smaller_grid_generator([10, 10, 20, 20], 3)
    print(res)


if __name__ == "__main__":
    main()
