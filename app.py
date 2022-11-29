from flask import Flask, jsonify
from model import SimulationModel

app = Flask(__name__)

# port = int(os.getenv('PORT', 8000))

@app.route('/run')
def run():
    # Run simulation
    parameters = {
    'cars': 5,
    'steps': 3000,
    'matrix': [
        [0, 1, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 1],
        [0, 0, 0, 0]
    ]
    }

    model = SimulationModel(parameters)
    results = model.run()
    return results.reporters.results.to_dict()[0]

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)