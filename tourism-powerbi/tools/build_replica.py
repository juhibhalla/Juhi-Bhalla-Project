import csv
import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
echarts_path = sys.argv[1]
rows = []
with open(os.path.join(ROOT, "data", "Tourism_Hospitality_Industry_Analysis.csv"), newline="", encoding="utf-8") as f:
    for r in csv.DictReader(f):
        rows.append({
            "country": r["Country"].strip(), "city": r["City"].strip(), "y": int(r["Year"]), "m": int(r["Month"]),
            "t": int(r["Number_of_Tourists"]), "purpose": r["Purpose_of_Visit"].strip(), "los": float(r["Average_Length_of_Stay"]),
            "spend": float(r["Tourist_Spending_USD"]), "occ": float(r["Hotel_Occupancy_Rate"]), "rating": r["Hotel_Rating"].strip(),
            "price": float(r["Average_Room_Price_USD"]), "rev": float(r["Tourism_Revenue_USD"]), "emp": int(r["Employment_in_Tourism"]),
            "gdp": float(r["Contribution_to_GDP_Percent"]), "air": int(r["Airport_Passenger_Traffic"]),
            "infra": float(r["Transport_Infrastructure_Quality"]), "eco": float(r["Eco_Tourism_Revenue_USD"]),
            "co2": float(r["Carbon_Footprint_kg"]), "waste": float(r["Waste_Management_Rating"]),
            "sat": float(r["Tourist_Satisfaction_Score"]), "rev_n": int(r["Number_of_Online_Reviews"]),
        })
tpl = open(os.path.join(ROOT, "tools", "replica_template.html"), encoding="utf-8").read()
ec = open(echarts_path, encoding="utf-8").read()
out = tpl.replace("__DATA__", json.dumps(rows, separators=(",", ":"))).replace("<script>__ECHARTS__</script>", "<script>" + ec + "</script>")
os.makedirs(os.path.join(ROOT, "Report_Preview"), exist_ok=True)
with open(os.path.join(ROOT, "Report_Preview", "Tourism_Report_Preview.html"), "w", encoding="utf-8") as f:
    f.write(out)
print(len(rows), len(out))
