const fs = require("fs");
const path = require("path");
const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, Table, TableRow, TableCell, WidthType, ShadingType,
  AlignmentType, ImageRun, PageBreak, LevelFormat, BorderStyle, TableOfContents, Footer, PageNumber, Header,
} = require("docx");

const SP = process.argv[2];
const ROOT = process.argv[3];
const OUT = process.argv[4];
const measures = JSON.parse(fs.readFileSync(path.join(ROOT, "tools", "measures.json"), "utf8")).map(m => Object.assign(m, { format: m.format.replace(/\\\$/g, "$") }));

const FONT = "Calibri";
const NAVY = "0B3C5D";
const W = 9026;

const P = (text, opts = {}) => new Paragraph({ spacing: { after: 120 }, ...opts, children: runs(text) });
function runs(text) {
  if (Array.isArray(text)) return text;
  const parts = String(text).split(/(\*\*[^*]+\*\*)/g).filter(Boolean);
  return parts.map(t => t.startsWith("**") ? new TextRun({ text: t.slice(2, -2), bold: true }) : new TextRun(t));
}
const H1 = t => new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun(t)] });
const H2 = t => new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun(t)] });
const H3 = t => new Paragraph({ heading: HeadingLevel.HEADING_3, children: [new TextRun(t)] });
const B = (t, lvl = 0) => new Paragraph({ numbering: { reference: "bullets", level: lvl }, spacing: { after: 60 }, children: runs(t) });
let numRef = 0;
function steps(items) {
  const ref = "steps" + (numRef++);
  numberingConfigs.push({ reference: ref, levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 540, hanging: 360 } } } }] });
  return items.map(t => new Paragraph({ numbering: { reference: ref, level: 0 }, spacing: { after: 70 }, children: runs(t) }));
}
const numberingConfigs = [
  { reference: "bullets", levels: [
    { level: 0, format: LevelFormat.BULLET, text: "\u2022", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 540, hanging: 300 } } } },
    { level: 1, format: LevelFormat.BULLET, text: "\u2013", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 1000, hanging: 300 } } } },
  ] },
];
function code(text) {
  const lines = text.split("\n");
  return lines.map((l, i) => new Paragraph({
    shading: { type: ShadingType.CLEAR, color: "auto", fill: "F2F4F7" },
    spacing: { before: i === 0 ? 60 : 0, after: i === lines.length - 1 ? 140 : 0, line: 250 },
    indent: { left: 120, right: 120 },
    border: i === 0 ? { top: { style: BorderStyle.SINGLE, size: 4, color: "D0D6DE", space: 4 } } : (i === lines.length - 1 ? { bottom: { style: BorderStyle.SINGLE, size: 4, color: "D0D6DE", space: 4 } } : undefined),
    children: [new TextRun({ text: l.length ? l : " ", font: "Consolas", size: 17 })],
  }));
}
function note(text) {
  return new Paragraph({
    shading: { type: ShadingType.CLEAR, color: "auto", fill: "E8F1F9" },
    border: { left: { style: BorderStyle.SINGLE, size: 18, color: "1F77B4", space: 8 } },
    spacing: { before: 80, after: 160 }, indent: { left: 160, right: 120 },
    children: runs(text),
  });
}
const border = { style: BorderStyle.SINGLE, size: 4, color: "C9D1DC" };
const borders = { top: border, bottom: border, left: border, right: border };
function table(headers, rows, widths) {
  const total = widths.reduce((a, b) => a + b, 0);
  const mk = (t, hdr, w, shade) => new TableCell({
    width: { size: w, type: WidthType.DXA }, borders,
    shading: { type: ShadingType.CLEAR, color: "auto", fill: hdr ? NAVY : (shade ? "F5F7FA" : "FFFFFF") },
    margins: { top: 60, bottom: 60, left: 100, right: 100 },
    children: String(t).split("\n").map(line => new Paragraph({ children: hdr ? [new TextRun({ text: line, bold: true, color: "FFFFFF", size: 19 })] : runs(line).map(r => r) })),
  });
  return new Table({
    width: { size: total, type: WidthType.DXA }, columnWidths: widths,
    rows: [
      new TableRow({ tableHeader: true, children: headers.map((h, i) => mk(h, true, widths[i])) }),
      ...rows.map((r, ri) => new TableRow({ children: r.map((c, i) => mk(c, false, widths[i], ri % 2 === 1)) })),
    ],
  });
}
const gap = () => new Paragraph({ spacing: { after: 100 }, children: [] });
function shot(file, caption) {
  return [
    new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 120, after: 60 }, children: [new ImageRun({ type: "jpg", data: fs.readFileSync(file), transformation: { width: 600, height: 337.5 } })] }),
    new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 200 }, children: [new TextRun({ text: caption, italics: true, size: 18, color: "5B6B7F" })] }),
  ];
}
const pb = () => new Paragraph({ children: [new PageBreak()] });

const c = [];

