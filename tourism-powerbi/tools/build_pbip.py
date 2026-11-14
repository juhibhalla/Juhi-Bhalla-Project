import json
import os
import uuid
import shutil

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
NAME = "Tourism_Analysis"
OUT = os.path.join(ROOT, "PowerBI")
SM = os.path.join(OUT, f"{NAME}.SemanticModel")
RP = os.path.join(OUT, f"{NAME}.Report")

NS = uuid.UUID("6f1c2d64-8a7e-4c55-9d7b-0e1f2a3b4c5d")


def tag(s):
    return str(uuid.uuid5(NS, s))


def dump(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)
        f.write("\n")


CSV_COLUMNS = [
    ("Country", "text", "string"),
    ("City", "text", "string"),
    ("Year", "Int64.Type", "int64"),
    ("Month", "Int64.Type", "int64"),
    ("Number_of_Tourists", "Int64.Type", "int64"),
    ("Purpose_of_Visit", "text", "string"),
    ("Average_Length_of_Stay", "number", "double"),
    ("Tourist_Spending_USD", "number", "double"),
    ("Hotel_Occupancy_Rate", "number", "double"),
    ("Number_of_Hotels", "Int64.Type", "int64"),
    ("Hotel_Rating", "text", "string"),
    ("Average_Room_Price_USD", "number", "double"),
    ("Tourism_Revenue_USD", "number", "double"),
    ("Employment_in_Tourism", "Int64.Type", "int64"),
    ("Contribution_to_GDP_Percent", "number", "double"),
    ("Number_of_Flights", "Int64.Type", "int64"),
    ("Airport_Passenger_Traffic", "Int64.Type", "int64"),
    ("Transport_Infrastructure_Quality", "number", "double"),
    ("Eco_Tourism_Revenue_USD", "number", "double"),
    ("Carbon_Footprint_kg", "number", "double"),
    ("Waste_Management_Rating", "number", "double"),
    ("Tourist_Satisfaction_Score", "number", "double"),
    ("Number_of_Online_Reviews", "Int64.Type", "int64"),
]

AVG_COLS = {
    "Average_Length_of_Stay", "Tourist_Spending_USD", "Hotel_Occupancy_Rate", "Hotel_Rating",
    "Average_Room_Price_USD", "Contribution_to_GDP_Percent", "Transport_Infrastructure_Quality",
    "Waste_Management_Rating", "Tourist_Satisfaction_Score",
}
HIDDEN = {"Year", "Month"}

tourism_m = [
    "let",
    "    Source = Csv.Document(File.Contents(CsvFilePath), [Delimiter = \",\", Columns = 23, Encoding = 65001, QuoteStyle = QuoteStyle.Csv]),",
    "    PromotedHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),",
    "    ChangedTypes = Table.TransformColumnTypes(PromotedHeaders, {"
    + ", ".join(f'{{"{c}", {t}}}' for c, t, _ in CSV_COLUMNS)
    + '}, "en-US"),',
    "    TrimmedText = Table.TransformColumns(ChangedTypes, {{\"Country\", Text.Trim, type text}, {\"City\", Text.Trim, type text}, {\"Purpose_of_Visit\", Text.Trim, type text}, {\"Hotel_Rating\", Text.Trim, type text}}),",
    "    RemovedBlankRows = Table.SelectRows(TrimmedText, each [Country] <> null and [Year] <> null and [Month] <> null),",
    "    RenamedColumns = Table.TransformColumnNames(RemovedBlankRows, each Text.Replace(_, \"_\", \" \")),",
    "    AddedDate = Table.AddColumn(RenamedColumns, \"Date\", each #date([Year], [Month], 1), type date),",
    "    AddedRatingOrder = Table.AddColumn(AddedDate, \"Rating Order\", each if [Hotel Rating] = \"Unrated\" then 0 else Number.From(Text.Start([Hotel Rating], 1)), Int64.Type)",
    "in",
    "    AddedRatingOrder",
]

date_m = [
    "let",
    "    StartDate = #date(2020, 1, 1),",
    "    EndDate = #date(2025, 12, 1),",
    "    MonthList = List.Generate(() => StartDate, each _ <= EndDate, each Date.AddMonths(_, 1)),",
    "    DateTable = Table.FromList(MonthList, Splitter.SplitByNothing(), {\"Date\"}),",
    "    TypedDate = Table.TransformColumnTypes(DateTable, {{\"Date\", type date}}),",
    "    AddedYear = Table.AddColumn(TypedDate, \"Year\", each Date.Year([Date]), Int64.Type),",
    "    AddedMonthNumber = Table.AddColumn(AddedYear, \"Month Number\", each Date.Month([Date]), Int64.Type),",
    "    AddedMonth = Table.AddColumn(AddedMonthNumber, \"Month\", each Date.ToText([Date], \"MMM\", \"en-US\"), type text),",
    "    AddedQuarter = Table.AddColumn(AddedMonth, \"Quarter\", each \"Q\" & Text.From(Date.QuarterOfYear([Date])), type text),",
    "    AddedYearMonth = Table.AddColumn(AddedQuarter, \"Year Month\", each Date.ToText([Date], \"yyyy-MM\", \"en-US\"), type text),",
    "    AddedMonthIndex = Table.AddColumn(AddedYearMonth, \"Month Index\", each (Date.Year([Date]) - 2020) * 12 + Date.Month([Date]), Int64.Type),",
    "    AddedPeriodType = Table.AddColumn(AddedMonthIndex, \"Period Type\", each if [Date] <= #date(2024, 12, 1) then \"Actual\" else \"Forecast\", type text)",
    "in",
    "    AddedPeriodType",
]


