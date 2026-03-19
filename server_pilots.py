from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import os

DATA_FILE = "pilots.json"

def read_pilots():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def write_pilots(pilots):
    with open(DATA_FILE, "w") as f:
        json.dump(pilots, f, indent=2)

def find_pilot(pilots, pilot_id):
    for index, pilot in enumerate(pilots):
        if pilot["id"] == pilot_id:
            return pilot, index
    return None, None


class PilotsHandler(BaseHTTPRequestHandler):

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

    def get_pilot_id_from_path(self):
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
        pilots = read_pilots()

        if self.path == "/pilots":
            self.send_json(200, pilots)

        elif self.path.startswith("/pilots/"):
            pilot_id = self.get_pilot_id_from_path()
            if pilot_id is None:
                self.send_json(400, {"error": "ID invalid."})
                return
            pilot, _ = find_pilot(pilots, pilot_id)
            if pilot is None:
                self.send_json(404, {"error": f"Pilotul cu ID {pilot_id} nu a fost gasit."})
            else:
                self.send_json(200, pilot)
        else:
            self.send_json(404, {"error": "Ruta nu exista."})

    def do_POST(self):
        if self.path == "/pilots":
            body = self.get_body()
            if body is None:
                self.send_json(400, {"error": "Body-ul nu este JSON valid."})
                return

            required = ["name", "nationality", "number", "team", "championships", "wins"]
            for field in required:
                if field not in body:
                    self.send_json(400, {"error": f"Campul '{field}' este obligatoriu."})
                    return

            pilots = read_pilots()

            for pilot in pilots:
                if pilot["name"].lower() == body["name"].lower():
                    self.send_json(409, {"error": "Un pilot cu acest nume exista deja."})
                    return

            new_id = max((p["id"] for p in pilots), default=0) + 1
            new_pilot = {
                "id": new_id,
                "name": body["name"],
                "nationality": body["nationality"],
                "number": body["number"],
                "team": body["team"],
                "championships": body["championships"],
                "wins": body["wins"]
            }
            pilots.append(new_pilot)
            write_pilots(pilots)
            self.send_json(201, new_pilot)
        else:
            self.send_json(404, {"error": "Ruta nu exista."})

    def do_PUT(self):
        if self.path.startswith("/pilots/"):
            pilot_id = self.get_pilot_id_from_path()
            if pilot_id is None:
                self.send_json(400, {"error": "ID invalid."})
                return

            body = self.get_body()
            if body is None:
                self.send_json(400, {"error": "Body-ul nu este JSON valid."})
                return

            required = ["name", "nationality", "number", "team", "championships", "wins"]
            for field in required:
                if field not in body:
                    self.send_json(400, {"error": f"Campul '{field}' este obligatoriu pentru PUT."})
                    return

            pilots = read_pilots()
            pilot, index = find_pilot(pilots, pilot_id)
            if pilot is None:
                self.send_json(404, {"error": f"Pilotul cu ID {pilot_id} nu a fost gasit."})
                return

            pilots[index] = {
                "id": pilot_id,
                "name": body["name"],
                "nationality": body["nationality"],
                "number": body["number"],
                "team": body["team"],
                "championships": body["championships"],
                "wins": body["wins"]
            }
            write_pilots(pilots)
            self.send_json(200, pilots[index])
        else:
            self.send_json(405, {"error": "Method Not Allowed."})

    def do_PATCH(self):
        if self.path.startswith("/pilots/"):
            pilot_id = self.get_pilot_id_from_path()
            if pilot_id is None:
                self.send_json(400, {"error": "ID invalid."})
                return

            body = self.get_body()
            if body is None:
                self.send_json(400, {"error": "Body-ul nu este JSON valid."})
                return

            pilots = read_pilots()
            pilot, index = find_pilot(pilots, pilot_id)
            if pilot is None:
                self.send_json(404, {"error": f"Pilotul cu ID {pilot_id} nu a fost gasit."})
                return

            allowed_fields = ["name", "nationality", "number", "team", "championships", "wins"]
            for field in allowed_fields:
                if field in body:
                    pilots[index][field] = body[field]

            write_pilots(pilots)
            self.send_json(200, pilots[index])
        else:
            self.send_json(405, {"error": "Method Not Allowed."})

    def do_DELETE(self):
        pilots = read_pilots()

        if self.path == "/pilots":
            write_pilots([])
            self.send_json(200, {"message": "Toti pilotii au fost stersi."})

        elif self.path.startswith("/pilots/"):
            pilot_id = self.get_pilot_id_from_path()
            if pilot_id is None:
                self.send_json(400, {"error": "ID invalid."})
                return

            pilot, index = find_pilot(pilots, pilot_id)
            if pilot is None:
                self.send_json(404, {"error": f"Pilotul cu ID {pilot_id} nu a fost gasit."})
                return

            pilots.pop(index)
            write_pilots(pilots)
            self.send_json(200, {"message": f"Pilotul cu ID {pilot_id} a fost sters."})
        else:
            self.send_json(404, {"error": "Ruta nu exista."})

    def log_message(self, format, *args):
        print(f"  >> {self.command} {self.path} -> {args[1]}")


if __name__ == "__main__":
    HOST = "localhost"
    PORT = 8001
    server = HTTPServer((HOST, PORT), PilotsHandler)
    print(f"Pilots API pornit pe http://{HOST}:{PORT}")
    print(f"Incearca: http://{HOST}:{PORT}/pilots")
    print(f"Apasa CTRL+C pentru a opri serverul.\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n  Server oprit.")
