from flask import Flask, request, jsonify, render_template_string
import asyncio
from zuora import getzuoraStripe1

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Zuora Checker</title>
    <style>
        body { background: #0d0d0d; color: #eee; font-family: monospace; display: flex; justify-content: center; padding: 40px; }
        .box { width: 500px; }
        h1 { color: #7fff7f; }
        input { width: 100%; padding: 10px; margin: 8px 0; background: #1a1a1a; border: 1px solid #333; color: #eee; border-radius: 6px; box-sizing: border-box; font-family: monospace; }
        button { width: 100%; padding: 12px; background: #2a7a2a; color: #fff; border: none; border-radius: 6px; cursor: pointer; font-size: 16px; font-family: monospace; }
        button:hover { background: #3a9a3a; }
        #result { margin-top: 20px; padding: 15px; border-radius: 6px; display: none; font-size: 14px; }
        .approved { background: #0a2a0a; border: 1px solid #2a7a2a; color: #7fff7f; }
        .declined { background: #2a0a0a; border: 1px solid #7a2a2a; color: #ff7f7f; }
        .loading { color: #aaa; text-align: center; margin-top: 10px; display: none; }
    </style>
</head>
<body>
<div class="box">
    <h1>⚡ Zuora Checker</h1>
    <input id="cc" placeholder="Card number" />
    <input id="month" placeholder="Month (e.g. 12)" />
    <input id="year" placeholder="Year (e.g. 2028)" />
    <input id="cvv" placeholder="CVV" />
    <button onclick="check()">Check</button>
    <div class="loading" id="loading">⏳ Checking...</div>
    <div id="result"></div>
</div>
<script>
async function check() {
    const cc    = document.getElementById('cc').value.trim();
    const month = document.getElementById('month').value.trim();
    const year  = document.getElementById('year').value.trim();
    const cvv   = document.getElementById('cvv').value.trim();

    if (!cc || !month || !year || !cvv) {
        alert('Fill all fields');
        return;
    }

    document.getElementById('loading').style.display = 'block';
    document.getElementById('result').style.display  = 'none';

    const resp = await fetch('/check', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({cc, month, year, cvv})
    });

    const data = await resp.json();
    document.getElementById('loading').style.display = 'none';

    const div = document.getElementById('result');
    div.style.display = 'block';
    div.className = data.status.includes('Approved') ? 'approved' : 'declined';
    div.innerHTML = `<b>${data.status}</b><br>${data.message}`;
}

document.addEventListener('keydown', e => { if (e.key === 'Enter') check(); });
</script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML)

@app.route('/check', methods=['POST'])
def check():
    data  = request.json
    cc    = data.get('cc', '')
    month = data.get('month', '')
    year  = data.get('year', '')
    cvv   = data.get('cvv', '')

    status, message = asyncio.run(getzuoraStripe1(cc, month, year, cvv))
    return jsonify({"status": status, "message": message})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
