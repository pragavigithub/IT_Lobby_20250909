# make_license.py
import json, base64, datetime
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend

# Load private key
with open("private_key.pem","rb") as f:
    priv = serialization.load_pem_private_key(f.read(), password=None, backend=default_backend())

license_data = {
    "name": "Emerging Alliance",
    "product": "BarCode&CopyPastAdd_on",
    "from": "2025-07-01",
    "to": "2025-12-17",
    "metadata": {"max_users": 10},
    "issued_at": datetime.datetime.utcnow().isoformat() + "Z"
}

payload_bytes = json.dumps(license_data, separators=(',',':')).encode('utf-8')

signature = priv.sign(
    payload_bytes,
    padding.PKCS1v15(),
    hashes.SHA256()
)

out = {
    "payload": base64.b64encode(payload_bytes).decode('ascii'),
    "signature": base64.b64encode(signature).decode('ascii')
}

with open("license.lic", "w") as f:
    json.dump(out, f, indent=2)
print("License file written: license.lic")
