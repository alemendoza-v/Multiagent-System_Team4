from flask import Flask, jsonify
from model import SimulationModel
import os

app = Flask(__name__, static_url_path='')

port = int(os.getenv('PORT', 8000))

@app.route('/run/<int:cars>')
def run(cars):
    # Run simulation
    parameters = {
    'cars': cars,
    'steps': 7000,
    'matrix': [
        [0, 1, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 1],
        [0, 0, 0, 0]
    ]
    }

    model = SimulationModel(parameters)
    results = model.run()
    return jsonify(results.reporters.results.to_dict()[0])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port, debug=False)