def col(name, dtype, source=None, hidden=False, summarize="none", fmt=None, sort_by=None, category=None):
    c = {"name": name, "dataType": dtype, "sourceColumn": source or name, "summarizeBy": summarize, "lineageTag": tag("col" + name + str(source))}
    if fmt:
        c["formatString"] = fmt
    if hidden:
        c["isHidden"] = True
    if sort_by:
        c["sortByColumn"] = sort_by
    if category:
        c["dataCategory"] = category
    return c


tourism_cols = []
for c, _, d in CSV_COLUMNS:
    n = c.replace("_", " ")
    summarize = "none" if d == "string" else ("average" if c in AVG_COLS else "sum")
    if c in ("Year", "Month"):
        summarize = "none"
    fmt = None
    if d == "int64":
        fmt = "#,0" if c not in ("Year", "Month") else "0"
    if d == "double":
        fmt = "#,0.00"
    tourism_cols.append(col(
        n, d, n, hidden=c in HIDDEN, summarize=summarize, fmt=fmt,
        sort_by="Rating Order" if c == "Hotel_Rating" else None,
        category={"Country": "Country", "City": "City"}.get(c),
    ))
tourism_cols.append(col("Date", "dateTime", "Date", hidden=True, fmt="yyyy-mm-dd"))
tourism_cols.append(col("Rating Order", "int64", "Rating Order", hidden=True, fmt="0"))

date_cols = [
    col("Date", "dateTime", fmt="mmm yyyy"),
    col("Year", "int64", fmt="0"),
    col("Month Number", "int64", hidden=True, fmt="0"),
    col("Month", "string", sort_by="Month Number"),
    col("Quarter", "string"),
    col("Year Month", "string", sort_by="Month Index"),
    col("Month Index", "int64", hidden=True, fmt="0"),
    col("Period Type", "string"),
]


def regression(measure, period_filter=True):
    return [
        "VAR Points =",
        "    CALCULATETABLE(",
        f"        ADDCOLUMNS(VALUES(DimDate[Month Index]), \"@y\", {measure}),",
        "        REMOVEFILTERS(DimDate),",
        "        DimDate[Period Type] = \"Actual\"",
        "    )",
        "VAR Fit = FILTER(Points, NOT ISBLANK([@y]))",
        "VAR n = COUNTROWS(Fit)",
        "VAR SumX = SUMX(Fit, DimDate[Month Index])",
        "VAR SumY = SUMX(Fit, [@y])",
        "VAR SumXY = SUMX(Fit, DimDate[Month Index] * [@y])",
        "VAR SumXX = SUMX(Fit, DimDate[Month Index] ^ 2)",
        "VAR Slope = DIVIDE(n * SumXY - SumX * SumY, n * SumXX - SumX ^ 2)",
        "VAR Intercept = DIVIDE(SumY - Slope * SumX, n)",
        "VAR x = MAX(DimDate[Month Index])",
    ]


def seasonal_index(measure):
    return [
        "VAR m = MAX(DimDate[Month Number])",
        "VAR MonthAvg = CALCULATE(AVERAGEX(VALUES(DimDate[Month Index]), " + measure + "), REMOVEFILTERS(DimDate), DimDate[Period Type] = \"Actual\", DimDate[Month Number] = m)",
        "VAR OverallAvg = CALCULATE(AVERAGEX(VALUES(DimDate[Month Index]), " + measure + "), REMOVEFILTERS(DimDate), DimDate[Period Type] = \"Actual\")",
        "VAR SeasonalIndex = DIVIDE(MonthAvg, OverallAvg, 1)",
    ]


def yoy(measure):
    return [
        "VAR SelectedYear = MAX(Tourism[Year])",
        f"VAR CurrentValue = CALCULATE({measure}, REMOVEFILTERS(DimDate), DimDate[Year] = SelectedYear)",
        f"VAR PriorValue = CALCULATE({measure}, REMOVEFILTERS(DimDate), DimDate[Year] = SelectedYear - 1)",
        "RETURN",
        "    DIVIDE(CurrentValue - PriorValue, PriorValue)",
    ]


