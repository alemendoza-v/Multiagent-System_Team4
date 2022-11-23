from flask import Flask, jsonify
import os
from models import SimulationModel, board

app = Flask(__name__)

# port = int(os.getenv('PORT', 8000))



@app.route('/run')
def run():
    # Run simulation
    parameters = {
    'cars': 7,
    'steps': 2000,
    'matrix': [
        [0, 1, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 1],
        [0, 0, 0, 0]
    ],
    }
    model = SimulationModel(parameters)
    results = model.run()

    return jsonify(board)

if __name__ == '__main__':
    app.run(debug=True)