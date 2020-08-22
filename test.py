from flask import Flask
app = Flask(__name__)

@app.route("/")
def test():
    return "Hello, there, world!"

if __name__ == "__main__":
    print("Starting the server...")
    app.run(debug=False)
    print("The server is done!")

