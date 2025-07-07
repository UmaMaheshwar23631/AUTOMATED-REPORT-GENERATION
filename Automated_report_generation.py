import pandas as pd
import matplotlib.pyplot as plt
from fpdf import FPDF
from datetime import datetime
import os

# ============ CONFIGURATION ============
INPUT_FILE = "employees.csv"       # Replace with your CSV file. By default , I have used an employee based csv file
MAX_TABLE_ROWS = 30                # Show top 30 rows in PDF table
MAX_CATEGORIES = 5                 # For bar charts (top N categories)
LOGO_PATH = "logo.png"             # Optional logo

# ============ HELPER FUNCTIONS ============
def is_numeric(series):
    return pd.api.types.is_numeric_dtype(series)

def is_categorical(series):
    return pd.api.types.is_object_dtype(series) or pd.api.types.is_categorical_dtype(series)

def generate_chart(series, title, filename):
    plt.figure(figsize=(6, 4))
    series.value_counts().head(MAX_CATEGORIES).plot(kind='bar', color='skyblue')
    plt.title(title)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(filename)
    plt.close()

def generate_unique_pdf_name(base="smart_report"):
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    return f"{base}_{timestamp}.pdf"

# ============ PDF CLASS ============
class PDF(FPDF):
    def header(self):
        if os.path.exists(LOGO_PATH):
            self.image(LOGO_PATH, x=10, y=8, w=25)
        self.set_font("Arial", 'B', 16)
        self.cell(0, 10, "Auto-Generated Data Report", ln=True, align="C")
        self.set_font("Arial", '', 10)
        self.cell(0, 10, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True, align="C")
        self.ln(10)

    def section_title(self, title):
        self.set_fill_color(230, 230, 250)
        self.set_font("Arial", 'B', 13)
        self.cell(0, 10, title, ln=True, fill=True)
        self.ln(2)

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 10)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")

# ============ MAIN SCRIPT ============
df = pd.read_csv(INPUT_FILE)

pdf = PDF()
pdf.add_page()
pdf.set_font("Arial", size=12)

# Metadata
pdf.section_title("File Overview")
pdf.cell(0, 10, f"File: {os.path.basename(INPUT_FILE)}", ln=True)
pdf.cell(0, 10, f"Rows: {len(df)}, Columns: {len(df.columns)}", ln=True)
pdf.ln(5)

# Categorize Columns
numeric_cols = [col for col in df.columns if is_numeric(df[col])]
categorical_cols = [col for col in df.columns if is_categorical(df[col])]

# Numeric Summary
if numeric_cols:
    pdf.section_title("Numeric Column Summary")
    for col in numeric_cols:
        mean = df[col].mean()
        min_ = df[col].min()
        max_ = df[col].max()
        pdf.cell(0, 10, f"{col} - Mean: {mean:.2f}, Min: {min_}, Max: {max_}", ln=True)

# Categorical Summary
if categorical_cols:
    pdf.section_title("Categorical Column Summary")
    for col in categorical_cols:
        counts = df[col].value_counts().head(MAX_CATEGORIES)
        pdf.set_font("Arial", 'B', 11)
        pdf.cell(0, 10, f"{col} (Top {MAX_CATEGORIES} categories):", ln=True)
        pdf.set_font("Arial", size=11)
        for val, count in counts.items():
            pdf.cell(0, 10, f"  - {val}: {count}", ln=True)
        pdf.ln(2)

# Charts for top useful categories
pdf.section_title("Visual Charts")
for col in categorical_cols:
    if df[col].nunique() <= 25:  # Ignore columns with too many unique values
        chart_file = f"{col}_chart.png"
        generate_chart(df[col], f"{col} Distribution", chart_file)
        if os.path.exists(chart_file):
            pdf.image(chart_file, w=160)
            pdf.ln(5)

# Data Table
pdf.section_title("Sample Data Table (Top 30 Rows)")
pdf.set_font("Arial", 'B', 11)
col_width = pdf.w / len(df.columns) - 2

# Table Headers
for col in df.columns:
    pdf.cell(col_width, 10, str(col)[:15], 1)
pdf.ln()

# Table Rows
pdf.set_font("Arial", size=10)
for _, row in df.head(MAX_TABLE_ROWS).iterrows():
    for val in row:
        pdf.cell(col_width, 10, str(val)[:15], 1)
    pdf.ln()

# Save with timestamp
output_pdf = generate_unique_pdf_name()
pdf.output(output_pdf)

print(f"✅ Report Generated: {output_pdf}")