MEASURES = [
    ("1 Market Analysis", "Total Tourists", ["SUM(Tourism[Number of Tourists])"], "#,0"),
    ("1 Market Analysis", "Tourist Nights", ["SUMX(Tourism, Tourism[Number of Tourists] * Tourism[Average Length of Stay])"], "#,0"),
    ("1 Market Analysis", "Avg Length of Stay", ["DIVIDE([Tourist Nights], [Total Tourists])"], "0.0"),
    ("1 Market Analysis", "Avg Satisfaction", ["AVERAGE(Tourism[Tourist Satisfaction Score])"], "0.00"),
    ("1 Market Analysis", "Online Reviews", ["SUM(Tourism[Number of Online Reviews])"], "#,0"),
    ("1 Market Analysis", "Airport Passenger Traffic", ["SUM(Tourism[Airport Passenger Traffic])"], "#,0"),
    ("1 Market Analysis", "Total Flights", ["SUM(Tourism[Number of Flights])"], "#,0"),
    ("1 Market Analysis", "Tourists YoY %", yoy("[Total Tourists]"), "+0.0%;-0.0%;0.0%"),
    ("1 Market Analysis", "Destination Share %", ["DIVIDE([Total Tourists], CALCULATE([Total Tourists], ALLSELECTED(Tourism[City]), ALLSELECTED(Tourism[Country])))"], "0.0%"),
    ("2 Revenue Forecasting", "Total Revenue", ["SUM(Tourism[Tourism Revenue USD])"], "\\$#,0"),
    ("2 Revenue Forecasting", "Avg Occupancy %", ["AVERAGE(Tourism[Hotel Occupancy Rate]) / 100"], "0.0%"),
    ("2 Revenue Forecasting", "Avg Room Price", ["AVERAGE(Tourism[Average Room Price USD])"], "\\$#,0.00"),
    ("2 Revenue Forecasting", "RevPAR", ["AVERAGEX(Tourism, Tourism[Average Room Price USD] * Tourism[Hotel Occupancy Rate] / 100)"], "\\$#,0.00"),
    ("2 Revenue Forecasting", "Revenue YoY %", yoy("[Total Revenue]"), "+0.0%;-0.0%;0.0%"),
    ("2 Revenue Forecasting", "Revenue Actual", ["IF(MAX(DimDate[Period Type]) = \"Actual\", [Total Revenue])"], "\\$#,0"),
    ("2 Revenue Forecasting", "Revenue Trend", regression("[Total Revenue]") + [
        "RETURN",
        "    IF(n > 1 && HASONEVALUE(DimDate[Year Month]), Intercept + Slope * x)",
    ], "\\$#,0"),
    ("2 Revenue Forecasting", "Revenue Forecast", regression("[Total Revenue]") + seasonal_index("[Total Revenue]") + [
        "RETURN",
        "    IF(n > 1 && HASONEVALUE(DimDate[Year Month]) && MAX(DimDate[Period Type]) = \"Forecast\", (Intercept + Slope * x) * SeasonalIndex)",
    ], "\\$#,0"),
    ("2 Revenue Forecasting", "2025 Revenue Forecast", [
        "SUMX(",
        "    CALCULATETABLE(VALUES(DimDate[Year Month]), REMOVEFILTERS(DimDate), DimDate[Period Type] = \"Forecast\"),",
        "    VAR CurrentMonth = DimDate[Year Month]",
        "    RETURN",
        "        CALCULATE([Revenue Forecast], REMOVEFILTERS(DimDate), DimDate[Year Month] = CurrentMonth)",
        ")",
    ], "\\$#,0"),
    ("2 Revenue Forecasting", "Revenue 3M Moving Avg", [
        "VAR CurrentIndex = MAX(DimDate[Month Index])",
        "RETURN",
        "    IF(",
        "        HASONEVALUE(DimDate[Year Month]) && MAX(DimDate[Period Type]) = \"Actual\",",
        "        CALCULATE(AVERAGEX(VALUES(DimDate[Month Index]), [Total Revenue]), REMOVEFILTERS(DimDate), DimDate[Month Index] > CurrentIndex - 3, DimDate[Month Index] <= CurrentIndex)",
        "    )",
    ], "\\$#,0"),
    ("2 Revenue Forecasting", "Occupancy Actual", ["IF(MAX(DimDate[Period Type]) = \"Actual\", [Avg Occupancy %])"], "0.0%"),
    ("2 Revenue Forecasting", "Occupancy Forecast", regression("[Avg Occupancy %]") + seasonal_index("[Avg Occupancy %]") + [
        "RETURN",
        "    IF(n > 1 && HASONEVALUE(DimDate[Year Month]), MIN(MAX((Intercept + Slope * x) * SeasonalIndex, 0), 1))",
    ], "0.0%"),
    ("3 Hospitality Insights", "Total Visitor Spend", ["SUMX(Tourism, Tourism[Number of Tourists] * Tourism[Tourist Spending USD])"], "\\$#,0"),
    ("3 Hospitality Insights", "Avg Spend per Tourist", ["DIVIDE([Total Visitor Spend], [Total Tourists])"], "\\$#,0.00"),
    ("3 Hospitality Insights", "Spend per Night", ["DIVIDE([Total Visitor Spend], [Tourist Nights])"], "\\$#,0.00"),
    ("3 Hospitality Insights", "Avg Hotels per City", ["AVERAGE(Tourism[Number of Hotels])"], "#,0"),
    ("3 Hospitality Insights", "Spend Share %", ["DIVIDE([Total Visitor Spend], CALCULATE([Total Visitor Spend], ALLSELECTED(Tourism[Hotel Rating])))"], "0.0%"),
    ("4 Tourism Policy", "Tourism Employment", ["SUM(Tourism[Employment in Tourism])"], "#,0"),
    ("4 Tourism Policy", "Avg GDP Contribution %", ["AVERAGE(Tourism[Contribution to GDP Percent]) / 100"], "0.0%"),
    ("4 Tourism Policy", "Eco-Tourism Revenue", ["SUM(Tourism[Eco Tourism Revenue USD])"], "\\$#,0"),
    ("4 Tourism Policy", "Eco-Tourism Share %", ["DIVIDE([Eco-Tourism Revenue], [Total Revenue])"], "0.0%"),
    ("4 Tourism Policy", "Carbon Footprint (t)", ["SUM(Tourism[Carbon Footprint kg]) / 1000"], "#,0"),
    ("4 Tourism Policy", "Carbon per Tourist (kg)", ["DIVIDE(SUM(Tourism[Carbon Footprint kg]), [Total Tourists])"], "#,0.0"),
    ("4 Tourism Policy", "Avg Infrastructure Quality", ["AVERAGE(Tourism[Transport Infrastructure Quality])"], "0.0"),
    ("4 Tourism Policy", "Avg Waste Management", ["AVERAGE(Tourism[Waste Management Rating])"], "0.0"),
    ("4 Tourism Policy", "Jobs per 1K Tourists", ["DIVIDE([Tourism Employment], [Total Tourists]) * 1000"], "#,0.0"),
]