c.push(new Paragraph({ spacing: { before: 2400, after: 200 }, children: [new TextRun({ text: "Tourism & Hospitality Industry Analysis", bold: true, size: 56, color: NAVY, font: FONT })] }));
c.push(new Paragraph({ spacing: { after: 400 }, children: [new TextRun({ text: "Interactive Power BI Report \u2013 Step-by-Step Build Guide", size: 32, color: "1F77B4" })] }));
c.push(new Paragraph({ border: { bottom: { style: BorderStyle.SINGLE, size: 12, color: "F28E2B", space: 6 } }, spacing: { after: 400 }, children: [] }));
c.push(P("Use cases covered:"));
["Market Analysis \u2013 identify travel trends and popular destinations",
 "Revenue Forecasting \u2013 predict hotel occupancy rates and revenue patterns",
 "Hospitality Business Insights \u2013 analyse customer preferences and spending habits",
 "Tourism Policy Evaluation \u2013 support government tourism strategies"].forEach(t => c.push(B(t)));
c.push(new Paragraph({ spacing: { before: 600 }, children: [new TextRun({ text: "Dataset: Tourism_Hospitality_Industry_Analysis.csv  |  500 records  |  23 columns  |  2020 \u2013 2024", color: "5B6B7F", size: 20 })] }));
c.push(pb());

c.push(new Paragraph({ children: [new TextRun({ text: "Contents", bold: true, size: 32, color: NAVY })], spacing: { after: 200 } }));
c.push(new TableOfContents("Contents", { hyperlink: true, headingStyleRange: "1-2" }));
c.push(note("If the contents list is empty, right-click it in Word and choose **Update Field**."));
c.push(pb());

c.push(H1("1. Overview"));
c.push(P("This guide explains, step by step, how the interactive Power BI report for the tourism and hospitality dataset is built. It covers loading and cleaning the data, building the data model, writing the DAX measures and designing the four report pages, one per use case."));
c.push(P("The report itself is kept free of commentary: every page contains only a page header, slicers, KPI cards and visuals. All explanation lives in this document."));
c.push(H2("1.1 Deliverables"));
c.push(table(["File / folder", "Purpose"], [
  ["PowerBI/Tourism_Analysis.pbip", "Power BI Project file. Double-click to open the complete report in Power BI Desktop."],
  ["PowerBI/Tourism_Analysis.SemanticModel/", "Data model: Power Query steps, tables, relationship and all 35 DAX measures."],
  ["PowerBI/Tourism_Analysis.Report/", "The four report pages, visuals, slicers and the custom theme."],
  ["PowerBI/TourismTheme.json", "Colour theme. Can be imported into any report through View > Themes."],
  ["data/Tourism_Hospitality_Industry_Analysis.csv", "Source dataset."],
  ["Report_Preview/Tourism_Report_Preview.html", "Browser-based interactive preview of the same report. Opens without Power BI."],
  ["Video/Tourism_Report_Walkthrough.mp4", "Short walkthrough video of the report pages and interactions."],
  ["Docs/Tourism_PowerBI_Report_Guide.docx", "This document."],
], [3700, 5326]));
c.push(gap());
c.push(H2("1.2 About the dataset"));
c.push(P("Each row is a monthly snapshot of one city: tourist volumes, visit purpose, spending, hotel performance, economic indicators, transport and sustainability metrics. The file has no missing values."));
c.push(table(["Attribute", "Value"], [
  ["Records", "500 rows, 23 columns"],
  ["Time span", "January 2020 \u2013 December 2024 (monthly; Year and Month columns)"],
  ["Geography", "20 countries, 56 cities"],
  ["Purpose of visit", "Business, Cultural, Educational, Family Visit, Leisure, Medical, Religious"],
  ["Hotel rating", "Unrated, 1-star, 2-star, 3-star, 4-star, 5-star"],
], [2600, 6426]));
c.push(gap());
c.push(table(["Use case", "Columns used"], [
  ["Market Analysis", "Country, City, Year, Month, Number_of_Tourists, Purpose_of_Visit, Average_Length_of_Stay, Tourist_Satisfaction_Score, Number_of_Online_Reviews, Airport_Passenger_Traffic"],
  ["Revenue Forecasting", "Tourism_Revenue_USD, Hotel_Occupancy_Rate, Average_Room_Price_USD, Hotel_Rating, Year, Month"],
  ["Hospitality Insights", "Tourist_Spending_USD, Average_Length_of_Stay, Average_Room_Price_USD, Hotel_Rating, Purpose_of_Visit, Tourist_Satisfaction_Score, Number_of_Hotels"],
  ["Tourism Policy", "Employment_in_Tourism, Contribution_to_GDP_Percent, Eco_Tourism_Revenue_USD, Carbon_Footprint_kg, Transport_Infrastructure_Quality, Waste_Management_Rating, Number_of_Flights"],
], [2600, 6426]));

