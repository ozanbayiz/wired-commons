import warnings
import requests
import urllib.request
import random

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import geopandas as gpd
import rasterio as rio
from rasterio.warp import calculate_default_transform, reproject, Resampling, transform_bounds

import json
from io import BytesIO

import folium
from streamlit_folium import folium_static
import streamlit as st

import urllib.parse, urllib.request
import concurrent.futures

import gc

## Create Vector Layers
################################

vector_colors = [
    "black", "maroon", "red", "purple", "fuchsia", 
    "green", "lime", "olive", "yellow", "navy", "blue", 
    "teal", "aqua", "orange", "aquamarine", "blueviolet", 
    "brown", "chartreuse", "chocolate", "coral", "crimson", 
    "cyan", "darkblue", "darkcyan", "darkgoldenrod", 
    "darkgreen", "darkkhaki", "darkmagenta", "darkolivegreen", 
    "darkorange", "darkorchid", "darkred", "darksalmon", 
    "darkseagreen", "darkturquoise", "darkviolet", "deeppink", 
    "deepskyblue", "dodgerblue", "firebrick", "forestgreen", 
    "gold", "goldenrod", "greenyellow", "hotpink", "indianred", 
    "indigo", "khaki", "lawngreen", "lightblue", "lightcoral", 
    "lightpink", "lightsalmon", "lightseagreen", "lightskyblue", 
    "limegreen", "magenta", "mediumaquamarine", "mediumblue", 
    "mediumorchid", "mediumpurple", "mediumseagreen", 
    "mediumslateblue", "mediumspringgreen", "mediumturquoise", 
    "mediumvioletred", "midnightblue", "orange", "orangered", 
    "orchid", "palegreen", "paleturquoise", "palevioletred", 
    "peru", "pink", "plum", "powderblue", "rebeccapurple", 
    "rosybrown", "royalblue", "saddlebrown", "salmon", 
    "sandybrown", "seagreen", "sienna", "skyblue", "slateblue", 
    "slategray", "springgreen", "steelblue", "tan", "thistle", 
    "tomato", "turquoise", "violet", "yellowgreen"
]

def fetch_geometries(base_url):
    print(f"fetching geometries for {base_url}")
    url_string = base_url + "?f=json"
    j = urllib.request.urlopen(url_string)
    js = json.load(j)
    if 'error' in js:
        return
    max_records_count = int(js["maxRecordCount"])
    max_records_count = min(max_records_count, 800)
    # Get object ids of features
    where = "1=1"
    url_string = base_url + "/query?where={}&returnIdsOnly=true&f=json".format(where)
    j = urllib.request.urlopen(url_string)
    js = json.load(j)
    id_field = js["objectIdFieldName"]
    id_list = js["objectIds"]
    # this could be optimized maybe
    id_list.sort()
    num_of_records = len(id_list)
    request_number = 0
    # create URLs for requests
    url_strings = []
    for i in range(0, num_of_records, max_records_count):
        request_number += 1
        to_rec = i + (max_records_count - 1)
        if to_rec > num_of_records:
            to_rec = num_of_records - 1
        from_id = id_list[i]
        to_id = id_list[to_rec]
        where = '{} BETWEEN {} AND {}'.format(id_field, from_id, to_id)
        url_string = base_url + "/query?where={}&returnGeometry=true&outFields=" "&f=geojson".format(where, " ")
        url_strings.append(url_string)
    # specify helper function which does the fetching
    def load_features(urlstring):
        try:
            with warnings.catch_warnings(action='ignore'):
                resp = requests.get(urlstring, verify=False)
            data = resp.json()
            gdf = gpd.GeoDataFrame.from_features(data['features'], crs='EPSG:4326')
            return gdf
        except:
            print ('Failed to load {}'.format(urlstring))
    # thread pool to fetch features
    with concurrent.futures.ThreadPoolExecutor(max_workers=None) as executor:
        features_list = list(executor.map(load_features, url_strings))
    final_gdf = pd.concat(features_list)
    return final_gdf

