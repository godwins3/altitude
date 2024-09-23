from server import app

if __name__ == "__main__":
    app.run(debug=True, threaded=True,port=5000,host="0.0.0.0")