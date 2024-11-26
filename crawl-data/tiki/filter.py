import pandas as pd
import os

current_dir = os.path.dirname(__file__)

target_dir=os.path.normpath(os.path.join(current_dir,"./output/tiki_url.csv"))

output_dir=os.path.normpath(os.path.join(current_dir,"./output/tiki_url_filtered.csv"))


df = pd.read_csv(target_dir)
df_cleaned = df.drop_duplicates()
df_cleaned.to_csv(output_dir, index=False)