def fetch_all_features(base_url):
    print(base_url)
    # Get record extract limit
    url_string = base_url + "?f=json"
    j = urllib.request.urlopen(url_string)
    js = json.load(j)
    if 'error' in js:
        return
    max_records_count = int(js["maxRecordCount"])
    max_records_count = min(max_records_count, 800)
    # Get object ids of features
    fields = "*"
    where = "1=1"
    url_string = base_url + "/query?where={}&returnIdsOnly=true&f=json".format(where)
    j = urllib.request.urlopen(url_string)
    js = json.load(j)
    id_field = js["objectIdFieldName"]
    id_list = js["objectIds"]
    # this could be optimized maybe
    id_list.sort()
    num_of_records = len(id_list)
    request_number = 0
    # create URLs for requests
    url_strings = []
    for i in range(0, num_of_records, max_records_count):
        request_number += 1
        to_rec = i + (max_records_count - 1)
        if to_rec > num_of_records:
            to_rec = num_of_records - 1
        from_id = id_list[i]
        to_id = id_list[to_rec]
        where = '{} BETWEEN {} AND {}'.format(id_field, from_id, to_id)
        url_string = base_url + "/query?where={}&returnGeometry=true&outFields={}&f=geojson".format(where, fields)
        url_strings.append(url_string)
    # specify helper function which does the fetching
    def load_features(urlstring):
        try:
            with warnings.catch_warnings(action='ignore'):
                resp = requests.get(urlstring, verify=False)
            data = resp.json()
            gdf = gpd.GeoDataFrame.from_features(data['features'], crs='EPSG:4326')
            return gdf
        except:
            print ('Failed to load {}'.format(urlstring))
    # thread pool to fetch features
    with concurrent.futures.ThreadPoolExecutor(max_workers=None) as executor:
        features_list = list(executor.map(load_features, url_strings))
    final_gdf = pd.concat(features_list)
    final_gdf = final_gdf[~final_gdf.geometry.is_empty]
    final_gdf['geometry'] = final_gdf['geometry'].buffer(0) # fix invalid geometries
    ## something to decrease resolution of geometries

    return final_gdf[~final_gdf.geometry.is_empty]

def fetch_geojson(url):
    geojson = requests.get(url).json()
    return geojson

def fetch_opentopo_geojson(url):
    information = requests.get(url).json()
    json_link = [x['href'] for x in information['links'] if x['rel'] == 'child' and 'raster' not in x['href']]
    if len(json_link) > 0:
        geojson = requests.get(json_link[0]).json()
        feature_collection = {
            "type": "FeatureCollection",
            "features": [
                geojson
            ]
        }
        return feature_collection

def create_vector_layer(geojson, dataset_title):
    if 'errors' in geojson:       
        return
    else:
        layer_color = random.choice(vector_colors)
        print(layer_color)
        style_function=lambda x: {
            'color':layer_color
        }
        layer = folium.GeoJson(
            geojson,
            name=dataset_title,
            style_function=style_function
        )
        del geojson
        gc.collect()
    return layer

## Create Raster Layers
################################

raster_cmaps = ['viridis', 'plasma', 'inferno', 'magma', 'cividis']

def fetch_raster_bytes(url):
    response = requests.get(url)
    return BytesIO(response.content)

def create_raster_layer(raster_bytes, dataset_name, downsample_data=True):
    with rio.open(raster_bytes) as src:
        nodata_value = src.nodata
        src_crs = src.crs
        # reproject bounds to EPSG:4326
        src_bounds = src.bounds
        minx, miny, maxx, maxy = transform_bounds(src_crs, 'EPSG:4326', *src_bounds)
        layer_bounds = ((miny, minx), (maxy, maxx))

        # reproject data to EPSG:3857
        transform, width, height = calculate_default_transform(
            src_crs, 'EPSG:3857', src.width, src.height, *src.bounds)

        data = np.empty((height, width), dtype=src.dtypes[0])

        reproject(
            source=rio.band(src, 1),
            destination=data,
            src_transform=src.transform,
            src_crs=src_crs,
            dst_transform=transform,
            dst_crs='EPSG:3857',
            resampling=Resampling.nearest
        )
        if downsample_data:
            data = data[::50, ::50].astype(np.float32)
        data[np.where(data==nodata_value)] = np.nan
        # create layer
        cmap = plt.get_cmap(random.choice(raster_cmaps))
        norm = plt.Normalize(vmin=np.nanmin(data), vmax=np.nanmax(data))
        image_data = cmap(norm(data))
        alpha_channel = np.where(np.isfinite(data), 255, 0)
        rgba_image_data = np.dstack((image_data[:, :, :3] * 255, alpha_channel)).astype(np.uint8)
        raster_layer = folium.raster_layers.ImageOverlay(
            name=dataset_name,
            image=rgba_image_data,
            bounds=layer_bounds,
            transparent=True,
            fmt="image/png8",
            tiled=True,
            interactive=True,
            cross_origin=False,
            zindex=1,
        )
        del raster_bytes
        gc.collect()
    return raster_layer

