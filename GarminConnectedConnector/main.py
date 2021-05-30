from flask import Flask
import garmin_plots
import io
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from flask import Response, request

app = Flask(__name__)


@app.route('/plot.png')
def plot_png():
    activity = request.args.get('activity')
    fig = garmin_plots.running_plot(activity)
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')


@app.route("/")
def hello():
    return """
    <img src="/plot.png?activity=running" alt="my plot">
    <img src="/plot.png?activity=cycling" alt="my plot">
    """


if __name__ == '__main__':
    app.run()