from flask import Flask, request, render_template, jsonify
import pandas as pd
import requests
import os
import configparser
import json

app = Flask(__name__)

# Pfad zur Konfigurationsdatei
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
                # Quellen-Infos extrahieren
                sources = event.get('sources', [])
                source_names = ', '.join([source.get('id', '') for source in sources])
                source_urls = ', '.join([source.get('url', '') for source in sources])
                event_data = {
                    'ID': event['id'],
                    'Title': event['title'],
                    'Description': event.get('description', 'No description available'),
                    'Link': event['link'],
                    'Categories': ', '.join([category['title'] for category in event['categories']]),
                    'Sources': source_urls,
                    'Source Names': source_names,
                    'Geometry Date': geometry['date'],
                    'Geometry Type': geometry['type'],
                    'Geometry Coordinates': geometry['coordinates']
                }
                data.append(event_data)
        df = pd.DataFrame(data)
        return df
    else:
        return pd.DataFrame()


# Fetch events and return as JSON
@app.route('/fetch_events', methods=['POST'])
def fetch_events():
    limit = request.form.get('limit')
    days = request.form.get('days')
    events = fetch_nasa_events(limit, days)
    df = events_to_dataframe(events)
    return df.to_json(orient='records')

# Save events to JSON file
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

# Startseite
@app.route('/')
def index():
    return render_template('index.html')

# Daten anzeigen
@app.route("/data", methods=["POST"])
def data():
    config = read_config(config_path)
    try:
        limit = config.getint("Einstellungen", "limit")
    except Exception:
        limit = 10
    try:
        days = config.getint("Einstellungen", "days")
    except Exception:
        days = 10
    return render_template("data.html", limit=limit, days=days)

# Einstellungen anzeigen 
@app.route("/preferences", methods=["GET"])
def preferences():
    config = read_config(config_path)
    config_dict = {section: dict(config.items(section)) for section in config.sections()}
    return render_template("preferences.html", config=config_dict)

# Einstellungen updaten
@app.route('/update_preferences', methods=['POST'])
def update_preferences():
    limit = request.form.get('limit')
    days = request.form.get('days')
    config = configparser.ConfigParser()
    config.read(config_path)
    if not config.has_section('Einstellungen'):
        config.add_section('Einstellungen')
    if limit is not None:
        config.set('Einstellungen', 'limit', str(limit))
    if days is not None:
        config.set('Einstellungen', 'days', str(days))
    with open(config_path, 'w') as configfile:
        config.write(configfile)
    return render_template('preferences.html', config={section: dict(config.items(section)) for section in config.sections()}, message='Einstellungen gespeichert!')

# Web-Anwendung beenden
@app.route('/shutdown', methods=['POST'])
def shutdown():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        return 'Server kann nicht automatisch beendet werden. Bitte im Terminal stoppen.'
    func()
    return render_template('shutdown.html')


if __name__ == '__main__':
    
    # auf Config-Datei prüfen; erstellen, wenn nicht vorhanden
    get_config() 
    
    # Config-Daten einlesen
    config = read_config(config_path)   
    
     # Config-Werte nutzen
    username = config.get("Benutzer", "username")
    activ_user = config.getboolean("Benutzer", "activ")
    language = config.get("Benutzer", "language")
    url = config.get("Einstellungen", "url")
    limit = config.getint("Einstellungen", "limit")
    days = config.getint("Einstellungen", "days")

    # Flask starten
    app.run(debug=True)

