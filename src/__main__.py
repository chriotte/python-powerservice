import powerservice.trading as t
from powerservice.trading import save_csv, summarise_data, get_trades, check_if_valid_date
from powerservice import *
import pandas as pd

ts = pd.Timestamp.now()
date = ts.strftime('%d/%m/%Y')
#path = f"/csv/{ts.strftime('%Y')}/{ts.strftime('%m')}/{ts.strftime('%d')}"
trades = get_trades(date = date)

for i in range(len(trades)):
    df = pd.DataFrame(trades[i])

    file_name = f'PowerPosition_{ts.strftime("%Y%m%d")}_{ts.strftime("%H%M")}.csv'
    profile_file_name = f'PowerPosition_{ts.strftime("%Y%m%d")}_{ts.strftime("%H%M")}_data_profiling.csv'
    quality_file_name = f'PowerPosition_{ts.strftime("%Y%m%d")}_{ts.strftime("%H%M")}_data_quality.csv'
    #df = trading.trading.get_trades(date = date)


    save_csv(summarise_data(df), f'{file_name}')
    save_csv(summarise_data(df).describe(), f'{profile_file_name}', index=True)
    save_csv(data_quality_check(df), f'{quality_file_name}', index=True)