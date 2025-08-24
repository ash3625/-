from flask import Flask, request, jsonify, render_template
import json
import os
from collections import Counter

app = Flask(__name__)
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

game_state = {
    "board_6": [],
    "board_2_1": [],
    "board_2_2": []
}

@app.route('/')
def index():
    return render_template('index.html')

def rebuild_2_board(board_6_results):
    filtered_results = [r['result'] for r in board_6_results if r['result'] in ['P', 'B']]
    
    if not filtered_results:
        return [], []

    board_2_results = []
    current_col = []
    
    for result in filtered_results:
        if not current_col or current_col[-1]['result'] != result:
            if current_col:
                board_2_results.append(current_col)
            current_col = [{'result': result, 'highlight': False}]
        elif len(current_col) < 2:
            current_col.append({'result': result, 'highlight': False})
        else:
            continue
    
    if current_col:
        board_2_results.append(current_col)
    
    max_cols_2_1 = 30
    board_2_1 = []
    board_2_2 = []
    
    for i, col in enumerate(board_2_results):
        highlight = False
        if len(col) == 2:
            highlight = True
        
        for item in col:
            item['highlight'] = highlight
            
        if i < max_cols_2_1:
            board_2_1.append(col)
        else:
            board_2_2.append(col)

    return board_2_1, board_2_2

@app.route('/add_round', methods=['POST'])
def add_round():
    global game_state
    data = request.json
    result = data.get('result')
    
    if result and result in ['P', 'B', 'T', 'S', 'D']:
        game_state["board_6"].append({'result': result})
        game_state["board_2_1"], game_state["board_2_2"] = rebuild_2_board(game_state["board_6"])
        predictions = {} # 예측 로직을 프론트엔드로 옮김
        return jsonify({
            "success": True, 
            "board_6": game_state["board_6"],
            "board_2_1": game_state["board_2_1"],
            "board_2_2": game_state["board_2_2"],
            "predictions": predictions
        })
    else:
        return jsonify({"success": False, "error": "Invalid result"}), 400

@app.route('/get_game_state', methods=['GET'])
def get_game_state():
    global game_state
    predictions = {} # 예측 로직을 프론트엔드로 옮김
    return jsonify({
        "success": True, 
        "board_6": game_state["board_6"],
        "board_2_1": game_state["board_2_1"],
        "board_2_2": game_state["board_2_2"],
        "predictions": predictions
    })

@app.route('/delete_last', methods=['POST'])
def delete_last():
    global game_state
    if game_state["board_6"]:
        game_state["board_6"].pop()
        game_state["board_2_1"], game_state["board_2_2"] = rebuild_2_board(game_state["board_6"])
        predictions = {} # 예측 로직을 프론트엔드로 옮김
        return jsonify({
            "success": True, 
            "board_6": game_state["board_6"],
            "board_2_1": game_state["board_2_1"],
            "board_2_2": game_state["board_2_2"],
            "predictions": predictions
        })
    else:
        return jsonify({"success": False, "error": "No results to delete"}), 400

@app.route('/reset', methods=['POST'])
def reset_game():
    global game_state
    game_state = {
        "board_6": [],
        "board_2_1": [],
        "board_2_2": []
    }
    predictions = {} # 예측 로직을 프론트엔드로 옮김
    return jsonify({
        "success": True,
        "message": "게임이 초기화되었습니다.",
        "board_6": game_state["board_6"],
        "board_2_1": game_state["board_2_1"],
        "board_2_2": game_state["board_2_2"],
        "predictions": predictions
    })

if __name__ == '__main__':
    app.run(debug=True)
