# F1 Dashboard — Homework 2

## Structura proiectului
```
f1-app/
├── server.py           ← Web Service 1: Echipe  (port 8000) — HW1 neschimbat
├── server_pilots.py    ← Web Service 2: Piloti  (port 8001) — nou
├── server_races.py     ← Web Service 3: Curse   (port 8002) — nou
├── teams.json          ← Date echipe
├── pilots.json         ← Date piloti
├── races.json          ← Date curse
├── app.py              ← Backend Flask (port 5000) — agregate toate 3 servicii
└── frontend/           ← React (port 3000)
    ├── package.json
    ├── public/index.html
    └── src/
        ├── index.js
        ├── index.css
        └── App.jsx
```

## Setup (o singura data)

### 1. Instaleaza dependente Python
```
pip install flask flask-cors requests
```

### 2. Instaleaza Node.js
Descarca de pe https://nodejs.org (versiunea LTS)

### 3. Instaleaza dependente React
```
cd frontend
npm install
```

## Rulare (de fiecare data)

Deschide 5 terminale in PyCharm:

**Terminal 1 — Web Service Echipe (HW1):**
```
python server.py
```
→ http://localhost:8000/teams

**Terminal 2 — Web Service Piloti:**
```
python server_pilots.py
```
→ http://localhost:8001/pilots

**Terminal 3 — Web Service Curse:**
```
python server_races.py
```
→ http://localhost:8002/races

**Terminal 4 — Flask backend:**
```
python app.py
```
→ http://localhost:5000/api/...

**Terminal 5 — React frontend:**
```
cd frontend
npm start
```
→ http://localhost:3000

## Endpoint-uri Flask disponibile

### Echipe
- GET    /api/teams
- GET    /api/teams/{id}
- POST   /api/teams
- PUT    /api/teams/{id}
- PATCH  /api/teams/{id}
- DELETE /api/teams/{id}

### Piloti
- GET    /api/pilots
- GET    /api/pilots/{id}
- POST   /api/pilots
- PUT    /api/pilots/{id}
- PATCH  /api/pilots/{id}
- DELETE /api/pilots/{id}

### Curse
- GET    /api/races
- GET    /api/races/{id}
- POST   /api/races
- PUT    /api/races/{id}
- PATCH  /api/races/{id}
- DELETE /api/races/{id}

### Agregate
- GET    /api/dashboard  ← combina date din toate 3 servicii
