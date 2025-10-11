from flask import Flask

# Create an instance of the Flask web application
app = Flask(__name__)

# Define a "route". This tells Flask what function to run
# when a user visits the main URL of our server.
@app.route("/")
def index():
    return "Hello from the Personal Cloud Server!"

# This is a standard block in Python to make the script runnable.
if __name__ == "__main__":
    # app.run() starts the server.
    # host='0.0.0.0' makes the server visible on your network (not just on the laptop itself).
    # port=5000 is the "door number" our server will listen on.
    app.run(host='0.0.0.0', port=5000, debug=True)
