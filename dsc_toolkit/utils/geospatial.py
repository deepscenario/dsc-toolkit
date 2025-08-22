from pyproj import CRS, Proj


def get_utm_crs(zone_number: int, hemisphere: str) -> CRS:
    assert hemisphere in ('N', 'S'), f'Invalid hemisphere: {hemisphere}'
    return Proj(proj='utm', zone=zone_number, datum='WGS84', ellps='WGS84', units='m', north=hemisphere == 'N').crs
