import pandas as pd

df = pd.read_csv('./output/tiki_url.csv')
df_cleaned = df.drop_duplicates()
df_cleaned.to_csv('./output/tiki_url_filtered.csv', index=False)
