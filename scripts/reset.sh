docker-compose --profile dev down -v
mv app/files/output/ingested/* app/files/input
rm app/files/output/reports/*