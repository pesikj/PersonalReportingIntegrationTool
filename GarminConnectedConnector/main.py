import io

from flask import Flask
from flask import Response, request
from flask import render_template
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

import garmin_plots

app = Flask(__name__)

@app.route("/reload/", methods=['POST'])
def reload_data():
    from_index = int(request.form['from'])
    to_index = int(request.form['to'])
    garmin_plots.garmin_connector.load_data(from_index, to_index)
    return "index"

@app.route('/plot.png')
def plot_png():
    activity = request.args.get('activity')
    fig = garmin_plots.garmin_connector.running_plot(activity)
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')


@app.route("/")
def hello():
    activities_metadata = garmin_plots.garmin_connector.activities_metadata
    return render_template('index.html', title='Home', activities_metadata=activities_metadata)


if __name__ == '__main__':
    app.run()
