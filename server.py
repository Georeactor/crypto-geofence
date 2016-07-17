# server.py

import os, re, json
import flask
from flask import request
from phe import paillier

app = flask.Flask(__name__)

# colorado geo fence
# xmin, ymin, xmax, ymax // west, south, east, north
# deg * 1000 units
# add 90 deg to north/south
# add 180 deg to east/west
geobox = [-102052 + 180000, 36971 + 90000, -109190 + 180000, 41010 + 90000]

@app.route('/')
def print_index():
    return open('./index.html', 'r').read()

@app.route('/calculate')
def calculate_geo():
    # rebuild public key
    g = int(request.args.get('g'))
    n = int(request.args.get('n'))
    pubkey = paillier.PaillierPublicKey(g=g, n=n)

    # load the coordinates as EncryptedNumber type
    lat = paillier.EncryptedNumber(pubkey, int(request.args.get('lat')))
    lng = paillier.EncryptedNumber(pubkey, int(request.args.get('lng')))

    # use same key to encrypt the geobox
    west = pubkey.encrypt(geobox[0])
    south = pubkey.encrypt(geobox[1])
    east = pubkey.encrypt(geobox[2])
    north = pubkey.encrypt(geobox[3])

    latoffset = (south - lat)
    latoffset2 = (north - lat)
    lngoffset = (west - lng)
    lngoffset2 = (east - lng)

    return json.dumps({
      "lat": str(latoffset.ciphertext()),
      "lat2": str(latoffset2.ciphertext()),
      "lng": str(lngoffset.ciphertext()),
      "lng2": str(lngoffset2.ciphertext()),
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
