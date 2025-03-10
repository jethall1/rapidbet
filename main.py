from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import requests

app = Flask(__name__)
app.secret_key = "supersecretkey"  # Change for production
API_ODDS_URL = "https://rapidfeature.com/v1/odds"
API_OUTCOME_URL = "https://rapidfeature.com/v1/outcome/{}"

# Initialize balance and bets
def init_session():
    if 'balance' not in session:
        session['balance'] = 1000  # Starting balance
    if 'bets' not in session:
        session['bets'] = []  # Store placed bets

@app.route('/')
def index():
    init_session()
    odds_response = requests.get(API_ODDS_URL)
    horses = odds_response.json() if odds_response.status_code == 200 else []
    return render_template("index.html", balance=session['balance'], horses=horses, bets=session['bets'])

@app.route('/bet', methods=['POST'])
def place_bet():
    init_session()
    horse_id = int(request.form.get('horse_id'))
    horse_name = request.form.get('horse_name')
    odds = float(request.form.get('odds'))
    amount = float(request.form.get('amount'))
    
    if amount > session['balance'] or amount <= 0:
        return redirect(url_for('index'))
    
    session['balance'] -= amount
    session['bets'].append({'id': horse_id, 'name': horse_name, 'odds': odds, 'amount': amount})
    session.modified = True
    return redirect(url_for('index'))

@app.route('/fetch_results')
def fetch_results():
    init_session()
    new_bets = []
    for bet in session['bets']:
        outcome_response = requests.get(API_OUTCOME_URL.format(bet['id']))
        if outcome_response.status_code == 200:
            outcome = outcome_response.json()
            if outcome['won']:
                session['balance'] += bet['amount'] * bet['odds']
            else:
                bet['lost'] = True
        new_bets.append(bet)
    session['bets'] = new_bets
    session.modified = True
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)