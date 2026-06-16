# Pencil Production Line Simulator

Student: Ismail Rachid  
Student ID: 100006790

## Run the website
Open:

```text
website/index.html
```

or from PowerShell inside this folder:

```powershell
start .\website\index.html
```

## Run the Python HMI

```powershell
pip install -r requirements.txt
python .\src\main.py
```

## Run InfluxDB and Grafana

Start Docker Desktop first, then run:

```powershell
docker compose up -d
```

Open Grafana:

```text
http://localhost:3000
```

Login:

```text
admin
admin
```

The dashboard is automatically provisioned from:

```text
grafana/provisioning/dashboards/pencil-line-dashboard.json
```

If Grafana is empty, produce data by running the HMI and pressing START, or run:

```powershell
python .\src\producer.py
```

## Code structure

```text
src/main.py             starts the app
src/hmi.py              front-end Tkinter HMI
src/production_line.py  back-end production logic
src/stations.py         separate station classes
src/models.py           Pencil data model
src/database.py         InfluxDB writer
src/producer.py         optional test telemetry sender
```

## AI usage
Course instructions require AI use to be declared in the appendix if AI tools were used.