c.push(pb());
c.push(H1("2. Quick start \u2013 open the ready-made report"));
c.push(P("The fastest route is to open the Power BI Project that is already built. You need Power BI Desktop (free, Windows). Use a 2024 or later release."));
c.push(...steps([
  "Copy the whole **tourism-powerbi** folder to your PC, for example to **C:\\PowerBI\\tourism-powerbi**.",
  "Copy **data\\Tourism_Hospitality_Industry_Analysis.csv** to **C:\\PowerBI\\**. The report looks for the file at C:\\PowerBI\\Tourism_Hospitality_Industry_Analysis.csv by default.",
  "Older Power BI Desktop versions only: go to File > Options and settings > Options > Preview features, tick **Power BI Project (.pbip) save option**, and restart Power BI Desktop.",
  "Double-click **PowerBI\\Tourism_Analysis.pbip**. Power BI Desktop opens the report. The visuals are empty at first because a project file stores no data.",
  "To keep the CSV somewhere else, go to Home > Transform data > **Edit parameters** and set **CsvFilePath** to the full path of the CSV.",
  "Click **Home > Refresh**. All four pages fill with data.",
  "Optional: use **File > Save as** and choose the .pbix type to get a single-file report you can share or publish.",
]));
c.push(note("If Power BI Desktop asks about data privacy levels on refresh, choose **Ignore privacy levels** or set the file source to **Organizational**. The data is a local CSV file."));
c.push(note("If the colours do not look like the screenshots in this guide, go to **View > Themes > Browse for themes** and select **PowerBI\\TourismTheme.json**."));
c.push(P("Sections 3 to 9 explain how the same report is built from a blank file. Follow them if you want to rebuild the report yourself or learn how each part works."));

c.push(pb());
c.push(H1("3. Load and transform the data (Power Query)"));
c.push(H2("3.1 Create the file path parameter"));
c.push(...steps([
  "Open a blank report in Power BI Desktop and click **Home > Transform data** to open Power Query Editor.",
  "Click **Manage Parameters > New Parameter**. Set Name = **CsvFilePath**, Type = **Text**, Current Value = the full path of the CSV file. Click OK.",
]));
c.push(H2("3.2 Import and clean the Tourism table"));
c.push(...steps([
  "Click **New Source > Text/CSV**, select the CSV file and click **Transform Data**.",
  "Rename the query to **Tourism**.",
  "In **Advanced Editor**, replace the hard-coded path with the CsvFilePath parameter (see the code below).",
  "Set data types with locale **English (United States)**. This makes decimals like 12.4 parse correctly on any regional setting.",
  "Trim the text columns (Country, City, Purpose_of_Visit, Hotel_Rating) to remove stray spaces.",
  "Filter out blank rows. This is a safety step; the current file has none.",
  "Replace underscores in column names with spaces to get friendly field names, for example Number of Tourists.",
  "Add a custom column **Date** = first day of the month (#date([Year],[Month],1)). This column links the data to the calendar table.",
  "Add a custom column **Rating Order** (Unrated = 0, 1-star = 1 \u2026 5-star = 5). It is used to sort hotel ratings correctly.",
]));
c.push(P("The complete query:"));
c.push(...code(`let
    Source = Csv.Document(File.Contents(CsvFilePath), [Delimiter = ",", Columns = 23, Encoding = 65001, QuoteStyle = QuoteStyle.Csv]),
    PromotedHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),
    ChangedTypes = Table.TransformColumnTypes(PromotedHeaders, {
        {"Country", type text}, {"City", type text}, {"Year", Int64.Type}, {"Month", Int64.Type},
        {"Number_of_Tourists", Int64.Type}, {"Purpose_of_Visit", type text},
        {"Average_Length_of_Stay", type number}, {"Tourist_Spending_USD", type number},
        {"Hotel_Occupancy_Rate", type number}, {"Number_of_Hotels", Int64.Type},
        {"Hotel_Rating", type text}, {"Average_Room_Price_USD", type number},
        {"Tourism_Revenue_USD", type number}, {"Employment_in_Tourism", Int64.Type},
        {"Contribution_to_GDP_Percent", type number}, {"Number_of_Flights", Int64.Type},
        {"Airport_Passenger_Traffic", Int64.Type}, {"Transport_Infrastructure_Quality", type number},
        {"Eco_Tourism_Revenue_USD", type number}, {"Carbon_Footprint_kg", type number},
        {"Waste_Management_Rating", type number}, {"Tourist_Satisfaction_Score", type number},
        {"Number_of_Online_Reviews", Int64.Type}}, "en-US"),
    TrimmedText = Table.TransformColumns(ChangedTypes, {{"Country", Text.Trim, type text},
        {"City", Text.Trim, type text}, {"Purpose_of_Visit", Text.Trim, type text},
        {"Hotel_Rating", Text.Trim, type text}}),
    RemovedBlankRows = Table.SelectRows(TrimmedText, each [Country] <> null and [Year] <> null and [Month] <> null),
    RenamedColumns = Table.TransformColumnNames(RemovedBlankRows, each Text.Replace(_, "_", " ")),
    AddedDate = Table.AddColumn(RenamedColumns, "Date", each #date([Year], [Month], 1), type date),
    AddedRatingOrder = Table.AddColumn(AddedDate, "Rating Order", each
        if [Hotel Rating] = "Unrated" then 0 else Number.From(Text.Start([Hotel Rating], 1)), Int64.Type)
in
    AddedRatingOrder`));
