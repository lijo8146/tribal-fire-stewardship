"""Website and notebook figures; static charts and keyless interactive maps."""
import base64,io,html
import pandas as pd
import geopandas as gpd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import folium
from . import ROOT
from .io import history_manifest,sources
COLORS={"Wildfire":"#a34f32","Prescribed Fire":"#276b66","Wildland Fire Use":"#b58a35","Unknown":"#77766f"}
def source_link(key):
    source=next(s for s in sources() if s["id"]==key)
    return f"[{source['publisher']}: {source['title']}]({source['url']})"
def image_html(fig,alt,css="chart-image"):
    stream=io.BytesIO();fig.savefig(stream,format="png",dpi=140,bbox_inches="tight",facecolor="#faf8f2");plt.close(fig)
    return f'<img class="{css}" alt="{html.escape(alt)}" src="data:image/png;base64,{base64.b64encode(stream.getvalue()).decode()}">'
def history_chart(key):
    annual=pd.read_csv(ROOT/"data/processed"/f"history_{key}.csv")
    table=annual.pivot(index="year",columns="type",values="mapped_events")
    fig,ax=plt.subplots(figsize=(9,3.4));fig.patch.set_facecolor("#faf8f2");ax.set_facecolor("#faf8f2")
    bottom=table.iloc[:,0]*0
    for category,color in COLORS.items():
        ax.bar(table.index,table[category],bottom=bottom,label=category,color=color,width=.84);bottom+=table[category]
    ax.set_ylabel("Mapped events intersecting the window")
    ax.set_xlabel("Ignition year; zero means no event recorded in this snapshot")
    ax.spines[['top','right']].set_visible(False);ax.grid(axis="y",alpha=.18);ax.set_axisbelow(True)
    ax.legend(loc="upper left",ncol=2,fontsize=8)
    return image_html(fig,"Annual MTBS event counts in a regional context window, separated by recorded incident type")
def history_map(key):
    meta=history_manifest()["regions"][key]
    frame=gpd.read_file(ROOT/"data/processed"/f"history_{key}.geojson")
    if frame.empty:
        for column in ["type","name","year"]:frame[column]=pd.Series(dtype="str")
    west,south,east,north=meta["bounds"]
    m=folium.Map(tiles=None,control_scale=True,scrollWheelZoom=False)
    folium.TileLayer(tiles="https://tile.openstreetmap.org/{z}/{x}/{y}.png",attr='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',name="OpenStreetMap",max_zoom=19).add_to(m)
    folium.FeatureGroup(name="Data only (no basemap)",overlay=False,show=False).add_to(m)
    for category,color in COLORS.items():
        subset=frame[frame["type"]==category].copy()
        if subset.empty:continue
        subset["name"]=subset["name"].fillna("Unnamed public record").map(lambda x:html.escape(str(x)))
        folium.GeoJson(subset.__geo_interface__,name=category,style_function=lambda feature,c=color:{"color":c,"fillColor":c,"fillOpacity":.28,"weight":.7},tooltip=folium.GeoJsonTooltip(fields=["name","year","type"],aliases=["Public event name","Ignition year","Recorded type"])).add_to(m)
    folium.Rectangle([[south,west],[north,east]],color="#253c3a",weight=2,fill=False,dash_array="6 4",tooltip="Regional context window; not a Tribal boundary").add_to(m)
    m.fit_bounds([[south,west],[north,east]]);folium.LayerControl(collapsed=True).add_to(m)
    figure=folium.Figure(width="100%",height=440);m.add_to(figure)
    fig,ax=plt.subplots(figsize=(9,4.5));ax.set_facecolor("#faf8f2")
    for category,color in COLORS.items():
        subset=frame[frame["type"]==category]
        if len(subset):subset.plot(ax=ax,color=color,edgecolor=color,alpha=.45,linewidth=.25)
    ax.set(xlim=(west,east),ylim=(south,north),xlabel="Longitude",ylabel="Latitude",title=meta["label"]+" · public MTBS perimeters")
    ax.set_aspect(1/__import__("numpy").cos(__import__("numpy").deg2rad((south+north)/2)))
    return '<div class="interactive-map">'+figure._repr_html_()+'</div>'+image_html(fig,"Printable regional public-fire perimeter map; no background tiles","print-map")
def region_brief(key):
    meta=history_manifest()["regions"][key]
    counts="; ".join(f"{kind}: {number:,}" for kind,number in meta["by_type"].items())
    return f"**{meta['mapped_events']:,} distinct mapped events intersect this window.** {counts}.\n\n{meta['note']}"
