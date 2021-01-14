Build:
docker build -t informaticup_gruppe7_luh .

Ausführen: !!!!API Key lokal einfügen, **API_KEY** ersetzen!!!!
docker run -e URL="wss://msoll.de/spe_ed" -e KEY="**API_KEY**" -e TIME_URL "https://msoll.de/spe_ed_time" informaticup_gruppe7_luh
