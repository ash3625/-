from flask import Flask, request, jsonify, render_template, session
import os
from collections import Counter

# Flask 앱 초기화
app = Flask(__name__)

# 세션을 사용하기 위해 반드시 secret_key를 설정해야 합니다.
# os.environ.get()을 사용하여 환경 변수에서 SECRET_KEY를 가져옵니다.
# 만약 환경 변수가 설정되지 않았을 경우, 임의의 기본값을 사용합니다.
# 이 기본값은 배포 환경에서 반드시 안전한 값으로 변경해야 합니다.
app.secret_key = os.environ.get('SECRET_KEY', os.urandom(24))

# 2매표 보드를 재구성하는 함수
def rebuild_2_board(board_6_results):
    """
    6매표 결과를 기반으로 2매표 보드를 재구성합니다.
    'P' 또는 'B' 결과만 사용하여 보드를 만듭니다.
    """
    filtered_results = [r['result'] for r in board_6_results if r['result'] in ['P', 'B']]
    
    if not filtered_results:
        return [], []

    board_2_results = []
    current_col = []
    
    for result in filtered_results:
        # 새로운 컬럼 시작
        if not current_col or current_col[-1]['result'] != result:
            if current_col:
                board_2_results.append(current_col)
            current_col = [{'result': result, 'highlight': False}]
        # 동일한 결과가 연속되는 경우, 최대 2개까지만 추가
        elif len(current_col) < 2:
            current_col.append({'result': result, 'highlight': False})
        else:
            continue
    
    if current_col:
        board_2_results.append(current_col)
    
    # 보드 분리 로직 (30개 컬럼 기준)
    max_cols_2_1 = 30
    board_2_1 = []
    board_2_2 = []
    
    for i, col in enumerate(board_2_results):
        highlight = len(col) == 2
        for item in col:
            item['highlight'] = highlight
            
        if i < max_cols_2_1:
            board_2_1.append(col)
        else:
            board_2_2.append(col)

    return board_2_1, board_2_2

def get_user_game_state():
    """
    사용자의 세션에서 게임 상태를 가져옵니다.
    세션에 상태가 없으면 초기 상태를 설정하여 반환합니다.
    """
    if 'game_state' not in session:
        session['game_state'] = {
            "board_6": [],
            "board_2_1": [],
            "board_2_2": []
        }
    return session['game_state']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add_round', methods=['POST'])
def add_round():
    """
    사용자로부터 라운드 결과를 받아 게임 상태에 추가합니다.
    """
    user_state = get_user_game_state()
    data = request.json
    result = data.get('result')
    
    if result and result in ['P', 'B', 'T', 'S', 'D']:
        user_state["board_6"].append({'result': result})
        user_state["board_2_1"], user_state["board_2_2"] = rebuild_2_board(user_state["board_6"])
        session['game_state'] = user_state # 세션에 업데이트된 상태 저장
        predictions = {}
        return jsonify({
            "success": True, 
            "board_6": user_state["board_6"],
            "board_2_1": user_state["board_2_1"],
            "board_2_2": user_state["board_2_2"],
            "predictions": predictions
        })
    else:
        return jsonify({"success": False, "error": "Invalid result"}), 400

@app.route('/get_game_state', methods=['GET'])
def get_game_state():
    """
    현재 사용자의 게임 상태를 반환합니다.
    """
    user_state = get_user_game_state()
    predictions = {}
    return jsonify({
        "success": True, 
        "board_6": user_state["board_6"],
        "board_2_1": user_state["board_2_1"],
        "board_2_2": user_state["board_2_2"],
        "predictions": predictions
    })

@app.route('/delete_last', methods=['POST'])
def delete_last():
    """
    마지막 라운드 결과를 삭제합니다.
    """
    user_state = get_user_game_state()
    if user_state["board_6"]:
        user_state["board_6"].pop()
        user_state["board_2_1"], user_state["board_2_2"] = rebuild_2_board(user_state["board_6"])
        session['game_state'] = user_state # 세션에 업데이트된 상태 저장
        predictions = {}
        return jsonify({
            "success": True, 
            "board_6": user_state["board_6"],
            "board_2_1": user_state["board_2_1"],
            "board_2_2": user_state["board_2_2"],
            "predictions": predictions
        })
    else:
        return jsonify({"success": False, "error": "No results to delete"}), 400

@app.route('/reset', methods=['POST'])
def reset_game():
    """
    현재 사용자의 게임 상태를 초기화합니다.
    """
    if 'game_state' in session:
        del session['game_state']
    
    user_state = get_user_game_state()
    predictions = {}
    return jsonify({
        "success": True,
        "message": "게임이 초기화되었습니다.",
        "board_6": user_state["board_6"],
        "board_2_1": user_state["board_2_1"],
        "board_2_2": user_state["board_2_2"],
        "predictions": predictions
    })

if __name__ == '__main__':
    app.run(debug=True)