c.push(H2("3.3 Create the DimDate calendar table"));
c.push(P("A separate monthly calendar table is used for all time slicers and time axes. It runs to December 2025 so the forecast months have somewhere to plot. Create it with **New Source > Blank Query**, name it **DimDate**, and paste this into Advanced Editor:"));
c.push(...code(`let
    StartDate = #date(2020, 1, 1),
    EndDate = #date(2025, 12, 1),
    MonthList = List.Generate(() => StartDate, each _ <= EndDate, each Date.AddMonths(_, 1)),
    DateTable = Table.FromList(MonthList, Splitter.SplitByNothing(), {"Date"}),
    TypedDate = Table.TransformColumnTypes(DateTable, {{"Date", type date}}),
    AddedYear = Table.AddColumn(TypedDate, "Year", each Date.Year([Date]), Int64.Type),
    AddedMonthNumber = Table.AddColumn(AddedYear, "Month Number", each Date.Month([Date]), Int64.Type),
    AddedMonth = Table.AddColumn(AddedMonthNumber, "Month", each Date.ToText([Date], "MMM", "en-US"), type text),
    AddedQuarter = Table.AddColumn(AddedMonth, "Quarter", each "Q" & Text.From(Date.QuarterOfYear([Date])), type text),
    AddedYearMonth = Table.AddColumn(AddedQuarter, "Year Month", each Date.ToText([Date], "yyyy-MM", "en-US"), type text),
    AddedMonthIndex = Table.AddColumn(AddedYearMonth, "Month Index", each (Date.Year([Date]) - 2020) * 12 + Date.Month([Date]), Int64.Type),
    AddedPeriodType = Table.AddColumn(AddedMonthIndex, "Period Type", each if [Date] <= #date(2024, 12, 1) then "Actual" else "Forecast", type text)
in
    AddedPeriodType`));
c.push(P("Click **Home > Close & Apply** to load both tables."));

c.push(pb());
c.push(H1("4. Build the data model"));
c.push(H2("4.1 Relationship"));
c.push(...steps([
  "Open **Model view** (the third icon on the left).",
  "Drag **Tourism[Date]** onto **DimDate[Date]**. This creates a Many-to-one (*:1), single-direction relationship from Tourism to DimDate.",
  "Optional: File > Options > Current file > Data Load. Untick **Auto date/time**. The model has its own calendar table, so the hidden auto-date tables are not needed.",
]));
c.push(H2("4.2 Sorting, hiding and data categories"));
c.push(table(["Column", "Setting", "Why"], [
  ["DimDate[Month]", "Sort by column = Month Number", "Months show Jan \u2192 Dec instead of alphabetical order"],
  ["DimDate[Year Month]", "Sort by column = Month Index", "Correct time order on monthly axes"],
  ["Tourism[Hotel Rating]", "Sort by column = Rating Order", "Unrated, 1-star \u2026 5-star in order"],
  ["Tourism[Year], [Month], [Date], [Rating Order]", "Hide in report view", "Users filter time with DimDate only, so selections stay consistent"],
  ["DimDate[Month Number], [Month Index]", "Hide in report view", "Helper columns"],
  ["Tourism[Country]", "Data category = Country", "Enables map visuals if you add them later"],
  ["Tourism[City]", "Data category = City", "Same as above"],
  ["DimDate[Year]", "Summarization = Don't summarize", "Year acts as a category, not a number"],
], [3000, 3000, 3026]));
c.push(note("How to set a sort column: select the column in the Data pane, then on the **Column tools** ribbon click **Sort by column** and choose the helper column."));

