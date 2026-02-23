import pandas as pd

df = pd.read_excel("aws_test-focus-00001.snappy_transformed.xls")

print("Columns in AWS file:")
print(df.columns.tolist())