import sklearn
import pandas as pd
import matplotlib.pyplot as plt

from tsai.basics import *
from sklearn.metrics import mean_squared_error, mean_absolute_error

df = pd.read_csv('historical_20080801_full.csv', index_col = 0)

def transform_data(df, city):
    df.insert(0,'date', df.observation_time +' ' +df['time'])
    df = df[df.city == city]
    df_tmp = df.sort_values(by=['date'])  # sort line to have chronoligic order
    df_tmp[['date']] = df_tmp[['date']].apply(pd.to_datetime)
    df_tmp.reset_index(drop = True, inplace = True)                     # reset of index to able to use split function
    df_tmp.drop(['wind_dir','time','city','observation_time','visibility', 'weather_code'], inplace = True, axis = 1)   # remove categorical raw
    return df_tmp

df = transform_data(df, 'Margaux')

datetime_col = "date"
freq = '3H'
columns = df.columns[1:]
method = 'ffill'
value = 0

# pipeline
preproc_pipe = sklearn.pipeline.Pipeline([
    ('shrinker', TSShrinkDataFrame()), # shrink dataframe memory usage
    ('drop_duplicates', TSDropDuplicates(datetime_col=datetime_col)), # drop duplicate rows (if any)
    ('add_mts', TSAddMissingTimestamps(datetime_col=datetime_col, freq=freq)), # add missing timestamps (if any)
    ('fill_missing', TSFillMissing(columns=columns, method=method, value=value)), # fill missing data (1st ffill. 2nd value=0)
    ], 
    verbose=True)

fcst_history = 365 # # steps in the past
fcst_horizon = 7  # # steps in the future
valid_size   = 0.2  # int or float indicating the size of the training set
test_size    = 0.1  # int or float indicating the size of the test set

splits = get_forecasting_splits(df, fcst_history=fcst_history, fcst_horizon=fcst_horizon, datetime_col=datetime_col,
                                valid_size=valid_size, test_size=test_size, show_plot = False)

train_split = splits[0]

# pipeline
exp_pipe = sklearn.pipeline.Pipeline([
    ('scaler', TSStandardScaler(columns=columns)), # standardize data using train_split
    ], 
    verbose=True)

x_vars = df.columns[1:]
y_vars = df.columns[1:]
X, y = prepare_forecasting_data(df, fcst_history=fcst_history, fcst_horizon=fcst_horizon, x_vars=x_vars, y_vars=y_vars)

arch_config = dict(
    n_layers=3,  # number of encoder layers
    n_heads=4,  # number of heads
    d_model=16,  # dimension of model
    d_ff=128,  # dimension of fully connected network
    attn_dropout=0.0, # dropout applied to the attention weights
    dropout=0.3,  # dropout applied to all linear layers in the encoder except q,k&v projections
    patch_len=24,  # length of the patch applied to the time series to create patches
    stride=2,  # stride used when creating patches
    padding_patch=True,  # padding_patch
)

learn = TSForecaster(X, y, splits=splits, batch_size=16, pipelines=[preproc_pipe, exp_pipe],
                     arch="PatchTST", arch_config=arch_config, metrics=[mse, mae])

n_epochs = 50
lr_max = learn.lr_find().valley
learn.fit_one_cycle(n_epochs, lr_max=lr_max)

name = 'Margaux_v2a'
learn.export('Margaux_v2a.pt')

y_test_preds, *_ = learn.get_X_preds(X[splits[2]])
y_test_preds = to_np(y_test_preds)

y_test = y[splits[2]]

def get_var_data(y):
    dim_var = (int(y.shape[0]/7)+1)
    var0 = np.ones(dim_var)
    var1 = np.ones(dim_var)
    var2 = np.ones(dim_var)
    var3 = np.ones(dim_var)
    var4 = np.ones(dim_var)
    var5 = np.ones(dim_var)
    var6 = np.ones(dim_var)
    var7 = np.ones(dim_var)
    var8 = np.ones(dim_var)
    var9 = np.ones(dim_var)
    j=0
    
    while j < (y.shape[0]/7):
        y_part = y[j]
        y_part = y_part.flatten()
        var0[j:j+7] = y_part[0:7]
        var1[j:j+7] = y_part[7:14]
        var2[j:j+7] = y_part[14:21]
        var3[j:j+7] = y_part[21:28]
        var4[j:j+7] = y_part[28:35]
        var5[j:j+7] = y_part[35:42]
        var6[j:j+7] = y_part[42:49]
        var7[j:j+7] = y_part[49:56]
        var8[j:j+7] = y_part[56:63]
        j += 7

    return var0,var1,var2,var3,var4,var5,var6,var7,var8

