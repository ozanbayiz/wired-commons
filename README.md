# WIRED Commons Map Interface
<p align="center">
  <img src="https://media.licdn.com/dms/image/v2/D5622AQFbifiOtwXzZA/feedshare-shrink_2048_1536/feedshare-shrink_2048_1536/0/1720889977150?e=2147483647&v=beta&t=rHvMu_muXaJx7LidB4Ekrtw1gx5otLGFv2EGGhWenqI" />
</p>

A web app to find, review, and display geospatial data from the WIFIRE Commons Data Catalog on an interactive map interface.

---

The [WIFIRE Commons Data Catalog](https://wifire-data.sdsc.edu/dataset) is home to a wide collection of wildfire and environmental datasets. It promotes the FAIR data guidelines of findability, accessibility, interoperability, and reusability. However, the interoperability of the datasets it federates has not been widely tested for grid resilience use cases.

<p align="center">
  <img src="https://wifire.ucsd.edu/sites/default/files/gbb-uploads/WIFIRE_COMMONS_SM_RES_1_1.png" />
</p>

This app is one of my projects for the 2024 WIRED Grid Resilience Symposium. It demonstrates the interoperability of the WIFIRE Commons Data Catalog by providing an easy map interface for researchers to view spatial data.

Currently, the only supported file types are `Esri REST`, `ArcGIS GeoServices REST API`, `GeoJSON`, `GeoTIFF`, and `TIFF`

Special thanks to Katie O'Laughlin for their guidance as I navigated the development of this project.

<p align="center">
  <img style="max-width: min(50vw, 1000px);" src="./assets/map-interface-demo.png" />
</p>

<p align="center"> <a href="https://wired-commons.streamlit.app/">try it out!</a></p>