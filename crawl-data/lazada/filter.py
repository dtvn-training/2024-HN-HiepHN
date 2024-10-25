import pandas as pd

df = pd.read_csv('./output/lazada_url.csv')
df_cleaned = df.drop_duplicates()
df_cleaned.to_csv('./output/lazada_url_filtered.csv', index=False)
