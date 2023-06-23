import pandas as pd
import matplotlib.pyplot as plt

from tsai.basics import *
from tsai.inference import load_learner
from train_model import transform_data, fcst_history, fcst_horizon, freq, datetime_col, x_vars, y_vars


# Creating dates to have for inference
fcst_date = "2023-05-31 21:00"
dates = pd.date_range(start=None, end=fcst_date, periods=fcst_history, freq=freq)

# loading data to use for inference
df = pd.read_csv('historical_20080801_full.csv', index_col = 0)
df_initial = transform_data(df,'Margaux')
new_df = df_initial[df_initial['date'].isin(dates)]
new_df.reset_index(drop = True, inplace = True)
save_new_df = new_df

# loading of model
name = 'Margaux_v2b'
learn = load_learner(name+'.pt')


new_df = learn.transform(new_df)

# inference
new_X, _ = prepare_forecasting_data(new_df, fcst_history=fcst_history, fcst_horizon=0, x_vars=x_vars, y_vars=None)
new_scaled_preds, *_ = learn.get_X_preds(new_X)

new_scaled_preds = to_np(new_scaled_preds).swapaxes(1,2).reshape(-1, len(y_vars))
dates = pd.date_range(start=fcst_date, periods=fcst_horizon + 1, freq= freq)[1:]
preds_df = pd.DataFrame(dates, columns=[datetime_col])
preds_df.loc[:, y_vars] = new_scaled_preds
preds_df = learn.inverse_transform(preds_df)

df_total_pred= pd.concat([save_new_df, preds_df], ignore_index = True)



# Create of chart
date_format = '%Y-%m-%d %H:%M'
date_obj = datetime.strptime(fcst_date, date_format)


fig, axs = plt.subplots(nrows=3, ncols=3, figsize=(30, 15))
plt.subplots_adjust(hspace=0.5)
fig.suptitle("Forecasting", fontsize=18, y=0.95)
colors = ['C{}'.format(k) for k in range(16)]
for i, (column, ax) in enumerate(zip(new_df.columns[1:], axs.ravel())):
    # filter df for ticker and plot on specified axes
    ax.plot(df_total_pred['date'], df_total_pred[column], linestyle='-', color = colors[i],linewidth=1)
    ax.axvline(x=date_obj, linewidth=1, color='black')
    ax.set_title(column, fontsize = 16)
plt.show()


