import pandas as pd
from matplotlib import pyplot as plt
from datetime import date, timedelta
import openai
import io
import base64
import markdown2
from playwright.sync_api import sync_playwright
from dotenv import load_dotenv
import os


# Load the variables from the .env file
load_dotenv()

# Initialize the client with your API key
client = openai.OpenAI(
    api_key=os.getenv("API_KEY")
)

# Helper function to add 'st', 'nd', 'rd', 'th' to the day
def get_ordinal(n):
    if 11 <= n <= 13:
        return f"{n}th"
    return f"{n}{ {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th') }"


def ytd_this_year(data_file_name, month_day, title_date):
    # 1. Load the data
    df = pd.read_excel(data_file_name)

    # ADD COLUMNS TO DATA
    # 1. Convert date columns to datetime objects
    df['Booking date'] = pd.to_datetime(df['Booking date'])
    df['Arrival'] = pd.to_datetime(df['Arrival'])

    # 2. Add Booking date features
    df['Booking date year'] = df['Booking date'].dt.year
    df['Booking date month number'] = df['Booking date'].dt.month
    df['Booking date week number'] = df['Booking date'].dt.isocalendar().week

    # 3. Add Arrival features
    df['Arrival year'] = df['Arrival'].dt.year
    df['Arrival month number'] = df['Arrival'].dt.month
    df['Arrival week number'] = df['Arrival'].dt.isocalendar().week

    # FILTER DATA FOR PLOT
    # 1. Ensure date columns are in datetime format
    df['Booking date'] = pd.to_datetime(df['Booking date'])

    # 2. Define the years and their respective 'before May 4th' filters
    target_years = [2024, 2025, 2026]
    filtered_frames = []

    for year in target_years:
        # Create the snapshot date for the specific year
        snapshot_date = f"{year}-{month_day}"

        # Filter: Arrivals in that year AND Bookings taken before May 4th
        subset = df[(df['Arrival year'] == year) & (df['Booking date'] < snapshot_date)]
        filtered_frames.append(subset)

    # Combine the filtered data back into one dataframe
    combined_df = pd.concat(filtered_frames)

    # 3. Group by year and month number to get the monthly totals
    grouped = combined_df.groupby(['Arrival year', 'Arrival month number'])['Gross rent'].sum().reset_index()

    # 4. Pivot the data to prepare for the grouped bar chart
    pivot_df = grouped.pivot(index='Arrival month number', columns='Arrival year', values='Gross rent')

    # 5. Ensure all 12 months are represented
    pivot_df = pivot_df.reindex(range(1, 13))

    # 6. Create the bar plot
    ax = pivot_df.plot(kind='bar', figsize=(12, 7), width=0.8)

    # 7. Add styling and labels
    plt.title(f'Gross Rent Comparison (Bookings taken on or before {title_date} of each year)')
    plt.xlabel('Arrival Month Number')
    plt.ylabel('Total Gross Rent')
    plt.xticks(rotation=0)
    plt.legend(title='Arrival Year')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    ax.yaxis.set_major_formatter('£{x:,.0f}')

    # 8. Save chart to a memory buffer (BytesIO)
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)

    # 9. Encode the image to Base64
    base64_image = base64.b64encode(buf.read()).decode('utf-8')

    # 10. Send to OpenAI GPT-4o
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Role: Act as a Senior Revenue Manager and Marketing Consultant specializing in the UK self-catering holiday market. Context: I am providing a chart showing  'Like-for-Like ' bookings performance at May 10th for the current year (2026) versus the previous two years (2024, 2025). We operate in the self-catering accommodation sector with an average lead time of 12 weeks.  Task: Please perform a deep-dive analysis of this visual data and provide the following:  Trend Identification: Compare the YOY (Year-over-Year) and 2-year growth/decline. Identify specific  'pivot points ' where the current year deviates from historical norms.  Lead Time Gap Analysis: Given our 12-week lead time, analyze the current  'booking window ' visibility. If we are in May, tell me what this data suggests about our August and September occupancy.  Revenue vs. Occupancy: Based on the slopes of the lines, does it look like we are achieving  'growth through volume ' or  'growth through rate '?  Strategic Recommendations:  Short-term (Last Minute): Strategies for filling unbooked gaps in the next 0–4 weeks.  Medium-term (The 12-Week Sweet Spot): Specific marketing angles for the  'Prime Summer ' or  'Early Autumn ' window based on current momentum.  Long-term: How to leverage the 2026 data to secure 2027 early-bird bookings.  Market-Specific Tactics: Suggest 3 specific  'value-add ' (not discount) strategies to maximize RevPAR for the remaining 2026 holiday periods (e.g., targeting adult groups, pets, or digital nomads).  Constraint: Be critical. If the data looks like we are underperforming in a specific month, highlight it as a  'red flag ' and provide a recovery tactic. NOTE: use the month number and be accurate"},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{base64_image}"
                        }
                    },
                ],
            }
        ],
        max_tokens=15000,
    )

    ai_analysis_string = response.choices[0].message.content
    print("AI Analysis:", ai_analysis_string)
    plt.show()  # Optional: show the chart on your screen too

    analysis_html = markdown2.markdown(ai_analysis_string)

    # 3. CREATE THE HTML TEMPLATE
    html_template = f"""
        <html>
        <head>
            <style>
                @page {{ size: A4; margin: 20mm; }}
                body {{ font-family: sans-serif; color: #333; }}
                h1 {{ color: #1d3557; border-bottom: 2px solid #1d3557; }}
                .chart-box {{ text-align: center; margin: 20px 0; background: #f4f4f4; padding: 10px; }}
                .analysis {{ line-height: 1.6; font-size: 11pt; }}
            </style>
        </head>
        <body>
            <h1>Strategic Market Analysis 2026</h1>
            <div class="chart-box">
                <img src="data:image/png;base64,{base64_image}" style="width: 100%;">
            </div>
            <div class="analysis">
                {analysis_html}
            </div>
        </body>
        </html>
        """

    # 4. CONVERT TO PDF
    save_as_pdf(html_template)


def save_as_pdf(html_content):
    with sync_playwright() as p:
        # Launch a "hidden" browser
        browser = p.chromium.launch()
        page = browser.new_page()

        # Set the HTML content we built
        page.set_content(html_content)

        # Save as a professional PDF
        page.pdf(
            path=r"C:\Users\Marc\Downloads\Market_Analysis_Report.pdf",
            format="A4",
            print_background=True,  # Ensures your colors and charts show up
            margin={"top": "20mm", "bottom": "20mm", "left": "20mm", "right": "20mm"}
        )
        browser.close()
    print("PDF successfully generated using Playwright!")


if __name__ == '__main__':
    # month_day_input = input('Enter month and day (mm-dd) for the Monday date:')
    # date_4_title = input('Enter date to show on report (e.g. May 3rd):')
    today = date.today()
    monday = today - timedelta(days=today.weekday())
    sunday = today - timedelta(days=today.weekday() + 1)
    month_day_input = monday.strftime('%m-%d')
    date_4_title = f"{sunday.strftime('%B')} {get_ordinal(sunday.day)}"
    # print(f"Variable value: {month_day_input}")
    # print(f"Report title:   {date_4_title}")
    ytd_this_year(r'C:\Users\Marc\PycharmProjects\PeakVenuesAccounts\files\SuperControlDataV2.xlsx', month_day_input, date_4_title)
    # chat_with_gpt()
