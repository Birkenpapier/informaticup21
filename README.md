Build:
docker build -t informaticup_gruppe7_luh .

Ausführen: !!!API Key lokal einfügen!!!
docker run -e URL="wss://msoll.de/spe_ed" -e KEY="" informaticup_gruppe7_luh