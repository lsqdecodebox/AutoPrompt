from flask import Flask, render_template, request, jsonify
from prompt_optimizer import PromptOptimizer

app = Flask(__name__)
optimizer = PromptOptimizer()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/optimize', methods=['POST'])
def optimize():
    data = request.json
    example_text = data.get('example_text')
    expected_output = data.get('expected_output')
    target_text = data.get('target_text', '')
    last_prompt = data.get('last_prompt', '无')
    
    try:
        result = optimizer.optimize(example_text, expected_output, target_text, last_prompt)
        return jsonify({
            'status': 'success',
            'data': result
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)