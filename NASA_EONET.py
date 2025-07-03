from flask import Flask, request, render_template, jsonify
import pandas as pd
import requests
import os
import configparser

app = Flask(__name__)

#Pfad zur Konfigurationsdatei
config_path = "config.ini"

# Standardkonfiguration
default_config = {
    "Benutzer": {
        "username": "admin",
        "language": "de",
        "activ": "True"
    },
    "Einstellungen": {
        "url": f"https://eonet.gsfc.nasa.gov/api/v2.1/events?",
        "limit": 10,
        "days": 10
    }
}

def save_default_config(path, config_dict):
    config = configparser.ConfigParser()
    for section, options in config_dict.items():
        config[section] = options
    with open(path, "w") as configfile:
        config.write(configfile)
    print(f"Standardkonfiguration wurde in '{path}' gespeichert.")

def update_config(config, section, key, new_value):
    if config.has_section(section):
        config[section][key]= new_value

def read_config(path):
    config = configparser.ConfigParser()
    config.read(path)
    print(f"Konfigurationsdaten eingelesen.")
    for section in config.sections():
        print(f"[{section}]")
        for key, value in config[section].items():
            print(f"{key} = {value}")
    return config

def get_config():
    if not os.path.exists(config_path):
        print("Konfigurationsdatei nicht gefunden. Erstelle Standard-Konfiguration ...")
        save_default_config(config_path, default_config)
    else:
        print(f"Konfigurationsdatei '{config_path}' ist bereits vorhanden.")
    
    # Konfigurationsdaten einlesen
    config = read_config(config_path)

    # Config-Werte nutzen
    username = config.get("Benutzer", "username")
    activ_user = config.getboolean("Benutzer", "activ")
    language = config.get("Benutzer", "language")
    url = config.get("Einstellungen", "url")
    limit = config.getint("Einstellungen", "limit")
    days = config.getint("Einstellungen", "days")

def fetch_nasa_events(limit, days):
    url = f"https://eonet.gsfc.nasa.gov/api/v2.1/events?limit={limit}&days={days}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return None

def events_to_dataframe(events):
    if events:
        data = []
        for event in events['events']:
            for geometry in event['geometries']:
                event_data = {
                    'ID': event['id'],
                    'Title': event['title'],
                    'Description': event.get('description', 'No description available'),
                    'Link': event['link'],
                    'Categories': ', '.join([category['title'] for category in event['categories']]),
                    'Sources': ', '.join([source['url'] for source in event['sources']]),
                    'Geometry Date': geometry['date'],
                    'Geometry Type': geometry['type'],
                    'Geometry Coordinates': geometry['coordinates']
                }
                data.append(event_data)
        df = pd.DataFrame(data)
        return df
    else:
        return pd.DataFrame()



@app.route('/fetch_events', methods=['POST'])
def fetch_events():
    limit = request.form.get('limit')
    days = request.form.get('days')
    events = fetch_nasa_events(limit, days)
    df = events_to_dataframe(events)
    return df.to_json(orient='records')

@app.route('/save_json', methods=['POST'])
def save_json():
    limit = request.form.get('limit')
    days = request.form.get('days')
    events = fetch_nasa_events(limit, days)
    
    if events:
        with open('nasa_events.json', 'w') as f:
            json.dump(events, f)
        return jsonify({"message": "Data saved to nasa_events.json"})
    else:
        return jsonify({"message": "Failed to fetch events"})

@app.route('/')
def index():
    return render_template('index.html')

@app.route("/data", methods=["POST"])
def data(limit, days):
    return render_template("data.html")

if __name__ == '__main__':
    get_config()    
    app.run(debug=True)
    
    