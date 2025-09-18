# from app import app
# from Lic.license_validator import load_public_key, validate_license_file
# import sys, pkgutil
# # Import routes
# import routes
#
# # Import cascading dropdown APIs
# import api_cascading_dropdowns
#
# if __name__ == "__main__":
#
#     pub = load_public_key("E:\SAP_Integ\Git Change\20250918\2\IT_Lobby_20250909\Lic\public_key.pem")
#     ok, info = validate_license_file("E:\SAP_Integ\Git Change\20250918\2\IT_Lobby_20250909\Lic\license.lic", pub)
#     if not ok:
#         print("License validation failed:", info)
#         sys.exit(1)
#
#     app.run(host="0.0.0.0", port=5000, debug=True)
import sys
import os
import logging
from app import app
from Lic.license_validator import load_public_key, validate_license_file

# Import routes and APIs
import routes
import api_cascading_dropdowns

if __name__ == "__main__":
    # Use relative path so it works in exe or project folder
    #base_dir = os.path.dirname(os.path.abspath(__file__))
    pub_key_path = os.path.join("C:\\tmp\\", "sap_login", "public_key.pem")
    license_path = os.path.join("C:\\tmp\\", "sap_login", "license.lic")

    try:
        pub = load_public_key(pub_key_path)
        ok, info = validate_license_file(license_path, pub)
        if not ok:
            logging.info("❌ License validation failed:", info)
            sys.exit(1)
        else:
            logging.info("✅ License validated Successfully")
    except Exception as e:
        logging.info(f"❌ License check error: {e}")
        sys.exit(1)

    # Start Flask app only if license is valid
    app.run(host="0.0.0.0", port=5000, debug=True)
