from dash import Dash, dcc, html, Input, Output
import plotly.figure_factory as ff
import json
from src.config import lamdba_
from src.manipulate import get_stats


def plot_hist():
    """
    plots histogram of multiple observation time thresholds.
    :return: Histogram plotted in-browser.
    """
    app = Dash(__name__)

    app.layout = html.Div([
        html.H4('Number of Asteroid Observations'),
        dcc.Graph(id="graph"),
        html.P("Threshold (hrs):"),
        dcc.Slider(id="idx", min=0.25, max=12, value=0.25, step=0.25,
                   marks={0.25: '0.25', 24: '12'}, tooltip={'always_visible': True})
    ])

    @app.callback(
        Output("graph", "figure"),
        Input("idx", "value")
    )
    def display_hist(idx):
        """
        displays plot in browser.
        :param idx: index
        :return: figure
        """

        with open("data/sample.json", "r") as infile:
            dictionary = json.load(infile)
        orig_data = dictionary[str(int(idx*60*60))]

        mean, med, st_dev, aggregate, range_ = get_stats(orig_data, lamdba_)
        if (mean - st_dev) > 6**lamdba_:
            fig = ff.create_distplot([orig_data], ["# of Observations"], bin_size=10, show_rug=True, colors=['green'])
        else:
            fig = ff.create_distplot([orig_data], ["# of Observations"], bin_size=10, show_rug=True, colors=['red'])
        fig.update_layout(xaxis=dict(tickmode='linear', tick0=0, dtick=100))
        fig.add_annotation(x=200, y=0.02, text=f"Mean: {mean}", showarrow=False, yshift=10)
        fig.add_annotation(x=200, y=0.018, text=f"Median: {med}", showarrow=False, yshift=10)
        fig.add_annotation(x=200, y=0.016, text=f"σ: {st_dev}", showarrow=False, yshift=10)
        fig.add_annotation(x=200, y=0.014, text=f"Aggregate: {aggregate}", showarrow=False, yshift=10)
        fig.add_annotation(x=200, y=0.012, text=f"Range: {range_[0]}-{range_[1]}", showarrow=False, yshift=10)
        return fig

    app.run_server(debug=True)


if __name__ == "__main__":
    plot_hist()
