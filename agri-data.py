import pandas as pd

df = pd.read_csv("C:/Users/hp/Downloads/Kenya_data.csv")
# Structures of the data
print("--- Data Info ---")
print(df.info())

# statistical summary
print("n\ --- Statistical summary ---")
print(df.describe())

# Filter for a specific crop (Item) and specific measurement (Element)
# We want 'Production' in tonnes, not just the 'Area harvested'
maize_production = df[(df['Item'] == 'Maize (corn)') & (df['Element'] == 'Production')]

# Sort by Year so we see the timeline correctly
maize_production = maize_production.sort_values('Year')

# Print the last 5 years to see recent trends
print("\n--- Recent Maize Production in Kenya ---")
print(maize_production[['Year', 'Value', 'Unit']].tail())

import plotly.express as px

# Filter the data as before
crops_to_compare = ['Maize (corn)', 'Wheat']
comparison_df = df[(df['Item'].isin(crops_to_compare)) & (df['Element'] == 'Production')]
comparison_df = comparison_df.sort_values('Year')

# Normalizing the data: Dividing every year's value by the value in 1961
# We group by 'Item' so Maize is divided by its 1961 start, and Wheat by its own
comparison_df['Normalized_Growth'] = comparison_df.groupby('Item')['Value'].transform(lambda x: x / x.iloc[0])

# Create the interactive chart using the new 'Normalized_Growth' column
fig = px.line(comparison_df, 
              x='Year', 
              y='Normalized_Growth', 
              color='Item', 
              title='Growth Rate Comparison: Maize vs Wheat (Baseline 1961 = 1.0)',
              labels={'Normalized_Growth': 'Growth Multiplier (1961 = 1.0)'},
              markers=True)

# Add a horizontal line at 1.0 to show the baseline clearly
fig.add_hline(y=1.0, line_dash="dash", line_color="black")

fig.show()

# Expand the filter to include a Cash Crop
analysis_items = ['Maize (corn)', 'Coffee, green']
df_final = df[(df['Item'].isin(analysis_items)) & (df['Element'] == 'Production')]

# Normalizing again to compare growth percentages
df_final = df_final.sort_values('Year')
df_final['Index_1961'] = df_final.groupby('Item')['Value'].transform(lambda x: x / x.iloc[0])

# specialized comparison chart
fig = px.line(df_final, x='Year', y='Index_1961', color='Item',
              title='Food Security vs. Cash Income: Normalized Growth (1961-2021)',
              labels={'Index_1961': 'Growth Multiplier (1961=1.0)'})
fig.show()
# Calculate the Year-over-Year percentage change for Maize
maize_only = df[(df['Item'] == 'Maize (corn)') & (df['Element'] == 'Production')].sort_values('Year')
maize_only['Pct_Change'] = maize_only['Value'].pct_change() * 100

# Filter for "Crisis Years" (where drop is greater than 10%)
crisis_years = maize_only[maize_only['Pct_Change'] <= -10]

print("\n--- Identified Crisis Years for Maize (Drops > 10%) ---")
print(crisis_years[['Year', 'Value', 'Pct_Change']])

# Ensure we have the pct_change and previous year values
maize_only['Prev_Value'] = maize_only['Value'].shift(1)
maize_only['Loss_Amount'] = maize_only['Prev_Value'] - maize_only['Value']

# Filter for Crisis Years (Drops > 10%)
crisis_data = maize_only[maize_only['Pct_Change'] <= -10].copy()

# Calculate the sum of all losses during these years
total_tonnage_lost = crisis_data['Loss_Amount'].sum()

print("\n--- Summary of Agricultural Shocks (Maize) ---")
print(f"Number of Crisis Years identified: {len(crisis_data)}")
print(f"Total Production Lost during Crisis Years: {total_tonnage_lost:,.0f} Tonnes")

#Identify the single worst year
worst_year = crisis_data.loc[crisis_data['Pct_Change'].idxmin()]
print(f"Worst Shock Year: {worst_year['Year']} ({worst_year['Pct_Change']:.1f}% drop)")