c.push(pb());
c.push(H1("5. Create the DAX measures"));
c.push(P("All calculations are explicit measures stored in the Tourism table and grouped into four display folders, one per use case. To create a measure, select the **Tourism** table, click **Home > New measure**, paste the formula, then set the format on the **Measure tools** ribbon and type the folder name in Model view > Properties > **Display folder**."));
const folders = [...new Set(measures.map(m => m.folder))];
const simple = measures.filter(m => !m.dax.includes("\n"));
const complex = measures.filter(m => m.dax.includes("\n"));
folders.forEach(f => {
  c.push(H2("5." + f.slice(0, 1) + " " + f.slice(2) + " measures"));
  const rows = simple.filter(m => m.folder === f).map(m => [m.name, m.dax, m.format]);
  if (rows.length) c.push(table(["Measure", "DAX expression", "Format"], rows, [2300, 5126, 1600]));
  complex.filter(m => m.folder === f).forEach(m => {
    c.push(H3(m.name + "  (format: " + m.format + ")"));
    c.push(...code(m.name + " =\n" + m.dax));
  });
});
c.push(H2("5.5 How the forecast works"));
c.push(P("The Revenue Forecasting page uses a **seasonal linear-trend forecast**, written entirely in DAX so it reacts to every slicer:"));
c.push(B("**Trend.** A least-squares straight line is fitted to the monthly values for Jan 2020 \u2013 Dec 2024 (60 months). x = Month Index (1\u201360) and y = monthly revenue or average occupancy. Slope = (n\u00b7\u03a3xy \u2212 \u03a3x\u00b7\u03a3y) / (n\u00b7\u03a3x\u00b2 \u2212 (\u03a3x)\u00b2)."));
c.push(B("**Seasonality.** For each calendar month, a seasonal index = (average of that month across the five years) \u00f7 (average of all months). A value above 1 marks a stronger-than-average month."));
c.push(B("**Forecast.** The forecast for each 2025 month = trend value \u00d7 seasonal index. **2025 Revenue Forecast** adds up the 12 monthly forecasts."));
c.push(B("**Filters.** REMOVEFILTERS(DimDate) makes the model always learn from the full history. Country, city, rating and purpose slicers still apply, so selecting Japan gives a Japan-specific forecast."));
c.push(note("Alternative: you can also add Power BI's built-in forecast to a line chart with a continuous date axis (Analytics pane > Forecast). The DAX approach is used here because its numbers can be shown in cards and tables and stay consistent with slicers."));

c.push(pb());
c.push(H1("6. Report setup and theme"));
c.push(...steps([
  "Page size: click on an empty part of the canvas, then go to Format page > Canvas settings > Type = **16:9** (1280 \u00d7 720).",
  "Theme: go to **View > Themes > Browse for themes** and select **TourismTheme.json**. This sets the colours (navy #0B3C5D, blue #1F77B4, orange #F28E2B, teal #2CA58D, red #E15759), a light grey page background (#F3F6FA) and rounded white visual cards with a soft shadow.",
  "Create four pages and rename them (double-click the tab): **Market Analysis**, **Revenue Forecasting**, **Hospitality Insights**, **Tourism Policy**.",
  "Header on each page: Insert > **Text box**, size 1280 \u00d7 64 at position 0,0. Background colour #0B3C5D. Type the page title in white 20 pt bold, with a one-line subtitle under it in 10 pt.",
  "Use the same layout grid on every page: slicers at y = 66, KPI cards at y = 128 (height 88), first visual row at y = 226 and second row at y = 476 (height 238 each). Exact positions are under Format > General > Properties.",
]));
c.push(H2("6.1 Slicers (all pages)"));
c.push(...steps([
  "Insert a **Slicer** visual and drag the field into **Field**.",
  "Format > Visual > Slicer settings > Options > Style = **Dropdown**. Turn on **Multi-select with CTRL** and the **Select all** option.",
  "Turn off the visual title. The slicer header already shows the field name.",
  "Size: 240 \u00d7 58, placed side by side every 250 px starting at x = 10.",
  "Optional: to keep a selection when switching pages, use View > **Sync slicers** and tick Sync for each page.",
]));
c.push(H2("6.2 KPI cards (all pages)"));
c.push(...steps([
  "Insert a **Card** visual and drag one measure into **Fields**.",
  "Callout value: 22 pt, colour #0B3C5D, display units Auto. Category label: 10 pt, grey #5B6B7F.",
  "Visual border: on, colour #1F77B4, rounded corners 8 px. Title: off.",
  "Six cards per row, each 202 px wide with a 10 px gap.",
]));

const visTable = rows => table(["Visual", "Type", "Fields (field wells)", "Key settings"], rows, [2050, 1500, 3176, 2300]);