def create_layer(dataset):
    layer = None
    # OpenTopography
    if dataset['owner_org'] == 'e2d487d1-6973-487c-bb20-a11744d9e1ea':
        with st.spinner(f'fetching data for {dataset["title"]}'):
            gdf = fetch_opentopo_geojson(dataset['url'])
        with st.spinner(f'creating layer for {dataset["title"]}'):
            layer = create_vector_layer(gdf, dataset['title'])

    else:
        for resource in dataset['resources']:
            if resource['url']:
                # for FeatureServices
                if 'REST' in resource['format']:
                    print("Trying rest api")
                    if resource['url'][-1] in '0123456789': # make sure it's a valid Feature Service
                        with st.spinner(f'fetching data for {dataset["title"]}'):
                            try: 
                                gdf = fetch_geometries(resource['url'])
                            except: # there seems to be a lot that can go wrong :(
                                continue
                        with st.spinner(f'creating layer for {dataset["title"]}'):
                            if gdf is not None:
                                layer = create_vector_layer(gdf, dataset['title']) 
                    
                # for GeoJSONs
                elif resource['format'] == 'GeoJSON': 
                    print("trying geojson")
                    with st.spinner(f'fetching data for {dataset["title"]}'):
                        geojson = fetch_geojson(resource['url'])
                        print(resource['url'])
                    with st.spinner(f'creating layer for {dataset["title"]}'):
                        layer = create_vector_layer(geojson, dataset['title'])

                #For Rasters
                elif resource['format'] == 'GeoTIFF' or resource['format'] == 'TIFF':
                    with st.spinner(f'fetching data for {dataset["title"]}'):
                        raster_bytes = fetch_raster_bytes(resource['url'])
                    with st.spinner(f'creating layer for {dataset["title"]}'):
                        layer = create_raster_layer(raster_bytes, dataset['title'])
                
                if layer is not None:
                    break
    return layer


## Map Helpers
################################

def reset_map(location=[37.1661, -119.44944]):
    ## what if we preloaded the datasets that we already have? 
    ## Add them here so the map is initialized with the datasets
    map = folium.Map(location=location, zoom_start=4)   
    return map

def update_map(dataset, map_placeholder, error_placeholder):
    active_layers = st.session_state.active_layers
    cached_layers = st.session_state.cached_layers
    dataset_id = dataset['id']

    if dataset_id in active_layers:
        del st.session_state.active_layers[dataset_id]
    else:
        # get the layer
        if dataset_id in cached_layers:
            active_layers[dataset_id] = cached_layers[dataset_id]
        else:
            with error_placeholder:
                layer = create_layer(dataset)
                if layer:
                    active_layers[dataset_id] = layer
                    cached_layers[dataset_id] = layer
                else:
                    st.error(f'Layer for {dataset['title']} could not be fetched', icon="🚨")
    
    st.session_state.active_layers = active_layers
    st.session_state.cached_layers = cached_layers

    m = reset_map()
    with error_placeholder:
        with st.spinner("loading map..."):
            for dataset_id in active_layers:
                print(f"added layer {active_layers[dataset_id]} to map")
                active_layers[dataset_id].add_to(m)

            folium.plugins.Fullscreen(
                position='topright',
                title='Full Screen',
                title_cancel='Exit Full Screen',
                force_separate_button=True
            ).add_to(m)
            if len(active_layers) > 1:
                folium.LayerControl().add_to(m)
    with map_placeholder:
        folium_static(m)
    st.session_state.map = m     