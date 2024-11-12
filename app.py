from website import create_app
from config import Config

Config.init_folders()

app = create_app()

if __name__== '__main__':
    app.run(debug=True)