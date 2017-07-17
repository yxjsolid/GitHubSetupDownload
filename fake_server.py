from flask import Flask
app = Flask(__name__, static_folder="static",static_url_path='')

if __name__ == "__main__":
    context = ('cert.pem', 'key.pem')
    # app.run(host="10.103.12.31", port=443, debug=1, ssl_context = context)
    app.run(host="127.0.0.1", port=80, debug=1, )
    # app.run(host="10.103.12.31", port=80, debug=1, )