measures = []
for folder, name, expr, fmt in MEASURES:
    measures.append({
        "name": name,
        "expression": expr if len(expr) > 1 else expr[0],
        "formatString": fmt,
        "displayFolder": folder,
        "lineageTag": tag("m" + name),
    })

model = {
    "name": "SemanticModel",
    "compatibilityLevel": 1567,
    "model": {
        "culture": "en-US",
        "dataAccessOptions": {"legacyRedirects": True, "returnErrorValuesAsNull": True},
        "defaultPowerBIDataSourceVersion": "powerBI_V3",
        "sourceQueryCulture": "en-US",
        "tables": [
            {
                "name": "Tourism",
                "lineageTag": tag("tTourism"),
                "columns": tourism_cols,
                "measures": measures,
                "partitions": [{"name": "Tourism", "mode": "import", "source": {"type": "m", "expression": tourism_m}}],
                "annotations": [{"name": "PBI_ResultType", "value": "Table"}],
            },
            {
                "name": "DimDate",
                "lineageTag": tag("tDimDate"),
                "dataCategory": "Time",
                "columns": date_cols,
                "partitions": [{"name": "DimDate", "mode": "import", "source": {"type": "m", "expression": date_m}}],
                "annotations": [{"name": "PBI_ResultType", "value": "Table"}],
            },
        ],
        "relationships": [
            {"name": tag("relDate"), "fromTable": "Tourism", "fromColumn": "Date", "toTable": "DimDate", "toColumn": "Date"}
        ],
        "expressions": [
            {
                "name": "CsvFilePath",
                "kind": "m",
                "expression": "\"C:\\PowerBI\\Tourism_Hospitality_Industry_Analysis.csv\" meta [IsParameterQuery = true, Type = \"Text\", IsParameterQueryRequired = true]",
                "lineageTag": tag("eCsvFilePath"),
                "annotations": [{"name": "PBI_ResultType", "value": "Text"}, {"name": "PBI_NavigationStepName", "value": "Navigation"}],
            }
        ],
        "annotations": [
            {"name": "__PBI_TimeIntelligenceEnabled", "value": "0"},
            {"name": "PBI_QueryOrder", "value": "[\"CsvFilePath\",\"Tourism\",\"DimDate\"]"},
            {"name": "PBIDesktopVersion", "value": "2.130.0"},
        ],
    },
}


def L(v):
    return {"expr": {"Literal": {"Value": v}}}


def S(s):
    return L("'" + s.replace("'", "''") + "'")


def color(c):
    return {"solid": {"color": S(c)}}


ALIAS = {"Tourism": "t", "DimDate": "d"}
MEASURE_NAMES = {m[1] for m in MEASURES}


def field(ref):
    table, prop = ref.split(".", 1)
    kind = "Measure" if (table == "Tourism" and prop in MEASURE_NAMES) else "Column"
    return kind, table, prop


def select_item(ref):
    kind, table, prop = field(ref)
    return {kind: {"Expression": {"SourceRef": {"Source": ALIAS[table]}}, "Property": prop}, "Name": ref, "NativeReferenceName": prop}


def expr_of(ref):
    kind, table, prop = field(ref)
    return {kind: {"Expression": {"SourceRef": {"Source": ALIAS[table]}}, "Property": prop}}


counter = [0]


def visual(page, x, y, w, h, vtype, roles=None, title=None, sort=None, objects=None, vc=None):
    counter[0] += 1
    vname = uuid.uuid5(NS, f"{page}-{counter[0]}").hex[:20]
    roles = roles or {}
    refs = []
    for r in roles.values():
        for f in r:
            if f not in refs:
                refs.append(f)
    tables = []
    for f in refs:
        t = f.split(".", 1)[0]
        if t not in tables:
            tables.append(t)
    single = {"visualType": vtype, "drillFilterOtherVisuals": True}
    if roles:
        single["projections"] = {
            role: [dict({"queryRef": f}, **({"active": True} if (vtype == "slicer" or role == "Category") and i == 0 else {})) for i, f in enumerate(fs)]
            for role, fs in roles.items()
        }
        q = {"Version": 2, "From": [{"Name": ALIAS[t], "Entity": t, "Type": 0} for t in tables], "Select": [select_item(f) for f in refs]}
        if sort:
            q["OrderBy"] = [{"Direction": 2 if sort[1] == "desc" else 1, "Expression": expr_of(sort[0])}]
        single["prototypeQuery"] = q
    if objects:
        single["objects"] = objects
    vco = {}
    if title:
        vco["title"] = [{"properties": {"show": L("true"), "text": S(title), "fontSize": L("11D"), "bold": L("true")}}]
    vco.setdefault("background", [{"properties": {"show": L("true"), "color": color("#FFFFFF"), "transparency": L("0D")}}])
    vco.setdefault("border", [{"properties": {"show": L("true"), "color": color("#E1E6EF"), "radius": L("8D")}}])
    vco.setdefault("dropShadow", [{"properties": {"show": L("true"), "preset": S("Center"), "transparency": L("85D")}}])
    if vc:
        vco.update(vc)
    single["vcObjects"] = vco
    cfg = {"name": vname, "layouts": [{"id": 0, "position": {"x": x, "y": y, "z": counter[0] * 100, "width": w, "height": h, "tabOrder": counter[0] * 100}}], "singleVisual": single}
    return {"x": x, "y": y, "z": counter[0] * 100, "width": w, "height": h, "config": json.dumps(cfg), "filters": "[]"}


