import pandas as pd
from matplotlib import pyplot as plt
from datetime import date, timedelta


# Helper function to add 'st', 'nd', 'rd', 'th' to the day
def get_ordinal(n):
    if 11 <= n <= 13:
        return f"{n}th"
    return f"{n}{ {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th') }"


def ytd_plot(data_file_name, month_day, title_date, target_years, shift_value, pdf_path, bar_colours):
    # FETCH DATA FRAME FOR ANALYSIS
    # 1. Load the data
    df_raw = pd.read_excel(data_file_name)
    # 2. Remove lines outside of analysis scope
    df = df_raw[~df_raw['Property'].str.contains('Rock Mill', case=False, na=False)]
    # df.to_excel('debug.xlsx', index=False)   # Debug

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
    # 1. Define the years and their respective 'before May 4th' filters
    #    The Years are now defined from arguments passed to the function
    filtered_frames = []

    for year in target_years:
        # Create the snapshot date for the specific year
        snapshot_date = f"{year - shift_value}-{month_day}"

        # Filter: Arrivals in that year AND Bookings taken before May 4th
        subset = df[(df['Arrival year'] == year) & (df['Booking date'] < snapshot_date)]
        filtered_frames.append(subset)

    # Combine the filtered data back into one dataframe
    combined_df = pd.concat(filtered_frames)

    # 2. Group by year and month number to get the monthly totals
    grouped = combined_df.groupby(['Arrival year', 'Arrival month number'])['Gross rent'].sum().reset_index()
    # print(grouped) # for debug
    # 3. Pivot the data to prepare for the grouped bar chart
    pivot_df = grouped.pivot(index='Arrival month number', columns='Arrival year', values='Gross rent')

    # 4. Ensure all 12 months are represented
    pivot_df = pivot_df.reindex(range(1, 13))

    # 5. Create the bar plot
    ax = pivot_df.plot(kind='bar', figsize=(12, 7), width=0.8, color = bar_colours)

    # 6. Add styling and labels
    plt.title(f'Gross Rent Comparison (Bookings taken on or before {title_date} of each year)')
    plt.xlabel('Arrival Month Number')
    plt.ylabel('Total Gross Rent')
    plt.xticks(rotation=0)
    # Fetch yearly totals for legend
    yearly_sales = grouped.groupby(['Arrival year'])['Gross rent'].sum().reset_index()
    # Calculate growth
    sales_1 = yearly_sales.iloc[0, 1]
    sales_2 = yearly_sales.iloc[1, 1]
    sales_3 = yearly_sales.iloc[2, 1]
    growth_1 = ((sales_3 - sales_1) / sales_1) * 100
    growth_2 = ((sales_3 - sales_2) / sales_2) * 100
    # Build legend
    plt.legend(
        labels=[f'{target_years[0]} £{sales_1:,.0f}',
                f'{target_years[1]} £{sales_2:,.0f}',
                f'{target_years[2]} £{sales_3:,.0f} ({growth_1:0.1f}%, {growth_2:0.1f}%)'],
        title='Arrival Year'
    )
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    ax.yaxis.set_major_formatter('£{x:,.0f}')

    plt.show()
    #plt.savefig(pdf_path)
    #print(f'{pdf_path} successfully produced')


if __name__ == '__main__':

    # Calculate dates from today to give the Monday date of this week and Sunday's from last week
    today = date.today()
    monday = today - timedelta(days=today.weekday())
    sunday = today - timedelta(days=today.weekday() + 1)
    month_day_input = monday.strftime('%m-%d')
    date_4_title = f"{sunday.strftime('%B')} {get_ordinal(sunday.day)}"
    # Run report please note that the shift value is the number of years ahead
    # i.e. bookings for 2027 taken by 10.05.2026 would have a shift value of 1 as looking one year into the future
    ytd_plot(r'C:\Users\Marc\Downloads\SuperControlDataV2.xlsx',
                  month_day_input,
                  date_4_title,
                  [2024, 2025, 2026],
             0,
             r'C:\Users\Marc\Downloads\YTD.pdf',
             ['#3f55d1', '#5280e3', '#14ccc9'])

    ytd_plot(r'C:\Users\Marc\Downloads\SuperControlDataV2.xlsx',
             month_day_input,
             date_4_title,
             [2025, 2026, 2027],
             1,
             r'C:\Users\Marc\Downloads\YTD_year_in_advance.pdf',
             ['#f24666', '#ed8980', '#ffceab'])
