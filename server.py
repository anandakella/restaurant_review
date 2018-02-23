from revapp import create_app
from flask import Flask

def main():
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=8000)

if __name__ == '__main__':
    main()