def header(page, text, subtitle):
    counter[0] += 1
    vname = uuid.uuid5(NS, f"{page}-hdr-{counter[0]}").hex[:20]
    paragraphs = [
        {"textRuns": [{"value": text, "textStyle": {"fontWeight": "bold", "fontSize": "20pt", "color": "#FFFFFF", "fontFamily": "Segoe UI Semibold"}}]},
        {"textRuns": [{"value": subtitle, "textStyle": {"fontSize": "10pt", "color": "#CFE3F2", "fontFamily": "Segoe UI"}}]},
    ]
    cfg = {
        "name": vname,
        "layouts": [{"id": 0, "position": {"x": 0, "y": 0, "z": counter[0] * 100, "width": 1280, "height": 64}}],
        "singleVisual": {
            "visualType": "textbox",
            "drillFilterOtherVisuals": True,
            "objects": {"general": [{"properties": {"paragraphs": paragraphs}}]},
            "vcObjects": {
                "background": [{"properties": {"show": L("true"), "color": color("#0B3C5D"), "transparency": L("0D")}}],
                "padding": [{"properties": {"left": L("18D"), "top": L("6D")}}],
            },
        },
    }
    return {"x": 0, "y": 0, "z": counter[0] * 100, "width": 1280, "height": 64, "config": json.dumps(cfg), "filters": "[]"}


def slicer(page, x, y, w, ref, title):
    objects = {
        "data": [{"properties": {"mode": S("Dropdown")}}],
        "header": [{"properties": {"show": L("true"), "fontColor": color("#0B3C5D"), "textSize": L("10D")}}],
        "selection": [{"properties": {"selectAllCheckboxEnabled": L("true"), "singleSelect": L("false")}}],
    }
    return visual(page, x, y, w, 58, "slicer", {"Values": [ref]}, objects=objects, vc={
        "title": [{"properties": {"show": L("false")}}],
        "dropShadow": [{"properties": {"show": L("false")}}],
    })


def card(page, x, y, w, ref, label):
    objects = {
        "labels": [{"properties": {"fontSize": L("22D"), "color": color("#0B3C5D"), "labelDisplayUnits": L("0D"), "labelPrecision": L("1L")}}],
        "categoryLabels": [{"properties": {"show": L("true"), "fontSize": L("10D"), "color": color("#5B6B7F")}}],
    }
    return visual(page, x, y, w, 88, "card", {"Values": [ref]}, objects=objects, vc={
        "title": [{"properties": {"show": L("false")}}],
        "border": [{"properties": {"show": L("true"), "color": color("#1F77B4"), "radius": L("8D")}}],
    })


def data_labels(show=True):
    return {"labels": [{"properties": {"show": L("true" if show else "false"), "labelDisplayUnits": L("0D")}}]}


def legend(pos="Top"):
    return {"legend": [{"properties": {"show": L("true"), "position": S(pos)}}]}


def series_colors(pairs):
    out = []
    for ref, c in pairs:
        out.append({"properties": {"fill": color(c)}, "selector": {"metadata": ref}})
    return out


CARD_Y = 128
ROW1_Y = 226
ROW2_Y = 476
ROW_H = 238


def cards_row(page, refs):
    n = len(refs)
    gap = 10
    w = (1260 - gap * (n - 1)) // n
    return [card(page, 10 + i * (w + gap), CARD_Y, w, r, r) for i, r in enumerate(refs)]


def slicers_row(page, items):
    w = 240
    return [slicer(page, 10 + i * (w + 10), 66, w, ref, t) for i, (ref, t) in enumerate(items)]


pages = []

p = "market"
v = [header(p, "Market Analysis", "Travel trends and popular destinations | 2020 - 2024")]
v += slicers_row(p, [("DimDate.Year", "Year"), ("Tourism.Country", "Country"), ("Tourism.Purpose of Visit", "Purpose"), ("Tourism.Hotel Rating", "Hotel Rating")])
v += cards_row(p, ["Tourism.Total Tourists", "Tourism.Tourists YoY %", "Tourism.Tourist Nights", "Tourism.Avg Length of Stay", "Tourism.Avg Satisfaction", "Tourism.Airport Passenger Traffic"])
v.append(visual(p, 10, ROW1_Y, 620, ROW_H, "areaChart", {"Category": ["DimDate.Year Month"], "Y": ["Tourism.Total Tourists"]}, "Tourist Arrivals Trend", sort=("DimDate.Year Month", "asc"),
                objects={"dataPoint": series_colors([("Tourism.Total Tourists", "#1F77B4")])}))
v.append(visual(p, 640, ROW1_Y, 300, ROW_H, "donutChart", {"Category": ["Tourism.Purpose of Visit"], "Y": ["Tourism.Total Tourists"]}, "Tourists by Purpose of Visit", sort=("Tourism.Total Tourists", "desc"),
                objects={"legend": [{"properties": {"show": L("false")}}], "labels": [{"properties": {"show": L("true"), "labelStyle": S("Category, percent of total")}}]}))
