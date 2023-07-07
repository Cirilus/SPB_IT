from bokeh.io import save, show, curdoc
from bokeh.layouts import column
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from bokeh.embed import json_item, file_html
from bokeh.models import Plot, Range1d, MultiLine, Circle, HoverTool, TapTool, BoxSelectTool, ResetTool, WheelZoomTool, \
    ColumnDataSource
from bokeh.palettes import Spectral4
from bokeh.plotting import figure, from_networkx
import networkx as nx
from pydantic import BaseModel
from starlette.responses import HTMLResponse


app = FastAPI()
templates = Jinja2Templates(directory="templates")


G = nx.karate_club_graph()
plot = Plot(width=400, height=400,
            x_range=Range1d(-1.1, 1.1), y_range=Range1d(-1.1, 1.1))

graph_renderer = from_networkx(G, nx.spring_layout, scale=1, center=(0, 0))
graph_renderer.node_renderer.glyph = Circle(size=15, fill_color=Spectral4[0])
graph_renderer.edge_renderer.glyph = MultiLine(line_color="#CCCCCC", line_alpha=0.8, line_width=1)
plot.renderers.append(graph_renderer)

hover_tool = HoverTool(tooltips=[("Node", "@index")])
tap_tool = TapTool()
box_select_tool = BoxSelectTool()
reset_tool = ResetTool()
wheel_zoom_tool = WheelZoomTool()

plot.add_tools(hover_tool, tap_tool, box_select_tool, reset_tool, wheel_zoom_tool)



class AddNodeRequest(BaseModel):
    pass


@app.get("/")
async def index(request: Request):
    html = file_html(plot)
    return HTMLResponse(content=html)


# Создание маршрута для обработки запросов на добавление узла
@app.post('/add_node')
async def add_node(request: AddNodeRequest):
    global G, graph_renderer

    node_index = G.number_of_nodes()
    G.add_node(node_index)
    graph_renderer.node_renderer.data_source.data['index'].append(node_index)
    graph_renderer.node_renderer.data_source.data['fill_color'].append(Spectral4[node_index % len(Spectral4)])
    graph_renderer.node_renderer.data_source.data = dict(graph_renderer.node_renderer.data_source.data)

    return {'status': 'success', 'message': f'Added node {node_index}'}


# Запуск FastAPI сервера
if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app)