c.push(pb());
c.push(H1("7. Page 1 \u2013 Market Analysis"));
c.push(P("**Goal:** identify travel trends and popular destinations: where tourists go, when they travel, and why."));
c.push(...shot(path.join(SP, "hd", "page1.jpg"), "Figure 1 \u2013 Market Analysis page"));
c.push(H3("Slicers"));
c.push(P("DimDate[Year], Tourism[Country], Tourism[Purpose of Visit], Tourism[Hotel Rating]"));
c.push(H3("KPI cards"));
c.push(P("Total Tourists, Tourists YoY %, Tourist Nights, Avg Length of Stay, Avg Satisfaction, Airport Passenger Traffic"));
c.push(H3("Visuals"));
c.push(visTable([
  ["Tourist Arrivals Trend", "Area chart", "X-axis: DimDate[Year Month]\nY-axis: Total Tourists", "Sort ascending by Year Month; colour #1F77B4"],
  ["Tourists by Purpose of Visit", "Donut chart", "Legend: Purpose of Visit\nValues: Total Tourists", "Detail labels: Category, percent of total; legend off"],
  ["Seasonality \u2013 Tourists by Month", "Clustered column", "X-axis: DimDate[Month]\nY-axis: Total Tourists", "Sorted Jan\u2192Dec (via sort-by column); colour #2CA58D"],
  ["Tourists by Country", "Clustered bar", "Y-axis: Country\nX-axis: Total Tourists", "Sort descending; data labels on"],
  ["Most Popular Destinations (Cities)", "Clustered bar", "Y-axis: City\nX-axis: Total Tourists", "Sort descending; colour #F28E2B"],
  ["Destination Leaderboard", "Table", "City, Total Tourists, Destination Share %, Avg Satisfaction, Online Reviews", "Sort by Total Tourists descending"],
]));
c.push(H3("How to read it"));
c.push(B("Pick a **Year** to compare seasons. The **Tourists YoY %** card compares the selected (or latest) year with the year before."));
c.push(B("Click a slice in the **Purpose** donut to see which countries and cities attract that type of traveller. Click it again to clear."));
c.push(B("The **Destination Leaderboard** ranks cities by volume. Destination Share % shows each city's share of the current selection."));

c.push(pb());
c.push(H1("8. Page 2 \u2013 Revenue Forecasting"));
c.push(P("**Goal:** understand hotel occupancy and revenue patterns and project them into 2025."));
c.push(...shot(path.join(SP, "hd", "page2.jpg"), "Figure 2 \u2013 Revenue Forecasting page"));
c.push(H3("Slicers"));
c.push(P("Tourism[Country], Tourism[City], Tourism[Hotel Rating], Tourism[Purpose of Visit]. There is no Year slicer on this page because the charts show the full timeline including 2025."));
c.push(H3("KPI cards"));
c.push(P("Total Revenue, Revenue YoY %, Avg Occupancy %, Avg Room Price, RevPAR, 2025 Revenue Forecast"));
c.push(H3("Visuals"));
c.push(visTable([
  ["Monthly Revenue \u2013 Actual, Trend and 2025 Forecast", "Line chart", "X-axis: DimDate[Year Month]\nY-axis: Revenue Actual, Revenue 3M Moving Avg, Revenue Trend, Revenue Forecast", "Legend top; colours blue / light blue / grey / red. Format > Lines: set Revenue Trend to a dashed line"],
  ["Annual Revenue vs Occupancy", "Line and clustered column", "X-axis: DimDate[Year]\nColumn y-axis: Total Revenue\nLine y-axis: Avg Occupancy %", "Secondary axis on for the line"],
  ["Hotel Occupancy \u2013 Actual vs Forecast", "Line chart", "X-axis: DimDate[Year Month]\nY-axis: Occupancy Actual, Occupancy Forecast", "Forecast line dashed, red"],
  ["Occupancy Seasonality by Month", "Clustered column", "X-axis: DimDate[Month]\nY-axis: Avg Occupancy %", "Y-axis start about 60% to show the variation"],
  ["Revenue by Year and Quarter", "Matrix", "Rows: DimDate[Year]\nColumns: DimDate[Quarter]\nValues: Total Revenue", "Row and column subtotals on"],
]));
c.push(H3("How to read it"));
c.push(B("The **dark blue** line is actual monthly revenue and the **light blue** line smooths it over three months. The **grey dashed** line is the long-term trend, and the **red** line is the 2025 forecast with seasonality applied."));
c.push(B("Select a country, city or hotel class. The trend and forecast are recalculated for that segment only."));
c.push(B("**RevPAR** (revenue per available room) = room price \u00d7 occupancy. It is the standard hotel KPI that combines price and demand."));

c.push(pb());
c.push(H1("9. Page 3 \u2013 Hospitality Business Insights"));
c.push(P("**Goal:** analyse customer preferences and spending habits so hotels can target the most valuable guests."));
c.push(...shot(path.join(SP, "hd", "page3.jpg"), "Figure 3 \u2013 Hospitality Insights page"));
c.push(H3("Slicers"));
c.push(P("DimDate[Year], Tourism[Country], Tourism[Purpose of Visit], Tourism[Hotel Rating]"));
c.push(H3("KPI cards"));
c.push(P("Total Visitor Spend, Avg Spend per Tourist, Spend per Night, Avg Room Price, Avg Satisfaction, Online Reviews"));
c.push(H3("Visuals"));
c.push(visTable([
  ["Spend per Tourist and Length of Stay by Purpose", "Line and clustered column", "X-axis: Purpose of Visit\nColumn: Avg Spend per Tourist\nLine: Avg Length of Stay", "Sort by spend descending"],
  ["Room Price and Satisfaction by Hotel Rating", "Line and clustered column", "X-axis: Hotel Rating\nColumn: Avg Room Price\nLine: Avg Satisfaction", "Sort by Hotel Rating ascending"],
  ["Share of Visitor Spend by Hotel Rating", "Donut chart", "Legend: Hotel Rating\nValues: Total Visitor Spend", "Labels: percent of total; legend right"],
  ["Value for Money \u2013 Room Price vs Satisfaction", "Scatter chart", "Values: City\nX-axis: Avg Room Price\nY-axis: Avg Satisfaction\nSize: Total Tourists", "Category labels on"],
  ["Avg Spend per Tourist \u2013 Purpose x Hotel Rating", "Matrix", "Rows: Purpose of Visit\nColumns: Hotel Rating\nValues: Avg Spend per Tourist", "Optional: Cell elements > Background colour (gradient)"],
]));
c.push(H3("How to read it"));
c.push(B("Cities in the **top-left** of the scatter chart give high satisfaction at a lower room price (best value). Cities in the **bottom-right** are expensive with lower satisfaction."));
c.push(B("Use the matrix to find the highest-spending guest segments (darker cells), for example a purpose and star rating to target with packages."));