v.append(visual(p, 950, ROW1_Y, 320, ROW_H, "clusteredColumnChart", {"Category": ["DimDate.Month"], "Y": ["Tourism.Total Tourists"]}, "Seasonality - Tourists by Month", sort=("DimDate.Month", "asc"),
                objects={"dataPoint": series_colors([("Tourism.Total Tourists", "#2CA58D")])}))
v.append(visual(p, 10, ROW2_Y, 410, ROW_H, "clusteredBarChart", {"Category": ["Tourism.Country"], "Y": ["Tourism.Total Tourists"]}, "Tourists by Country", sort=("Tourism.Total Tourists", "desc"),
                objects={"dataPoint": series_colors([("Tourism.Total Tourists", "#1F77B4")])}))
v.append(visual(p, 430, ROW2_Y, 410, ROW_H, "clusteredBarChart", {"Category": ["Tourism.City"], "Y": ["Tourism.Total Tourists"]}, "Most Popular Destinations (Cities)", sort=("Tourism.Total Tourists", "desc"),
                objects={"dataPoint": series_colors([("Tourism.Total Tourists", "#F28E2B")])}))
v.append(visual(p, 850, ROW2_Y, 420, ROW_H, "tableEx", {"Values": ["Tourism.City", "Tourism.Total Tourists", "Tourism.Destination Share %", "Tourism.Avg Satisfaction", "Tourism.Online Reviews"]}, "Destination Leaderboard", sort=("Tourism.Total Tourists", "desc")))
pages.append(("ReportSectionMarket", "Market Analysis", v))

p = "revenue"
v = [header(p, "Revenue Forecasting", "Hotel occupancy and revenue patterns with a 2025 seasonal-trend forecast")]
v += slicers_row(p, [("Tourism.Country", "Country"), ("Tourism.City", "City"), ("Tourism.Hotel Rating", "Hotel Rating"), ("Tourism.Purpose of Visit", "Purpose")])
v += cards_row(p, ["Tourism.Total Revenue", "Tourism.Revenue YoY %", "Tourism.Avg Occupancy %", "Tourism.Avg Room Price", "Tourism.RevPAR", "Tourism.2025 Revenue Forecast"])
v.append(visual(p, 10, ROW1_Y, 840, ROW_H, "lineChart", {"Category": ["DimDate.Year Month"], "Y": ["Tourism.Revenue Actual", "Tourism.Revenue 3M Moving Avg", "Tourism.Revenue Trend", "Tourism.Revenue Forecast"]}, "Monthly Revenue - Actual, Trend and 2025 Forecast", sort=("DimDate.Year Month", "asc"),
                objects=dict(legend("Top"), dataPoint=series_colors([("Tourism.Revenue Actual", "#1F77B4"), ("Tourism.Revenue 3M Moving Avg", "#9DB9D3"), ("Tourism.Revenue Trend", "#7F7F7F"), ("Tourism.Revenue Forecast", "#E15759")]))))
v.append(visual(p, 860, ROW1_Y, 410, ROW_H, "lineClusteredColumnComboChart", {"Category": ["DimDate.Year"], "Y": ["Tourism.Total Revenue"], "Y2": ["Tourism.Avg Occupancy %"]}, "Annual Revenue vs Occupancy", sort=("DimDate.Year", "asc"),
                objects=dict(legend("Top"), dataPoint=series_colors([("Tourism.Total Revenue", "#1F77B4"), ("Tourism.Avg Occupancy %", "#F28E2B")]))))
v.append(visual(p, 10, ROW2_Y, 620, ROW_H, "lineChart", {"Category": ["DimDate.Year Month"], "Y": ["Tourism.Occupancy Actual", "Tourism.Occupancy Forecast"]}, "Hotel Occupancy - Actual vs Forecast", sort=("DimDate.Year Month", "asc"),
                objects=dict(legend("Top"), dataPoint=series_colors([("Tourism.Occupancy Actual", "#2CA58D"), ("Tourism.Occupancy Forecast", "#E15759")]))))
v.append(visual(p, 640, ROW2_Y, 310, ROW_H, "clusteredColumnChart", {"Category": ["DimDate.Month"], "Y": ["Tourism.Avg Occupancy %"]}, "Occupancy Seasonality by Month", sort=("DimDate.Month", "asc"),
                objects={"dataPoint": series_colors([("Tourism.Avg Occupancy %", "#2CA58D")])}))
v.append(visual(p, 960, ROW2_Y, 310, ROW_H, "pivotTable", {"Rows": ["DimDate.Year"], "Columns": ["DimDate.Quarter"], "Values": ["Tourism.Total Revenue"]}, "Revenue by Year and Quarter"))
pages.append(("ReportSectionRevenue", "Revenue Forecasting", v))