var0,var1,var2,var3,var4,var5,var6,var7,var8 = get_var_data(y_test)
var0_pred,var1_pred,var2_pred,var3_pred,var4_pred,var5_pred,var6_pred,var7_pred,var8_pred = get_var_data(y_test_preds)

fig = plt.figure(figsize= (12,9))
ax1 = fig.add_subplot(3,3,1)
ax2 = fig.add_subplot(3,3,2)
ax3 = fig.add_subplot(3,3,3)
ax4 = fig.add_subplot(3,3,4)
ax5 = fig.add_subplot(3,3,5)
ax6 = fig.add_subplot(3,3,6)
ax7 = fig.add_subplot(3,3,7)
ax8 = fig.add_subplot(3,3,8)
ax9 = fig.add_subplot(3,3,9)
l1 = ax1.plot(var0)
l1 = ax1.plot(var0_pred)
ax1.set_title(df.columns[1], fontsize = 10)
l2 = ax2.plot(var1)
l2 = ax2.plot(var1_pred)
ax2.set_title(df.columns[2], fontsize = 10)
l3 = ax3.plot(var2)
l3 = ax3.plot(var2_pred)
ax3.set_title(df.columns[3], fontsize = 10)
l4 = ax4.plot(var3)
l4 = ax4.plot(var3_pred)
ax4.set_title(df.columns[4], fontsize = 10)
l5 = ax5.plot(var4)
l5 = ax5.plot(var4_pred)
ax5.set_title(df.columns[5], fontsize = 10)
l6 = ax6.plot(var5)
l6 = ax6.plot(var5_pred)
ax6.set_title(df.columns[6], fontsize = 10)
l7 = ax7.plot(var6)
l7 = ax7.plot(var6_pred)
ax7.set_title(df.columns[7], fontsize = 10)
l8 = ax8.plot(var7)
l8 = ax8.plot(var7_pred)
ax8.set_title(df.columns[8], fontsize = 10)
l9 = ax9.plot(var8)
l9 = ax9.plot(var8_pred)
ax9.set_title(df.columns[9], fontsize = 10)
plt.show()

results_df = pd.DataFrame(columns=["mse", "mae"])
results_df.loc[df.columns[1], "mse"] = mean_squared_error(var0, var0_pred)
results_df.loc[df.columns[1], "mae"] = mean_absolute_error(var0, var0_pred)
results_df.loc[df.columns[2], "mse"] = mean_squared_error(var1, var1_pred)
results_df.loc[df.columns[2], "mae"] = mean_absolute_error(var1, var1_pred)
results_df.loc[df.columns[3], "mse"] = mean_squared_error(var2, var2_pred)
results_df.loc[df.columns[3], "mae"] = mean_absolute_error(var2, var2_pred)
results_df.loc[df.columns[4], "mse"] = mean_squared_error(var3, var3_pred)
results_df.loc[df.columns[4], "mae"] = mean_absolute_error(var3, var3_pred)
results_df.loc[df.columns[5], "mse"] = mean_squared_error(var4, var4_pred)
results_df.loc[df.columns[5], "mae"] = mean_absolute_error(var4, var4_pred)
results_df.loc[df.columns[6], "mse"] = mean_squared_error(var5, var5_pred)
results_df.loc[df.columns[6], "mae"] = mean_absolute_error(var5, var5_pred)
results_df.loc[df.columns[7], "mse"] = mean_squared_error(var6, var6_pred)
results_df.loc[df.columns[7], "mae"] = mean_absolute_error(var6, var6_pred)
results_df.loc[df.columns[8], "mse"] = mean_squared_error(var7, var7_pred)
results_df.loc[df.columns[8], "mae"] = mean_absolute_error(var7, var7_pred)
results_df.loc[df.columns[9], "mse"] = mean_squared_error(var8, var8_pred)
results_df.loc[df.columns[9], "mae"] = mean_absolute_error(var8, var8_pred)
#print('result on Test samples') 
#display(results_df)