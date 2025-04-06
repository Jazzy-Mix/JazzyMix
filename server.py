from flask import Flask, request, jsonify, render_template, redirect, url_for, send_from_directory
import requests
import base64
import datetime
import subprocess
import json

app = Flask(__name__, static_folder='.')

# M-Pesa Configuration
MPESA_CONSUMER_KEY = 'YOUR_MPESA_CONSUMER_KEY'
MPESA_CONSUMER_SECRET = 'YOUR_MPESA_CONSUMER_SECRET'
MPESA_SHORTCODE = 'YOUR_MPESA_SHORTCODE'
MPESA_PASSKEY = 'YOUR_MPESA_PASSKEY'
MPESA_API_URL = 'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'
MPESA_STK_PUSH_URL = 'https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest'

# PayPal Configuration
PAYPAL_CLIENT_ID = 'YOUR_PAYPAL_CLIENT_ID'
PAYPAL_CLIENT_SECRET = 'YOUR_PAYPAL_CLIENT_SECRET'
PAYPAL_API_URL = 'https://api.sandbox.paypal.com/v1/oauth2/token'
PAYPAL_PAYMENT_URL = 'https://api.sandbox.paypal.com/v1/payments/payment'

# PHP Script Path
PHP_SCRIPT_PATH = 'daraja.php'

# Define the services and their prices
services = {
    "Single Track Mixing": 250,
    "EP Mixing (3-5 Tracks)": 500,
    "Album Mixing (6+ Tracks)": 650,
    "Single Track Mastering": 100,
    "EP Mastering (3-5 Tracks)": 250,
    "Album Mastering (6+ Tracks)": 500,
    "Beat Production (Instrumental Only)": 200,
    "Full Song Production": 400,
    "Full Song Prod + Mix & Master": 450,
    "Recording Session (Per Hour)": 50
}

def calculate_total_cost(selected_services):
    total_cost = 0
    for service, price in selected_services.items():
        total_cost += price
    return total_cost

@app.route('/')
def index():
    return render_template('index.html', services=services)

@app.route('/select-services', methods=['POST'])
def select_services():
    selected_services = request.form.getlist('services')
    service_details = {}

    for service in selected_services:
        if service in services:
            service_details[service] = services[service]
            if "Tracks" in service:
                num_tracks = int(request.form[f'{service}_tracks'])
                if "3-5 Tracks" in service and (num_tracks < 3 or num_tracks > 5):
                    return jsonify({"success": False, "message": "Invalid number of tracks for this service."})
                elif "6+ Tracks" in service and num_tracks < 6:
                    return jsonify({"success": False, "message": "Invalid number of tracks for this service."})
                service_details[service] = services[service] * num_tracks
            elif "Recording Session" in service:
                hours = int(request.form[f'{service}_hours'])
                service_details[service] = services[service] * hours

    total_cost = calculate_total_cost(service_details)
    return jsonify({"success": True, "selected_services": service_details, "total_cost": total_cost})

@app.route('/collect-user-info', methods=['POST'])
def collect_user_info():
    user_info = {
        "Name": request.form['name'],
        "Email": request.form['email'],
        "Phone": request.form['phone'],
        "Date": request.form['date'],
        "Time": request.form['time']
    }
    return jsonify({"success": True, "user_info": user_info})

@app.route('/confirm-booking', methods=['POST'])
def confirm_booking():
    data = request.get_json()
    user_info = data.get('user_info')
    selected_services = data.get('selected_services')
    total_cost = data.get('total_cost')

    # Execute PHP script
    result = subprocess.run(['php', PHP_SCRIPT_PATH], capture_output=True, text=True)
    php_message = result.stdout.strip()

    return jsonify({
        "success": True,
        "user_info": user_info,
        "selected_services": selected_services,
        "total_cost": total_cost,
        "php_message": php_message
    })

@app.route('/pay-mpesa', methods=['POST'])
def pay_mpesa():
    data = request.get_json()
    mpesa_number = data.get('mpesaNumber')
    amount = data.get('amount')

    # Generate OAuth token for M-Pesa
    auth_response = requests.get(MPESA_API_URL, auth=(MPESA_CONSUMER_KEY, MPESA_CONSUMER_SECRET))
    access_token = auth_response.json().get('access_token')

    # Prepare M-Pesa STK push request
    timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    password = base64.b64encode(f"{MPESA_SHORTCODE}{MPESA_PASSKEY}{timestamp}".encode()).decode()

    stk_push_data = {
        "BusinessShortCode": MPESA_SHORTCODE,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": amount,
        "PartyA": mpesa_number,
        "PartyB": MPESA_SHORTCODE,
        "PhoneNumber": mpesa_number,
        "CallBackURL": "https://your-callback-url.com/callback",
        "AccountReference": "JazzyMix",
        "TransactionDesc": "Payment for Music Studio Booking"
    }

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    response = requests.post(MPESA_STK_PUSH_URL, json=stk_push_data, headers=headers)
    if response.status_code == 200:
        return jsonify({"success": True})
    else:
        return jsonify({"success": False, "error": "M-Pesa payment failed"})

@app.route('/pay-card', methods=['POST'])
def pay_card():
    data = request.get_json()
    card_number = data.get('cardNumber')
    expiry_date = data.get('expiryDate')
    cvv = data.get('cvv')
    amount = data.get('amount')

    # Placeholder for card payment logic
    # You would typically use a payment gateway like Stripe or Braintree here
    return jsonify({"success": True})

@app.route('/pay-paypal')
def pay_paypal():
    amount = request.args.get('amount', '100')  # Default amount if not provided

    # Prepare PayPal payment request
    auth_response = requests.post(PAYPAL_API_URL, auth=(PAYPAL_CLIENT_ID, PAYPAL_CLIENT_SECRET), data={
        'grant_type': 'client_credentials'
    })
    access_token = auth_response.json().get('access_token')

    payment_data = {
        "intent": "sale",
        "payer": {
            "payment_method": "paypal"
        },
        "transactions": [{
            "amount": {
                "total": amount,
                "currency": "USD"
            },
            "description": "Payment for Music Studio Booking"
        }],
        "redirect_urls": {
            "return_url": "http://localhost:5000/payment-success",
            "cancel_url": "http://localhost:5000/payment-cancel"
        }
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }

    response = requests.post(PAYPAL_PAYMENT_URL, json=payment_data, headers=headers)
    if response.status_code == 201:
        approval_url = next(link['href'] for link in response.json()['links'] if link['rel'] == 'approval_url')
        return redirect(approval_url)
    else:
        return jsonify({"success": False})

@app.route('/payment-success')
def payment_success():
    # Handle payment success
    return render_template('payment_success.html')

@app.route('/payment-cancel')
def payment_cancel():
    # Handle payment cancellation
    return render_template('payment_cancel.html')

@app.route('/<path:path>')
def static_files(path):
    try:
        return send_from_directory('.', path)
    except FileNotFoundError:
        return "Not Found", 404

if __name__ == '__main__':
    app.run(debug=True)