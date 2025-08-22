import argparse
import os

import folium
import pandas as pd
from pyproj import CRS, Transformer

from dsc_toolkit.utils.generic import check_recording_in_dataset, filter_by_frame_range, filter_by_track_ids
from dsc_toolkit.utils.geospatial import get_utm_crs
from dsc_toolkit.utils.io import load_data_meta


def augment_with_lonlatalt(anns_df: pd.DataFrame, data_meta: dict) -> pd.DataFrame:
    reference_utm = data_meta['reference_utm']
    utm_crs = get_utm_crs(*reference_utm['zone'])
    lonlat_crs = CRS('EPSG:4326')
    transformer = Transformer.from_crs(utm_crs, lonlat_crs, always_xy=True)

    x_offset, y_offset, z_offset = reference_utm['offset']
    longitudes, latitudes = transformer.transform(anns_df['translation_x'] + x_offset,
                                                  anns_df['translation_y'] + y_offset)

    anns_df['longitude'] = longitudes
    anns_df['latitude'] = latitudes
    anns_df['altitude'] = anns_df['translation_z'] + z_offset
    return anns_df


def create_folium_map(anns_df: pd.DataFrame) -> folium.Map:
    folium_map = folium.Map(location=[anns_df['latitude'].iloc[0], anns_df['longitude'].iloc[0]], zoom_start=18,
                            tiles=None)
    folium.TileLayer('OpenStreetMap', name='OpenStreetMap').add_to(folium_map)

    for track_id, group in anns_df.groupby('track_id'):
        track_points = list(zip(group['latitude'], group['longitude']))
        polyline = folium.PolyLine(track_points, weight=3, opacity=0.7, popup=f'track_id={track_id}')
        polyline.add_to(folium_map)

    return folium_map


def plot_georeferenced_anns(
    data_dir: str,
    recording_id: str,
    save_dir: str,
    track_ids: list[int] | None = None,
    frame_range: tuple[int, int] | None = None,
) -> None:
    data_meta = load_data_meta(data_dir)
    check_recording_in_dataset(data_meta, recording_id)

    anns_path = os.path.join(data_dir, 'annotations', recording_id, 'annotations.parquet')
    anns_df = pd.read_parquet(anns_path)

    if track_ids is not None:
        anns_df = filter_by_track_ids(anns_df, track_ids)

    if frame_range is not None:
        anns_df = filter_by_frame_range(anns_df, frame_range)

    assert len(anns_df) > 0, 'No annotations to visualize'

    anns_df = augment_with_lonlatalt(anns_df, data_meta)
    folium_map = create_folium_map(anns_df)

    os.makedirs(save_dir, exist_ok=True)
    save_html_path = os.path.join(save_dir, 'annotations_map.html')
    folium_map.save(save_html_path)
    print(f'Map saved to {save_html_path}')


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Script to visualize the provided annotations on a map')
    parser.add_argument('--data_dir', help='Directory that contains the released data', type=str, required=True)
    parser.add_argument('--recording', help='Recording to plot', type=str, dest='recording_id', required=True)
    parser.add_argument('--save_dir', help='Directory where the rendered plot is saved', type=str, required=True)
    parser.add_argument('--track_ids', help='Filter annotations by track ids', type=int, nargs='+', default=None)
    parser.add_argument('--frame_range', help='Filter annotations with frame id range', type=int, nargs=2, default=None)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    plot_georeferenced_anns(**vars(args))


if __name__ == '__main__':
    main()
