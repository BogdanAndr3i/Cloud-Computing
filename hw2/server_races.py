from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import os

DATA_FILE = "races.json"

def read_races():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def write_races(races):
    with open(DATA_FILE, "w") as f:
        json.dump(races, f, indent=2)

def find_race(races, race_id):
    for index, race in enumerate(races):
        if race["id"] == race_id:
            return race, index
    return None, None


class RacesHandler(BaseHTTPRequestHandler):

    def send_json(self, status_code, data):
        body = json.dumps(data, indent=2).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def get_body(self):
        length = int(self.headers.get("Content-Length", 0))
        if length == 0:
            return {}
        raw = self.rfile.read(length)
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return None

    def get_race_id_from_path(self):
        parts = self.path.strip("/").split("/")
        if len(parts) == 2 and parts[1].isdigit():
            return int(parts[1])
        return None

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, PATCH, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        races = read_races()

        if self.path == "/races":
            self.send_json(200, races)

        elif self.path.startswith("/races/"):
            race_id = self.get_race_id_from_path()
            if race_id is None:
                self.send_json(400, {"error": "ID invalid."})
                return
            race, _ = find_race(races, race_id)
            if race is None:
                self.send_json(404, {"error": f"Cursa cu ID {race_id} nu a fost gasita."})
            else:
                self.send_json(200, race)
        else:
            self.send_json(404, {"error": "Ruta nu exista."})

    def do_POST(self):
        if self.path == "/races":
            body = self.get_body()
            if body is None:
                self.send_json(400, {"error": "Body-ul nu este JSON valid."})
                return

            required = ["name", "circuit", "country", "date", "laps", "winner"]
            for field in required:
                if field not in body:
                    self.send_json(400, {"error": f"Campul '{field}' este obligatoriu."})
                    return

            races = read_races()

            for race in races:
                if race["name"].lower() == body["name"].lower():
                    self.send_json(409, {"error": "O cursa cu acest nume exista deja."})
                    return

            new_id = max((r["id"] for r in races), default=0) + 1
            new_race = {
                "id": new_id,
                "name": body["name"],
                "circuit": body["circuit"],
                "country": body["country"],
                "date": body["date"],
                "laps": body["laps"],
                "winner": body["winner"]
            }
            races.append(new_race)
            write_races(races)
            self.send_json(201, new_race)
        else:
            self.send_json(404, {"error": "Ruta nu exista."})

    def do_PUT(self):
        if self.path.startswith("/races/"):
            race_id = self.get_race_id_from_path()
            if race_id is None:
                self.send_json(400, {"error": "ID invalid."})
                return

            body = self.get_body()
            if body is None:
                self.send_json(400, {"error": "Body-ul nu este JSON valid."})
                return

            required = ["name", "circuit", "country", "date", "laps", "winner"]
            for field in required:
                if field not in body:
                    self.send_json(400, {"error": f"Campul '{field}' este obligatoriu pentru PUT."})
                    return

            races = read_races()
            race, index = find_race(races, race_id)
            if race is None:
                self.send_json(404, {"error": f"Cursa cu ID {race_id} nu a fost gasita."})
                return

            races[index] = {
                "id": race_id,
                "name": body["name"],
                "circuit": body["circuit"],
                "country": body["country"],
                "date": body["date"],
                "laps": body["laps"],
                "winner": body["winner"]
            }
            write_races(races)
            self.send_json(200, races[index])
        else:
            self.send_json(405, {"error": "Method Not Allowed."})

    def do_PATCH(self):
        if self.path.startswith("/races/"):
            race_id = self.get_race_id_from_path()
            if race_id is None:
                self.send_json(400, {"error": "ID invalid."})
                return

            body = self.get_body()
            if body is None:
                self.send_json(400, {"error": "Body-ul nu este JSON valid."})
                return

            races = read_races()
            race, index = find_race(races, race_id)
            if race is None:
                self.send_json(404, {"error": f"Cursa cu ID {race_id} nu a fost gasita."})
                return

            allowed_fields = ["name", "circuit", "country", "date", "laps", "winner"]
            for field in allowed_fields:
                if field in body:
                    races[index][field] = body[field]

            write_races(races)
            self.send_json(200, races[index])
        else:
            self.send_json(405, {"error": "Method Not Allowed."})

    def do_DELETE(self):
        races = read_races()

        if self.path == "/races":
            write_races([])
            self.send_json(200, {"message": "Toate cursele au fost sterse."})

        elif self.path.startswith("/races/"):
            race_id = self.get_race_id_from_path()
            if race_id is None:
                self.send_json(400, {"error": "ID invalid."})
                return

            race, index = find_race(races, race_id)
            if race is None:
                self.send_json(404, {"error": f"Cursa cu ID {race_id} nu a fost gasita."})
                return

            races.pop(index)
            write_races(races)
            self.send_json(200, {"message": f"Cursa cu ID {race_id} a fost stearsa."})
        else:
            self.send_json(404, {"error": "Ruta nu exista."})

    def log_message(self, format, *args):
        print(f"  >> {self.command} {self.path} -> {args[1]}")


if __name__ == "__main__":
    HOST = "localhost"
    PORT = 8002
    server = HTTPServer((HOST, PORT), RacesHandler)
    print(f"Races API pornit pe http://{HOST}:{PORT}")
    print(f"Incearca: http://{HOST}:{PORT}/races")
    print(f"Apasa CTRL+C pentru a opri serverul.\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n  Server oprit.")
