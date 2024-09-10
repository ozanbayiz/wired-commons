import streamlit as st
import folium
import os
from streamlit_folium import st_folium, folium_static
from ckanapi import RemoteCKAN
from dotenv import load_dotenv

from utils import reset_map, update_map

load_dotenv('.env')

if 'ckan' not in st.session_state:
    st.session_state.ckan = RemoteCKAN('https://wifire-data.sdsc.edu/', apikey=os.environ['apiKey'])

st.markdown(
    """
    <style>
            .block-container {
                padding-top: 1rem;
                padding-bottom: 0rem;
                padding-left: 0rem;
                padding-right: 0rem;
                margin-bottom: 0rem;
                margin-left: 0rem;
                margin-right: 0rem;
            }
    </style>
    """, 
    unsafe_allow_html=True
)

st.markdown(
    """
    <style>
        section[data-testid="stSidebar"] {
            width: min(40vw, 500px) !important; # Set the width to your desired value
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title('WIRED Map Interface')

# The Map
map_placeholder = st.empty()
if 'map' not in st.session_state:  
    m = reset_map()
    folium.plugins.Fullscreen(
            position='topright',
            title='Full Screen',
            title_cancel='Exit Full Screen',
            force_separate_button=True
        ).add_to(m)
    st.session_state.map = m
    with map_placeholder:
        folium_static(st.session_state.map)
    # also create cache to store existing layers for quicker loading
    # # Maybe can look into compressing somehow?
    st.session_state.cached_layers = {}
    st.session_state.active_layers = {}
else:
    with map_placeholder:
        folium_static(st.session_state.map)

error_placeholder = st.empty()
data_tag_html = """
        <div style="
            margin: 0 auto;
            background-color: {0};
            border-radius: 20px;
            border: 1px solid #505158;
            font-size: 0.7em;
            text-align: center;
            color: white;
        ">{2}</div>
"""

horizontal_line_html = '<hr style="border: none; border-top: 1px solid #505158; padding: 0; margin: 0;">'
supported_filetypes = ["Esri REST","ArcGIS GeoServices REST API", "GeoJSON", "GeoTIFF", "TIFF"]
filetype_colors = {
    "Esri REST": "darkslategray",
    "ArcGIS GeoServices REST API": "darkslateblue", 
    "GeoJSON": "darkseagreen", 
    "GeoTIFF": "rebeccapurple", 
    "TIFF": "blueviolet"
}

# Sidebar
with st.sidebar:
    st.write("Also take a look at the [WIFIRE Commons Data Catalog](https://wifire-data.sdsc.edu/dataset).")
    # search box
    search = st.text_input('Search WIFIRE Data Catalog')
    if (len(search) > 0 and 'search' not in st.session_state) \
            or ('search' in st.session_state and st.session_state.search != search):
        st.session_state.search = search
        params = {
            'q':f'title:"{search}" AND (res_format:"Esri REST" OR res_format:"ArcGIS GeoServices REST API" OR res_format:GeoJSON OR res_format:GeoTIFF OR res_format:TIFF)',
            'start': 0,
            'rows': 100
        }
        with st.spinner('searching WIFIRE Data Catalog'):
            response = st.session_state.ckan.action.package_search(**params)
            st.session_state.search_results = response['results']
    # checkboxes
    if 'search_results' in st.session_state:
        with st.expander("Search Results: ", expanded=True):
            result_list = {}
            if st.session_state.search_results:
                for result in st.session_state.search_results:
                    col1, col2 = st.columns([2,1])
                    with col1:
                        st.markdown(horizontal_line_html, unsafe_allow_html=True)
                        for resource in result['resources']:
                            if resource['format'] in supported_filetypes:
                                format = resource['format']
                                st.markdown(
                                    data_tag_html.format(filetype_colors[format], filetype_colors[format], format),
                                    unsafe_allow_html=True
                                )
                                break
                        result_list[result['id']] = st.checkbox(
                            result['title'], 
                            key=result['id'], 
                            value=(result['id'] in st.session_state.active_layers),
                            on_change=update_map,
                            args=(result, map_placeholder, error_placeholder)
                        )
                    with col2:
                        st.markdown(horizontal_line_html, unsafe_allow_html=True)
                        st.markdown("<div></div>", unsafe_allow_html=True)
                        st.link_button("View Metadata", url='https://wifire-data.sdsc.edu/dataset/'+result['id']) 
            else:
                st.write("No results found.")
        st.session_state.result_list = result_list