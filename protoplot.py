import numpy as np

from bokeh.layouts import column, row
from bokeh.models import ColumnDataSource, DataTable, TableColumn, PointDrawTool, Button
from bokeh.plotting import figure
from bokeh.server.server import Server


def compute(source_points, steps):
    x = list(np.linspace(-3, 3, steps))
    points = source_points.data
    points_x = [float(v) for v in points["x"]]
    points_y = [float(v) for v in points["y"]]
    a, b, c = fit_parabola(points_x, points_y)
    y = [a * v ** 2 + b * v + c for v in x];
    return dict(x=x, y=y)


def fit_parabola(x, y):
    """Fits the equation "y = ax^2 + bx + c" given exactly 3 points as two
    lists or arrays of x & y coordinates"""
    if len(x) > 3 or len(y) > 3:
        print("3 points max : only the first 3 points will be considered")
        x = x[:3]
        y = y[:3]
    A = np.zeros((3, 3), dtype=np.float)
    A[:, 0] = [v ** 2 for v in x]
    A[:, 1] = x
    A[:, 2] = 1
    a, b, c = np.linalg.solve(A, y)
    return a, b, c


def modify_doc(doc):
    initial_points = {"x": [0, 1, 2], "y": [1, 3, 4]}
    source_points = ColumnDataSource(initial_points)
    source_line_rough = ColumnDataSource(compute(source_points, 7))
    source_line_smooth = ColumnDataSource(compute(source_points, 100))

    plot = figure()
    line_rough = plot.line('x', 'y', source=source_line_rough, line_dash = "dotted")
    line_smooth = plot.line('x', 'y', source=source_line_smooth, line_color = "green")
    circles = plot.circle('x', 'y', source=source_points,
                          size=10,
                          nonselection_fill_alpha=0.5,
                          nonselection_fill_color="blue",
                          nonselection_line_color="firebrick",
                          nonselection_line_alpha=1.0,
                          selection_fill_alpha=0.9,
                          selection_fill_color="red",
                          selection_line_color="firebrick"
                          )

    plot2 = figure()
    line2 = plot2.line('y', 'x', source=source_line_smooth, line_width=5)
    line2.glyph.line_color = "green"

    def recompute():
        source_line_smooth.data = compute(source_points, 100)
        line_smooth.glyph.line_dash = [1, 0]
        line_smooth.glyph.line_color = "green"
        line2.glyph.line_color = "green"

    def update_data(attr, old, new):
        source_line_rough.data = compute(source_points, 5)
        line_smooth.glyph.line_dash = [6, 3]
        line_smooth.glyph.line_color = "red"
        line2.glyph.line_color = "red"

    draw_tool = PointDrawTool(renderers=[circles])
    plot.add_tools(draw_tool)
    plot.toolbar.active_tap = draw_tool

    source_points.on_change("data", update_data)

    columns = [TableColumn(field="x", title="x"),
               TableColumn(field="y", title="y")]
    table_points = DataTable(source=source_points, columns=columns, editable=True)
    button = Button(label="Recompute")
    button.on_click(recompute)

    doc.add_root(column(button, row(plot, plot2), table_points))


# Setting num_procs here means we can't touch the IOLoop before now, we must
# let Server handle that. If you need to explicitly handle IOLoops then you
# will need to use the lower level BaseServer class.
server = Server({'/': modify_doc})
server.start()

if __name__ == '__main__':
    print('Opening Bokeh application on http://localhost:5006/')

    server.io_loop.add_callback(server.show, "/")
server.io_loop.start()
