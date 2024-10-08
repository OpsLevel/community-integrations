import hmac
import hashlib
import os
from flask import Flask, request, abort

app = Flask(__name__)

# Define your webhook signing secret here
SIGNING_SECRET = os.environ["OPSLEVEL_SIGNING_SECRET"]

# Define required and action-specific headers
REQUIRED_HEADERS = {'X-OpsLevel-Timing'}
# Ensure the first letter is capitalized in the action headers in the OpsLevel action
ACTION_HEADERS = {'Content-Type', 'From', 'Authorization', 'Accept'}

def normalize_headers(headers):
    """
    Normalize the headers by correcting the case of 'X-Opslevel-Timing' to 'X-OpsLevel-Timing'.
    """
    if 'X-Opslevel-Timing' in headers:
        # Update to the correct header name
        headers['X-OpsLevel-Timing'] = headers.pop('X-Opslevel-Timing')
    return headers

def verify_signature(payload, headers, provided_signature, SIGNING_SECRET):
    """
    Compute the HMAC SHA-256 signature for the given payload and headers.
    """

    # Keep Required X-OpsLevel-Timing header and action headers
    allowed_headers = REQUIRED_HEADERS.union(ACTION_HEADERS)
    filtered_headers = {key: headers[key] for key in headers if key in allowed_headers}
    
    # Sort headers alphabetically
    sorted_headers = {key: filtered_headers[key] for key in sorted(filtered_headers)}

    # Create the message for HMAC: it should be the concatenated headers (joined by commas) + payload
    # e.g. "Content-Type:application/json,X-OpsLevel-Timing:123456789+{\n  "service": "shopping-cart-service",\n  "repository": "shopping-cart-repo"\n}"
    header_str = ','.join(f'{key}:{value}' for key, value in sorted_headers.items())
    message = f"{header_str}+{payload}"

    # Compute HMAC-SHA256 using the signing secret
    expected_signature = hmac.new(SIGNING_SECRET.encode('utf-8'), message.encode('utf-8'), hashlib.sha256).hexdigest()
        
    # Compare the provided signature with the computed expected signature
    return hmac.compare_digest(provided_signature, expected_signature)

@app.route('/webhook', methods=['POST'])
def webhook():
    # Step 1: Extract the signature from the request headers
    signature_header = request.headers.get('X-OpsLevel-Signature')
    if not signature_header:
        abort(400, 'X-OpsLevel-Signature header is missing')

    # Extract the actual signature (removing the "sha256=" prefix)
    provided_signature = signature_header.split('sha256=')[-1]

    # Step 2: Extract payload from request
    payload = request.data.decode('utf-8')

    # Step 3: Convert Flask request headers into Python Dictionary
    headers = dict(request.headers)

    # Normalize headers to fix "X-Opslevel-Timing" casing if necessary
    headers = normalize_headers(headers)

    # Step 4: Verify the computed signature with the provided signature
    if verify_signature(payload, headers, provided_signature, SIGNING_SECRET):
        return 'Signature is valid and request is authenticated', 200
    else:
        abort(403, 'Invalid signature')


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=9000)