p = "hospitality"
v = [header(p, "Hospitality Business Insights", "Customer preferences and spending habits")]
v += slicers_row(p, [("DimDate.Year", "Year"), ("Tourism.Country", "Country"), ("Tourism.Purpose of Visit", "Purpose"), ("Tourism.Hotel Rating", "Hotel Rating")])
v += cards_row(p, ["Tourism.Total Visitor Spend", "Tourism.Avg Spend per Tourist", "Tourism.Spend per Night", "Tourism.Avg Room Price", "Tourism.Avg Satisfaction", "Tourism.Online Reviews"])
v.append(visual(p, 10, ROW1_Y, 420, ROW_H, "lineClusteredColumnComboChart", {"Category": ["Tourism.Purpose of Visit"], "Y": ["Tourism.Avg Spend per Tourist"], "Y2": ["Tourism.Avg Length of Stay"]}, "Spend per Tourist and Length of Stay by Purpose", sort=("Tourism.Avg Spend per Tourist", "desc"),
                objects=dict(legend("Top"), dataPoint=series_colors([("Tourism.Avg Spend per Tourist", "#1F77B4"), ("Tourism.Avg Length of Stay", "#F28E2B")]))))
v.append(visual(p, 440, ROW1_Y, 420, ROW_H, "lineClusteredColumnComboChart", {"Category": ["Tourism.Hotel Rating"], "Y": ["Tourism.Avg Room Price"], "Y2": ["Tourism.Avg Satisfaction"]}, "Room Price and Satisfaction by Hotel Rating", sort=("Tourism.Hotel Rating", "asc"),
                objects=dict(legend("Top"), dataPoint=series_colors([("Tourism.Avg Room Price", "#2CA58D"), ("Tourism.Avg Satisfaction", "#E15759")]))))
v.append(visual(p, 870, ROW1_Y, 400, ROW_H, "donutChart", {"Category": ["Tourism.Hotel Rating"], "Y": ["Tourism.Total Visitor Spend"]}, "Share of Visitor Spend by Hotel Rating", sort=("Tourism.Hotel Rating", "asc"),
                objects={"legend": [{"properties": {"show": L("true"), "position": S("Right")}}], "labels": [{"properties": {"show": L("true"), "labelStyle": S("Percent of total")}}]}))
v.append(visual(p, 10, ROW2_Y, 620, ROW_H, "scatterChart", {"Category": ["Tourism.City"], "X": ["Tourism.Avg Room Price"], "Y": ["Tourism.Avg Satisfaction"], "Size": ["Tourism.Total Tourists"]}, "Value for Money - Room Price vs Satisfaction by City",
                objects={"dataPoint": [{"properties": {"fill": color("#1F77B4")}}], "categoryLabels": [{"properties": {"show": L("true")}}]}))
v.append(visual(p, 640, ROW2_Y, 630, ROW_H, "pivotTable", {"Rows": ["Tourism.Purpose of Visit"], "Columns": ["Tourism.Hotel Rating"], "Values": ["Tourism.Avg Spend per Tourist"]}, "Avg Spend per Tourist - Purpose x Hotel Rating"))
pages.append(("ReportSectionHospitality", "Hospitality Insights", v))

p = "policy"
v = [header(p, "Tourism Policy Evaluation", "Economic contribution, employment, sustainability and infrastructure")]
v += slicers_row(p, [("DimDate.Year", "Year"), ("Tourism.Country", "Country"), ("Tourism.Purpose of Visit", "Purpose")])
v += cards_row(p, ["Tourism.Tourism Employment", "Tourism.Avg GDP Contribution %", "Tourism.Eco-Tourism Revenue", "Tourism.Eco-Tourism Share %", "Tourism.Carbon per Tourist (kg)", "Tourism.Avg Infrastructure Quality"])
v.append(visual(p, 10, ROW1_Y, 410, ROW_H, "clusteredBarChart", {"Category": ["Tourism.Country"], "Y": ["Tourism.Avg GDP Contribution %"]}, "Tourism Contribution to GDP by Country", sort=("Tourism.Avg GDP Contribution %", "desc"),
                objects={"dataPoint": series_colors([("Tourism.Avg GDP Contribution %", "#0B3C5D")])}))
v.append(visual(p, 430, ROW1_Y, 420, ROW_H, "scatterChart", {"Category": ["Tourism.Country"], "X": ["Tourism.Carbon per Tourist (kg)"], "Y": ["Tourism.Eco-Tourism Share %"], "Size": ["Tourism.Total Revenue"]}, "Sustainability - Carbon per Tourist vs Eco-Tourism Share",
                objects={"dataPoint": [{"properties": {"fill": color("#2CA58D")}}], "categoryLabels": [{"properties": {"show": L("true")}}]}))
v.append(visual(p, 860, ROW1_Y, 410, ROW_H, "lineClusteredColumnComboChart", {"Category": ["DimDate.Year"], "Y": ["Tourism.Tourism Employment"], "Y2": ["Tourism.Eco-Tourism Share %"]}, "Employment and Eco-Tourism Share by Year", sort=("DimDate.Year", "asc"),
                objects=dict(legend("Top"), dataPoint=series_colors([("Tourism.Tourism Employment", "#1F77B4"), ("Tourism.Eco-Tourism Share %", "#2CA58D")]))))
v.append(visual(p, 10, ROW2_Y, 840, ROW_H, "tableEx", {"Values": ["Tourism.Country", "Tourism.Tourism Employment", "Tourism.Jobs per 1K Tourists", "Tourism.Avg GDP Contribution %", "Tourism.Eco-Tourism Share %", "Tourism.Carbon per Tourist (kg)", "Tourism.Avg Infrastructure Quality", "Tourism.Avg Waste Management"]}, "Country Policy Scorecard", sort=("Tourism.Avg GDP Contribution %", "desc")))
v.append(visual(p, 860, ROW2_Y, 410, ROW_H, "clusteredBarChart", {"Category": ["Tourism.Country"], "Y": ["Tourism.Avg Infrastructure Quality", "Tourism.Avg Waste Management"]}, "Infrastructure and Waste Management by Country", sort=("Tourism.Avg Infrastructure Quality", "desc"),
                objects=dict(legend("Top"), dataPoint=series_colors([("Tourism.Avg Infrastructure Quality", "#1F77B4"), ("Tourism.Avg Waste Management", "#F28E2B")]))))