c.push(pb());
c.push(H1("10. Page 4 \u2013 Tourism Policy Evaluation"));
c.push(P("**Goal:** support government tourism strategy by showing economic impact, employment, sustainability and infrastructure."));
c.push(...shot(path.join(SP, "hd", "page4.jpg"), "Figure 4 \u2013 Tourism Policy page"));
c.push(H3("Slicers"));
c.push(P("DimDate[Year], Tourism[Country], Tourism[Purpose of Visit]"));
c.push(H3("KPI cards"));
c.push(P("Tourism Employment, Avg GDP Contribution %, Eco-Tourism Revenue, Eco-Tourism Share %, Carbon per Tourist (kg), Avg Infrastructure Quality"));
c.push(H3("Visuals"));
c.push(visTable([
  ["Tourism Contribution to GDP by Country", "Clustered bar", "Y-axis: Country\nX-axis: Avg GDP Contribution %", "Sort descending; colour #0B3C5D"],
  ["Sustainability \u2013 Carbon per Tourist vs Eco-Tourism Share", "Scatter chart", "Values: Country\nX-axis: Carbon per Tourist (kg)\nY-axis: Eco-Tourism Share %\nSize: Total Revenue", "Category labels on; colour #2CA58D"],
  ["Employment and Eco-Tourism Share by Year", "Line and clustered column", "X-axis: DimDate[Year]\nColumn: Tourism Employment\nLine: Eco-Tourism Share %", "Secondary axis on"],
  ["Country Policy Scorecard", "Table", "Country, Tourism Employment, Jobs per 1K Tourists, Avg GDP Contribution %, Eco-Tourism Share %, Carbon per Tourist (kg), Avg Infrastructure Quality, Avg Waste Management", "Sort by GDP % descending; optional data bars on GDP %"],
  ["Infrastructure and Waste Management by Country", "Clustered bar", "Y-axis: Country\nX-axis: Avg Infrastructure Quality, Avg Waste Management", "Sort by infrastructure descending"],
]));
c.push(H3("How to read it"));
c.push(B("In the sustainability scatter chart, the **top-left** corner (low carbon per tourist, high eco-tourism share) is the target position. Countries to the right have the largest environmental pressure per visitor."));
c.push(B("The scorecard puts economic and sustainability indicators side by side, so a country can be benchmarked against its peers."));

c.push(pb());
c.push(H1("11. Interactivity"));
c.push(B("**Cross-filtering:** clicking a bar, slice, point or table row filters every other visual on the page. Click it again, or click an empty area, to clear."));
c.push(B("**Edit interactions:** to change how one visual affects another, select it and go to **Format > Edit interactions**, then choose Filter, Highlight or None on each target visual. The defaults are used in this report."));
c.push(B("**Tooltips:** hover over any data point to see its exact values."));
c.push(B("**Multi-select:** hold **Ctrl** to choose several slicer values or several bars at once."));
c.push(B("**Sync slicers (optional):** View > Sync slicers keeps Year and Country selections the same across pages."));
c.push(B("**Focus mode:** hover over a visual and click the expand icon to see it full screen."));

c.push(H1("12. Validate the numbers"));
c.push(P("After refreshing, with no slicer selections, the report should show these totals (calculated independently from the CSV):"));
c.push(table(["Measure", "Expected value"], [
  ["Total Tourists", "62,631,942"],
  ["Tourist Nights", "541,682,347"],
  ["Avg Length of Stay", "8.6 nights"],
  ["Avg Satisfaction", "7.44"],
  ["Total Revenue", "$174,868,958"],
  ["Avg Occupancy %", "64.8%"],
  ["Avg Room Price", "$273.98"],
  ["RevPAR", "$176.88"],
  ["2025 Revenue Forecast", "$35.55M"],
  ["Avg Spend per Tourist", "$2,792.01"],
  ["Tourism Employment", "13,537,576"],
  ["Avg GDP Contribution %", "10.5%"],
  ["Eco-Tourism Share %", "16.9%"],
  ["Carbon per Tourist (kg)", "297.1"],
], [4513, 4513]));

