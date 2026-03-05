from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import os

#json pentru citire si scriere
DATA_FILE = "teams.json"


def read_teams():
    #citire echipe din json
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r") as f:
        return json.load(f)


def write_teams(teams):
    #salvare echipe in json
    with open(DATA_FILE, "w") as f:
        json.dump(teams, f, indent=2)


def find_team(teams, team_id):
    #cautare echipa dupa ID
    for index, team in enumerate(teams):
        if team["id"] == team_id:
            return team, index
    return None, None


#handler principal - requesturi http
class F1Handler(BaseHTTPRequestHandler):

    def send_json(self, status_code, data):
        #trimit raspuns json cu status aferent
        body = json.dumps(data, indent=2).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def get_body(self):
        #citesc body request si parsare ca json
        length = int(self.headers.get("Content-Length", 0))
        if length == 0:
            return {}
        raw = self.rfile.read(length)
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return None

    def get_team_id_from_path(self):
        #extrag id team din url
        parts = self.path.strip("/").split("/")
        if len(parts) == 2 and parts[1].isdigit():
            return int(parts[1])
        return None

    def do_GET(self):
        teams = read_teams()

        #GET /teams
        if self.path == "/teams":
            self.send_json(200, teams)

        #GET /teams/{id}
        elif self.path.startswith("/teams/"):
            team_id = self.get_team_id_from_path()
            if team_id is None:
                self.send_json(400, {"error": "ID invalid."})
                return
            team, _ = find_team(teams, team_id)
            if team is None:
                self.send_json(404, {"error": f"Echipa cu ID {team_id} nu a fost gasita."})
            else:
                self.send_json(200, team)

        else:
            self.send_json(404, {"error": "Ruta nu exista."})

    #POST /teams  -> adauga o echipa noua
    def do_POST(self):
        if self.path == "/teams":
            body = self.get_body()
            if body is None:
                self.send_json(400, {"error": "Body-ul nu este JSON valid."})
                return

            #campuri obligatorii
            required = ["name", "driver", "country", "points", "championships"]
            for field in required:
                if field not in body:
                    self.send_json(400, {"error": f"Campul '{field}' este obligatoriu."})
                    return

            teams = read_teams()

            #verificare daca echipa exista - dupa nume
            for team in teams:
                if team["name"].lower() == body["name"].lower():
                    self.send_json(409, {"error": "O echipa cu acest nume exista deja."})
                    return

            #generez id nou
            new_id = max((t["id"] for t in teams), default=0) + 1
            new_team = {
                "id": new_id,
                "name": body["name"],
                "driver": body["driver"],
                "country": body["country"],
                "points": body["points"],
                "championships": body["championships"]
            }
            teams.append(new_team)
            write_teams(teams)
            self.send_json(201, new_team)

        else:
            self.send_json(404, {"error": "Ruta nu exista."})

    #PUT /teams/{id}  - inlocuiesc o echipa
    def do_PUT(self):
        if self.path.startswith("/teams/"):
            team_id = self.get_team_id_from_path()
            if team_id is None:
                self.send_json(400, {"error": "ID invalid."})
                return

            body = self.get_body()
            if body is None:
                self.send_json(400, {"error": "Body-ul nu este JSON valid."})
                return

            #Campuri obligatorii pentru PUT
            required = ["name", "driver", "country", "points", "championships"]
            for field in required:
                if field not in body:
                    self.send_json(400, {"error": f"Campul '{field}' este obligatoriu pentru PUT."})
                    return

            teams = read_teams()
            team, index = find_team(teams, team_id)
            if team is None:
                self.send_json(404, {"error": f"Echipa cu ID {team_id} nu a fost gasita."})
                return

            #inlocuiesc echipa - pastrez id ul
            teams[index] = {
                "id": team_id,
                "name": body["name"],
                "driver": body["driver"],
                "country": body["country"],
                "points": body["points"],
                "championships": body["championships"]
            }
            write_teams(teams)
            self.send_json(200, teams[index])

        else:
            self.send_json(405, {"error": "Method Not Allowed. PUT functioneaza doar pe /teams/{id}."})

    #PATCH /teams/{id}  - modific info despre o echipa
    def do_PATCH(self):
        if self.path.startswith("/teams/"):
            team_id = self.get_team_id_from_path()
            if team_id is None:
                self.send_json(400, {"error": "ID invalid."})
                return

            body = self.get_body()
            if body is None:
                self.send_json(400, {"error": "Body-ul nu este JSON valid."})
                return

            teams = read_teams()
            team, index = find_team(teams, team_id)
            if team is None:
                self.send_json(404, {"error": f"Echipa cu ID {team_id} nu a fost gasita."})
                return

            #actualizare doar campuri trimise in body
            allowed_fields = ["name", "driver", "country", "points", "championships"]
            for field in allowed_fields:
                if field in body:
                    teams[index][field] = body[field]

            write_teams(teams)
            self.send_json(200, teams[index])

        else:
            self.send_json(405, {"error": "Method Not Allowed. PATCH functioneaza doar pe /teams/{id}."})

    #DELETE /teams - sterg toate echipele
    #DELETE /teams/{id} - sterg echipa dupa id
    def do_DELETE(self):
        teams = read_teams()

        #DELETE /teams
        if self.path == "/teams":
            write_teams([])
            self.send_json(200, {"message": "Toate echipele au fost sterse."})

        #DELETE /teams/{id}
        elif self.path.startswith("/teams/"):
            team_id = self.get_team_id_from_path()
            if team_id is None:
                self.send_json(400, {"error": "ID invalid."})
                return

            team, index = find_team(teams, team_id)
            if team is None:
                self.send_json(404, {"error": f"Echipa cu ID {team_id} nu a fost gasita."})
                return

            teams.pop(index)
            write_teams(teams)
            self.send_json(200, {"message": f"Echipa cu ID {team_id} a fost stearsa."})

        else:
            self.send_json(404, {"error": "Ruta nu exista."})

    #suprima log-urile default din terminal (optional)
    def log_message(self, format, *args):
        print(f"  >> {self.command} {self.path} -> {args[1]}")


#pornire server
if __name__ == "__main__":
    HOST = "localhost"
    PORT = 8000
    server = HTTPServer((HOST, PORT), F1Handler)
    print(f"🏎️  F1 API pornit pe http://{HOST}:{PORT}")
    print(f"    Incearca: http://{HOST}:{PORT}/teams")
    print(f"    Apasa CTRL+C pentru a opri serverul.\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n  Server oprit.")