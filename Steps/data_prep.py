import pandas as pd

def prepare_data(df, cols_to_convert) -> None:

    for col in cols_to_convert:
        df[col] = pd.to_numeric(df[col], errors='coerce')  # 'coerce' will turn invalid parsing into NaN