pages.append(("ReportSectionPolicy", "Tourism Policy", v))

sections = []
for i, (sname, display, vcs) in enumerate(pages):
    sections.append({
        "name": sname,
        "displayName": display,
        "displayOption": 1,
        "width": 1280,
        "height": 720,
        "ordinal": i,
        "config": json.dumps({"objects": {"background": [{"properties": {"color": color("#F3F6FA"), "transparency": L("0D")}}]}}),
        "filters": "[]",
        "visualContainers": vcs,
    })

THEME_NAME = "TourismTheme.json"
theme = {
    "name": "Tourism Theme",
    "dataColors": ["#1F77B4", "#F28E2B", "#2CA58D", "#E15759", "#0B3C5D", "#9C755F", "#B07AA1", "#EDC948", "#76B7B2", "#FF9DA7"],
    "background": "#FFFFFF",
    "foreground": "#1B2A3A",
    "tableAccent": "#1F77B4",
    "good": "#2CA58D",
    "neutral": "#EDC948",
    "bad": "#E15759",
    "textClasses": {
        "title": {"fontFace": "Segoe UI Semibold", "fontSize": 11, "color": "#1B2A3A"},
        "label": {"fontFace": "Segoe UI", "fontSize": 9, "color": "#5B6B7F"},
        "callout": {"fontFace": "Segoe UI Semibold", "fontSize": 22, "color": "#0B3C5D"},
    },
    "visualStyles": {
        "page": {"*": {"background": [{"color": {"solid": {"color": "#F3F6FA"}}, "transparency": 0}]}},
        "*": {"*": {
            "border": [{"show": True, "color": {"solid": {"color": "#E1E6EF"}}, "radius": 8}],
            "dropShadow": [{"show": True, "preset": "Center", "transparency": 85}],
        }},
    },
}

report = {
    "config": json.dumps({
        "version": "5.43",
        "themeCollection": {"customTheme": {"name": THEME_NAME, "version": "5.43", "type": 1}},
        "activeSectionIndex": 0,
        "defaultDrillFilterOtherVisuals": True,
        "linguisticSchemaSyncVersion": 0,
        "settings": {"useNewFilterPaneExperience": True, "allowChangeFilterTypes": True, "useStylableVisualContainerHeader": True, "exportDataMode": 1, "useDefaultAggregateDisplayName": True},
        "objects": {"outspacePane": [{"properties": {"expanded": L("false")}}]},
    }),
    "layoutOptimization": 0,
    "resourcePackages": [
        {"resourcePackage": {"disabled": False, "items": [{"name": THEME_NAME, "path": THEME_NAME, "type": 201}], "name": "RegisteredResources", "type": 1}}
    ],
    "sections": sections,
}

if os.path.exists(OUT):
    shutil.rmtree(OUT)

dump(os.path.join(OUT, f"{NAME}.pbip"), {
    "$schema": "https://developer.microsoft.com/json-schemas/fabric/pbip/pbipProperties/1.0.0/schema.json",
    "version": "1.0",
    "artifacts": [{"report": {"path": f"{NAME}.Report"}}],
    "settings": {"enableAutoRecovery": True},
})
dump(os.path.join(SM, "definition.pbism"), {
    "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/semanticModel/definitionProperties/1.0.0/schema.json",
    "version": "4.2",
    "settings": {},
})
dump(os.path.join(SM, "model.bim"), model)
dump(os.path.join(SM, ".platform"), {
    "$schema": "https://developer.microsoft.com/json-schemas/fabric/gitIntegration/platformProperties/2.0.0/schema.json",
    "metadata": {"type": "SemanticModel", "displayName": NAME},
    "config": {"version": "2.0", "logicalId": tag("sm")},
})
dump(os.path.join(RP, "definition.pbir"), {
    "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definitionProperties/1.0.0/schema.json",
    "version": "4.0",
    "datasetReference": {"byPath": {"path": f"../{NAME}.SemanticModel"}},
})
dump(os.path.join(RP, "report.json"), report)
dump(os.path.join(RP, "StaticResources", "RegisteredResources", THEME_NAME), theme)
dump(os.path.join(RP, ".platform"), {
    "$schema": "https://developer.microsoft.com/json-schemas/fabric/gitIntegration/platformProperties/2.0.0/schema.json",
    "metadata": {"type": "Report", "displayName": NAME},
    "config": {"version": "2.0", "logicalId": tag("rp")},
})
dump(os.path.join(OUT, THEME_NAME), theme)
with open(os.path.join(OUT, ".gitignore"), "w") as f:
    f.write("**/.pbi/localSettings.json\n**/.pbi/cache.abf\n")

with open(os.path.join(ROOT, "tools", "measures.json"), "w", encoding="utf-8") as f:
    json.dump([{"folder": a, "name": b, "dax": "\n".join(c), "format": d} for a, b, c, d in MEASURES], f, indent=2)

print("pages", len(sections), "visuals", sum(len(s["visualContainers"]) for s in sections), "measures", len(MEASURES))
