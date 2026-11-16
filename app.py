# -*- coding: utf-8 -*-
from flask import Flask, render_template, jsonify, request
from generateur import generate_puzzle, reset_used_words

app = Flask(__name__)


@app.route('/')
def index():
    """Sert la page principale."""
    return render_template('index.html')


@app.route('/api/puzzle/<int:level>')
def api_puzzle(level):
    """
    Génère et retourne une grille pour le niveau demandé.
    GET /api/puzzle/0 → niveau 1
    """
    puzzle = generate_puzzle(level)
    return jsonify(puzzle)


@app.route('/api/reset', methods=['POST'])
def api_reset():
    """Réinitialise le filtre anti-doublon."""
    reset_used_words()
    return jsonify({'ok': True})


if __name__ == '__main__':
    # En production, utiliser gunicorn : gunicorn app:app
    app.run(debug=True, host='0.0.0.0', port=5000)