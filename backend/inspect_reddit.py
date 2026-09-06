import pandas as pd

df = pd.read_csv(r'C:\Users\Kanak\Desktop\moodcompiler\backend\data\reddit\Reddit_depression_dataset.csv')
print('Shape:', df.shape)
print()
print('Columns:', list(df.columns))
print()
for c in df.columns:
    print(f'  {c}: {df[c].nunique()} unique, dtype={df[c].dtype}')
print()
print('First 3 rows:')
print(df.head(3).to_string())
