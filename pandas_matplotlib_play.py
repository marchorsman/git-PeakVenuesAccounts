import pandas as pd
from matplotlib import pyplot as plt

x = [1, 2, 3]
y = [1, 4, 9]
z = [10, 5, 0]
plt.plot(x, y)
plt.plot(x, z)
plt.title("Test Plot")
plt.xlabel("x")
plt.ylabel("y and z")
plt.legend(["This is y", "This is z"])
# plt.show() **********************************
plt.show()

sample_data = pd.read_excel(r"C:\Users\Marc\PycharmProjects\PeakVenuesAccounts\files\your_output_file.xlsx")

"""
plt.plot(sample_data["Booking no"], sample_data["Gross rent"])
plt.show()

this_year_arrival = sample_data[sample_data["Arrival year"] == 2026]
# print(this_year_arrival)
plt.plot(this_year_arrival["Booking no"], this_year_arrival["Gross rent"])
plt.show()


# 1. Load the data (works for both .csv and .xlsx)
# For Excel: df = pd.read_excel('your_file.xlsx')
# this has been set up on line 15

# 2. Group by Arrival year and sum the Gross rent
yearly_rent = sample_data.groupby('Arrival year')['Gross rent'].sum().reset_index()

# 3. Sort by year to ensure correct plotting order
yearly_rent = yearly_rent.sort_values('Arrival year')

# 4. Create the plot
plt.figure(figsize=(10, 6))
plt.bar(yearly_rent['Arrival year'].astype(str), yearly_rent['Gross rent'], color='skyblue')

# 5. Add labels and title
plt.xlabel('Arrival Year')
plt.ylabel('Total Gross Rent')
plt.title('Total Gross Rent by Arrival Year')
plt.grid(axis='y', linestyle='--', alpha=0.7)

# 6. Show the plot
plt.show()
# plt.savefig('messing_about.pdf')


# SALES FOR MONTH BY MONTH
# 1. Load the data
# df = pd.read_excel('your_file.xlsx')
# This has been set up on line 15

# 2. Select the year you want to view
selected_year = 2026

# 3. Filter for that year and group by month number
# We sum the Gross rent per month first
monthly_totals = sample_data[sample_data['Arrival year'] == selected_year].groupby('Arrival month number')['Gross rent'].sum().reset_index()

# 4. Sort by month and calculate the accumulated (cumulative) sum
monthly_totals = monthly_totals.sort_values('Arrival month number')
monthly_totals['Accumulated Gross Rent'] = monthly_totals['Gross rent'].cumsum()

# 5. Create the plot
plt.figure(figsize=(10, 6))
plt.plot(monthly_totals['Arrival month number'], monthly_totals['Accumulated Gross Rent'],
         marker='o', linestyle='-', color='green', linewidth=2)

# Fill the area under the line for better visibility
plt.fill_between(monthly_totals['Arrival month number'], monthly_totals['Accumulated Gross Rent'], color='green', alpha=0.1)

# 6. Formatting the chart
plt.xlabel('Month Number')
plt.ylabel('Accumulated Gross Rent')
plt.title(f'Accumulated Gross Rent for Year {selected_year}')
plt.xticks(range(1, 13))  # Ensure x-axis shows months 1-12
plt.grid(True, linestyle=':', alpha=0.6)

plt.show()
"""

# BUILD OUT FOR A NUMBER OF YEARS ON THE SAME PLOT
# 3. Filter for that year and group by month number
# We sum the Gross rent per month first
monthly_totals_2024 = sample_data[sample_data['Arrival year'] == 2024].groupby('Arrival month number')['Gross rent'].sum().reset_index()
monthly_totals_2025 = sample_data[sample_data['Arrival year'] == 2025].groupby('Arrival month number')['Gross rent'].sum().reset_index()
monthly_totals_2026 = sample_data[sample_data['Arrival year'] == 2026].groupby('Arrival month number')['Gross rent'].sum().reset_index()


target_years = [2024, 2025, 2026]
filtered_data = sample_data[sample_data['Arrival year'].isin(target_years)]
combined_test = filtered_data.groupby(['Arrival year', 'Arrival month number'])['Gross rent'].sum().reset_index()
print(combined_test)
print(monthly_totals_2026)
vvv = combined_test.to_json()
print(vvv)

# *******  PIVOT TABLE FOR AI  ***********
df = pd.read_excel(r"C:\Users\Marc\PycharmProjects\PeakVenuesAccounts\files\your_output_file.xlsx")
# 1. Filter for the specific years
target_years = [2024, 2025, 2026]
df_filtered = df[df['Arrival year'].isin(target_years)]

# 2. Group and Sum
monthly_sales = df_filtered.groupby(['Arrival year', 'Arrival month number'])['Gross rent'].sum().reset_index()
yearly_sales = df_filtered.groupby(['Arrival year'])['Gross rent'].sum().reset_index()
print(yearly_sales)
print(yearly_sales.iloc[1, 1])
print(yearly_sales.loc[yearly_sales['Arrival year'] == 2025, 'Gross rent'].values[0])


# 3. Pivot the data (This is the "magic" step for AI readability)
# index='month' (rows are months 1-12)
# columns='year' (columns are 2024, 2025, 2026)
pivot_table = monthly_sales.pivot(index='Arrival month number', columns='Arrival year', values='Gross rent')

# 4. Fill any missing months with 0 (so the AI doesn't get confused by 'NaN')
pivot_table = pivot_table.fillna(0)

# 5. Create the string for your OpenAI prompt
raw_data_string = pivot_table.to_string()

print("--- DATA PREPARED FOR AI ---")
print(raw_data_string)







# 4. Sort by month and calculate the accumulated (cumulative) sum
monthly_totals_2024 = monthly_totals_2024.sort_values('Arrival month number')
monthly_totals_2024['Accumulated Gross Rent'] = monthly_totals_2024['Gross rent'].cumsum()

monthly_totals_2025 = monthly_totals_2025.sort_values('Arrival month number')
monthly_totals_2025['Accumulated Gross Rent'] = monthly_totals_2025['Gross rent'].cumsum()

monthly_totals_2026 = monthly_totals_2026.sort_values('Arrival month number')
monthly_totals_2026['Accumulated Gross Rent'] = monthly_totals_2026['Gross rent'].cumsum()

# 5. Create the plot
plt.figure(figsize=(10, 6))
plt.plot(monthly_totals_2024['Arrival month number'], monthly_totals_2024['Accumulated Gross Rent'],
         marker='o', linestyle='-', color='blue', linewidth=2)
plt.plot(monthly_totals_2025['Arrival month number'], monthly_totals_2025['Accumulated Gross Rent'],
         marker='o', linestyle='-', color='green', linewidth=2)
plt.plot(monthly_totals_2026['Arrival month number'], monthly_totals_2026['Accumulated Gross Rent'],
         marker='o', linestyle='-', color='red', linewidth=2)

# 6. Formatting the chart
plt.xlabel('Month Number')
plt.ylabel('Accumulated Gross Rent')
plt.title(f'Accumulated Gross Rent for Year')
# plt.legend(['2024', '2025', '2026'])
plt.legend(['2024', '2025', '2026'], title='Arrival Year')
plt.xticks(range(1, 13))  # Ensure x-axis shows months 1-12
plt.grid(True, linestyle=':', alpha=0.6)

# plt.show() ***************************************
