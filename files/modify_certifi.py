"""
Author: Jeremy Cornett
Date: 2019-12-02
Purpose: Ensure the CA certificate is installed in the CA bundle that certifi uses.
"""

import argparse
import certifi
import requests


if __name__ == "__main__":
    # Parse the command line arguments.
    parser = argparse.ArgumentParser(description="")
    parser.add_argument("url", help="The URL of the Jenkins master.")
    parser.add_argument("ca_cert", help="The path to a CA certificate to verify for connections with the "
                                        "Jenkins master.")
    args = parser.parse_args()

    # The process for obtaining the crumb doesn't use the OS cert store. It uses the ca bundle packaged in certifi.
    # Disabling the SSL verification is one workaround.
    # os.environ.setdefault("PYTHONHTTPSVERIFY", "0")
    # The appropriate way is to modify the bundle being used by certifi.
    # https://incognitjoe.github.io/adding-certs-to-requests.html
    # https://requests.readthedocs.io/en/master/user/advanced/#ca-certificates
    if args.ca_cert and len(args.ca_cert) != 0:
        try:
            test = requests.get(args.url)
        except requests.exceptions.SSLError as err:
            cafile = certifi.where()
            with open(args.ca_cert, 'rb') as infile:
                customca = infile.read()
            with open(cafile, 'ab') as outfile:
                outfile.write(customca)