c.push(pb());
c.push(H1("13. Key findings by use case"));
c.push(H2("13.1 Market Analysis"));
c.push(B("62.6 million tourists over 2020\u20132024. Volumes peaked in **2023 (14.5M, +12.0% YoY)** and then fell 17.8% in 2024."));
c.push(B("Top countries: **China (4.27M), Italy (4.03M), South Africa (4.01M), Germany (3.97M), Egypt (3.80M)**. Top cities: **Johannesburg, Luxor, Beijing, Manchester, Rio de Janeiro**."));
c.push(B("Purpose mix is fairly even. **Family Visit (16.9%)** and **Educational (16.2%)** lead, while Cultural (11.9%) is the smallest."));
c.push(B("Seasonality: **June** is the busiest month (6.6M) and **November** the quietest (3.4M)."));
c.push(H2("13.2 Revenue Forecasting"));
c.push(B("Total revenue was **$174.9M**. 2023 was the strongest year ($44.0M); 2024 fell 27.5% to $31.9M."));
c.push(B("Average occupancy is **64.8%**. It peaks in **November (68.6%)** and March\u2013April (68.0%), and is lowest in September (60.4%)."));
c.push(B("The long-term trend is almost flat, so the seasonal-trend model projects about **$35.6M** of revenue for 2025."));
c.push(H2("13.3 Hospitality Business Insights"));
c.push(B("Average spend is **$2,792 per tourist** (about $323 per night)."));
c.push(B("**Business** travellers spend the most per trip ($3,002) and **Family Visit** the least ($2,623). **Educational** and **Medical** visitors stay longest (about 9 nights)."));
c.push(B("Higher star ratings do not mean higher prices in this data. **4-star hotels** have the lowest average room price ($250) and the **highest satisfaction (7.79)**, which makes them the best value. Unrated hotels score lowest (7.11)."));
c.push(H2("13.4 Tourism Policy Evaluation"));
c.push(B("Tourism supports **13.5 million jobs** and contributes **10.5% of GDP** on average. Greece (12.5%), Germany (12.2%) and the UAE (12.1%) depend on tourism the most."));
c.push(B("Eco-tourism is **16.9%** of tourism revenue. China, the UK, Thailand and Mexico lead (about 19.5\u201319.8%), while Germany is lowest (11.8%)."));
c.push(B("Carbon per tourist averages **297 kg**. Mexico (335 kg) and South Africa (324 kg) are highest and France (249 kg) is lowest. These are candidates for green-transport and waste programmes."));
c.push(B("Canada, China and Japan have the best transport infrastructure scores (about 6.0\u20136.2/10). Germany and Thailand score lowest (about 4.7)."));

c.push(H1("14. Publish and share"));
c.push(...steps([
  "Save the report as **.pbix** (File > Save as).",
  "Click **Home > Publish** and choose a workspace in the Power BI Service.",
  "In the Service, open the semantic model settings and add a **gateway** or upload the CSV to OneDrive/SharePoint if you need scheduled refresh.",
  "Share the report or package it as an **App** for stakeholders. Use **Export > PDF** or **PowerPoint** for offline copies.",
]));
c.push(note("The browser preview (Report_Preview/Tourism_Report_Preview.html) and the walkthrough video show the same pages and interactions. You can use them to present the report to people who don't have Power BI."));

const doc = new Document({
  creator: "Tourism Analytics",
  title: "Tourism & Hospitality Power BI Report Guide",
  styles: {
    default: { document: { run: { font: FONT, size: 21 } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true, run: { font: FONT, size: 32, bold: true, color: NAVY }, paragraph: { spacing: { before: 240, after: 160 }, keepNext: true, outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true, run: { font: FONT, size: 26, bold: true, color: "1F77B4" }, paragraph: { spacing: { before: 220, after: 100 }, keepNext: true, outlineLevel: 1 } },
      { id: "Heading3", name: "Heading 3", basedOn: "Normal", next: "Normal", quickFormat: true, run: { font: FONT, size: 22, bold: true, color: "1B2A3A" }, paragraph: { spacing: { before: 160, after: 80 }, keepNext: true, outlineLevel: 2 } },
    ],
  },
  numbering: { config: numberingConfigs },
  sections: [{
    properties: { page: { margin: { top: 1300, bottom: 1300, left: 1440, right: 1440 } } },
    headers: { default: new Header({ children: [new Paragraph({ alignment: AlignmentType.RIGHT, children: [new TextRun({ text: "Tourism & Hospitality \u2013 Power BI Report Guide", size: 16, color: "8A97A8" })] })] }) },
    footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ children: ["Page ", PageNumber.CURRENT], size: 16, color: "8A97A8" })] })] }) },
    children: c,
  }],
});
Packer.toBuffer(doc).then(b => { fs.writeFileSync(OUT, b); console.log("written", b.length); });
