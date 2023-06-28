import sklearn
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import numpy as np

from tsai.basics import *
from sklearn.metrics import mean_squared_error, mean_absolute_error

import mlflow.fastai
import mlflow


def transform_data(df, city):
    '''Traitements des données issus de la base pour toujours avoir le même format de traitement'''
    df.insert(0,'date', df.observation_time +' ' +df['time'])
    df = df[df.city == city]
    df_tmp = df.sort_values(by=['date'])  # sort line to have chronoligic order
    df_tmp[['date']] = df_tmp[['date']].apply(pd.to_datetime)
    df_tmp.reset_index(drop = True, inplace = True)                     # reset of index to able to use split function
    df_tmp.drop(['wind_dir','time','city','observation_time','visibility', 'weather_code'], inplace = True, axis = 1)   # remove categorical raw
    return df_tmp

def get_var_data(y):
    dim_var = (int(y.shape[0]/fcst_horizon)+1)
    var0 = np.ones(dim_var)
    var1 = np.ones(dim_var)
    var2 = np.ones(dim_var)
    var3 = np.ones(dim_var)
    var4 = np.ones(dim_var)
    var5 = np.ones(dim_var)
    var6 = np.ones(dim_var)
    var7 = np.ones(dim_var)
    var8 = np.ones(dim_var)
    j=0

    while j < (dim_var-fcst_horizon):
        y_part = y[j]
        y_part = y_part.flatten()
        var0[j:j+fcst_horizon] = y_part[0:fcst_horizon]
        var1[j:j+fcst_horizon] = y_part[fcst_horizon:fcst_horizon*2]
        var2[j:j+fcst_horizon] = y_part[fcst_horizon*2:fcst_horizon*3]
        var3[j:j+fcst_horizon] = y_part[fcst_horizon*3:fcst_horizon*4]
        var4[j:j+fcst_horizon] = y_part[fcst_horizon*4:fcst_horizon*5]
        var5[j:j+fcst_horizon] = y_part[fcst_horizon*5:fcst_horizon*6]
        var6[j:j+fcst_horizon] = y_part[fcst_horizon*6:fcst_horizon*7]
        var7[j:j+fcst_horizon] = y_part[fcst_horizon*7:fcst_horizon*8]
        var8[j:j+fcst_horizon] = y_part[fcst_horizon*8:fcst_horizon*9]
        j += fcst_horizon

    return var0,var1,var2,var3,var4,var5,var6,var7,var8

def get_hyperparameters(n_layers =3,n_heads=16,d_model=16,d_ff=128,attn_dropout=0.0,dropout=0.3,patch_len=24,stride=24,padding_patch=True,
                        batch_size=16,fcst_history=400,fcst_horizon=8):
    arch_config = {'n_layers':n_layers,  # number of encoder layers
                    'n_heads':n_heads,  # number of heads
                    'd_model':d_model,  # dimension of model
                    'd_ff':d_ff,  # dimension of fully connected network
                    'attn_dropout':attn_dropout, # dropout applied to the attention weights
                    'dropout':dropout,  # dropout applied to all linear layers in the encoder except q,k&v projections
                    'patch_len':patch_len,  # length of the patch applied to the time series to create patches
                    'stride':stride,  # stride used when creating patches
                    'padding_patch':padding_patch}  # padding_patch
    
    return arch_config, batch_size,fcst_history,fcst_horizon

def get_results(var0,var1,var2,var3,var4,var5,var6,var7,var8,
                var0_pred,var1_pred,var2_pred,var3_pred,var4_pred,var5_pred,var6_pred,var7_pred,var8_pred):
    results_df = pd.DataFrame(columns=["mse", "mae"])
    results_df.loc[df.columns[1], "mse"] = round(mean_squared_error(var0, var0_pred),2)
    results_df.loc[df.columns[1], "mae"] = round(mean_absolute_error(var0, var0_pred),2)
    results_df.loc[df.columns[2], "mse"] = round(mean_squared_error(var1, var1_pred),2)
    results_df.loc[df.columns[2], "mae"] = round(mean_absolute_error(var1, var1_pred),2)
    results_df.loc[df.columns[3], "mse"] = round(mean_squared_error(var2, var2_pred),2)
    results_df.loc[df.columns[3], "mae"] = round(mean_absolute_error(var2, var2_pred),2)
    results_df.loc[df.columns[4], "mse"] = round(mean_squared_error(var3, var3_pred),2)
    results_df.loc[df.columns[4], "mae"] = round(mean_absolute_error(var3, var3_pred),2)
    results_df.loc[df.columns[5], "mse"] = round(mean_squared_error(var4, var4_pred),2)
    results_df.loc[df.columns[5], "mae"] = round(mean_absolute_error(var4, var4_pred),2)
    results_df.loc[df.columns[6], "mse"] = round(mean_squared_error(var5, var5_pred),2)
    results_df.loc[df.columns[6], "mae"] = round(mean_absolute_error(var5, var5_pred),2)
    results_df.loc[df.columns[7], "mse"] = round(mean_squared_error(var6, var6_pred),2)
    results_df.loc[df.columns[7], "mae"] = round(mean_absolute_error(var6, var6_pred),2)
    results_df.loc[df.columns[8], "mse"] = round(mean_squared_error(var7, var7_pred),2)
    results_df.loc[df.columns[8], "mae"] = round(mean_absolute_error(var7, var7_pred),2)
    results_df.loc[df.columns[9], "mse"] = round(mean_squared_error(var8, var8_pred),2)
    results_df.loc[df.columns[9], "mae"] = round(mean_absolute_error(var8, var8_pred),2)

    return results_df


def get_chart(results_df):
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
    fig.savefig("predictions.png")
    plt.close(fig)
    

def get_all_metrics(df):
    all_metrics = {}
    for name in df.index:
        all_metrics[name+'_mse'] = float(df.loc[name,'mse'])
        all_metrics[name+'_mae'] = float(df.loc[name,'mae'])
    return all_metrics

# import des données
df = pd.read_csv('historical_20080801_full.csv', index_col = 0)
df = transform_data(df, 'Margaux')

# Variables pour le modèle.
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

valid_size   = 0.2  # int or float indicating the size of the training set
test_size    = 0.1  # int or float indicating the size of the test set

# pipeline
exp_pipe = sklearn.pipeline.Pipeline([
    ('scaler', TSStandardScaler(columns=columns)), # standardize data using train_split
    ], 
    verbose=True)

x_vars = df.columns[1:]
y_vars = df.columns[1:]

init_time = datetime.now()

n_epochs = 50

with mlflow.start_run():
    with mlflow.start_run(description = 'iteration 0',nested=True):

        print('\niteration 0\n')       
    # Initialize our model and trainer
        arch_config, batch_size, fcst_history, fcst_horizon = get_hyperparameters()

        splits = get_forecasting_splits(df, fcst_history=fcst_history, fcst_horizon=fcst_horizon, datetime_col=datetime_col,
                                valid_size=valid_size, test_size=test_size, show_plot = False)
        train_split = splits[0]
        X, y = prepare_forecasting_data(df, fcst_history=fcst_history, fcst_horizon=fcst_horizon, x_vars=x_vars, y_vars=y_vars)

        learn = TSForecaster(X, y, splits=splits, batch_size=batch_size, path='model_tsai', pipelines=[preproc_pipe, exp_pipe],
                     arch="PatchTST", arch_config=arch_config, metrics=[mse, mae])

        lr_max = learn.lr_find().valley
        learn.fit_one_cycle(n_epochs, lr_max=lr_max)

        y_test_preds, *_ = learn.get_X_preds(X[splits[2]])
        y_test_preds = to_np(y_test_preds)
        y_test = y[splits[2]]

        var0,var1,var2,var3,var4,var5,var6,var7,var8 = get_var_data(y_test)
        var0_pred,var1_pred,var2_pred,var3_pred,var4_pred,var5_pred,var6_pred,var7_pred,var8_pred = get_var_data(y_test_preds)

        results_df = get_results(var0,var1,var2,var3,var4,var5,var6,var7,var8,
                                 var0_pred,var1_pred,var2_pred,var3_pred,var4_pred,var5_pred,var6_pred,var7_pred,var8_pred)
        all_metrics = get_all_metrics(results_df)

        get_chart(results_df)

# fetch the auto logged parameters and metrics
        mlflow.log_param("architecture", arch_config)
        mlflow.log_param("batch size", batch_size)
        mlflow.log_param("epochs number", n_epochs)
        mlflow.log_param("fcst_history", fcst_history)
        mlflow.log_param("fcst_horizon", fcst_horizon)
        mlflow.log_param("learning rate", lr_max)

        mlflow.log_metrics(all_metrics)

        mlflow.log_artifact("predictions.png")
        results_df.reset_index(inplace=True)
        results_df.to_csv('scores.csv',index=True)
        mlflow.log_artifact('scores.csv')
        mlflow.fastai.log_model(learn, "model")
        matplotlib.pyplot.close()

    with mlflow.start_run(description = 'iteration 1',nested=True):        
    # Initialize our model and trainer
        print('\niteration 1\n')
        arch_config, batch_size, fcst_history, fcst_horizon = get_hyperparameters(n_heads=8)

        splits = get_forecasting_splits(df, fcst_history=fcst_history, fcst_horizon=fcst_horizon, datetime_col=datetime_col,
                                valid_size=valid_size, test_size=test_size, show_plot = False)
        train_split = splits[0]
        X, y = prepare_forecasting_data(df, fcst_history=fcst_history, fcst_horizon=fcst_horizon, x_vars=x_vars, y_vars=y_vars)

        learn = TSForecaster(X, y, splits=splits, batch_size=batch_size, path='model_tsai', pipelines=[preproc_pipe, exp_pipe],
                     arch="PatchTST", arch_config=arch_config, metrics=[mse, mae])

        lr_max = learn.lr_find().valley
        learn.fit_one_cycle(n_epochs, lr_max=lr_max)

        y_test_preds, *_ = learn.get_X_preds(X[splits[2]])
        y_test_preds = to_np(y_test_preds)
        y_test = y[splits[2]]

        var0,var1,var2,var3,var4,var5,var6,var7,var8 = get_var_data(y_test)
        var0_pred,var1_pred,var2_pred,var3_pred,var4_pred,var5_pred,var6_pred,var7_pred,var8_pred = get_var_data(y_test_preds)

        results_df = get_results(var0,var1,var2,var3,var4,var5,var6,var7,var8,
                                 var0_pred,var1_pred,var2_pred,var3_pred,var4_pred,var5_pred,var6_pred,var7_pred,var8_pred)
        all_metrics = get_all_metrics(results_df)

        get_chart(results_df)

# fetch the auto logged parameters and metrics
        mlflow.log_param("architecture", arch_config)
        mlflow.log_param("batch size", batch_size)
        mlflow.log_param("epochs number", n_epochs)
        mlflow.log_param("fcst_history", fcst_history)
        mlflow.log_param("fcst_horizon", fcst_horizon)
        mlflow.log_param("learning rate", lr_max)

        mlflow.log_metrics(all_metrics)

        mlflow.log_artifact("predictions.png")
        results_df.reset_index(inplace=True)
        results_df.to_csv('scores.csv',index=True)
        mlflow.log_artifact('scores.csv')
        mlflow.fastai.log_model(learn, "model")
        matplotlib.pyplot.close()

    with mlflow.start_run(description = 'iteration 2',nested=True):        
    # Initialize our model and trainer
        print('\niteration 2\n')  
        arch_config, batch_size, fcst_history, fcst_horizon = get_hyperparameters(n_heads=16)

        splits = get_forecasting_splits(df, fcst_history=fcst_history, fcst_horizon=fcst_horizon, datetime_col=datetime_col,
                                valid_size=valid_size, test_size=test_size, show_plot = False)
        train_split = splits[0]
        X, y = prepare_forecasting_data(df, fcst_history=fcst_history, fcst_horizon=fcst_horizon, x_vars=x_vars, y_vars=y_vars)

        learn = TSForecaster(X, y, splits=splits, batch_size=batch_size, path='model_tsai', pipelines=[preproc_pipe, exp_pipe],
                     arch="PatchTST", arch_config=arch_config, metrics=[mse, mae])

        lr_max = learn.lr_find().valley
        learn.fit_one_cycle(n_epochs, lr_max=lr_max)

        y_test_preds, *_ = learn.get_X_preds(X[splits[2]])
        y_test_preds = to_np(y_test_preds)
        y_test = y[splits[2]]

        var0,var1,var2,var3,var4,var5,var6,var7,var8 = get_var_data(y_test)
        var0_pred,var1_pred,var2_pred,var3_pred,var4_pred,var5_pred,var6_pred,var7_pred,var8_pred = get_var_data(y_test_preds)

        results_df = get_results(var0,var1,var2,var3,var4,var5,var6,var7,var8,
                                 var0_pred,var1_pred,var2_pred,var3_pred,var4_pred,var5_pred,var6_pred,var7_pred,var8_pred)
        all_metrics = get_all_metrics(results_df)

        get_chart(results_df)

# fetch the auto logged parameters and metrics
        mlflow.log_param("architecture", arch_config)
        mlflow.log_param("batch size", batch_size)
        mlflow.log_param("epochs number", n_epochs)
        mlflow.log_param("fcst_history", fcst_history)
        mlflow.log_param("fcst_horizon", fcst_horizon)
        mlflow.log_param("learning rate", lr_max)

        mlflow.log_metrics(all_metrics)

        mlflow.log_artifact("predictions.png")
        results_df.reset_index(inplace=True)
        results_df.to_csv('scores.csv',index=True)
        mlflow.log_artifact('scores.csv')
        mlflow.fastai.log_model(learn, "model")
        matplotlib.pyplot.close()

    with mlflow.start_run(description = 'iteration 3',nested=True):
    # Initialize our model and trainer
        print('\niteration 3\n')  
        arch_config, batch_size, fcst_history, fcst_horizon = get_hyperparameters(n_heads=16, d_model=64)

        splits = get_forecasting_splits(df, fcst_history=fcst_history, fcst_horizon=fcst_horizon, datetime_col=datetime_col,
                                valid_size=valid_size, test_size=test_size, show_plot = False)
        train_split = splits[0]
        X, y = prepare_forecasting_data(df, fcst_history=fcst_history, fcst_horizon=fcst_horizon, x_vars=x_vars, y_vars=y_vars)

        learn = TSForecaster(X, y, splits=splits, batch_size=batch_size, path='model_tsai', pipelines=[preproc_pipe, exp_pipe],
                     arch="PatchTST", arch_config=arch_config, metrics=[mse, mae])

        lr_max = learn.lr_find().valley
        learn.fit_one_cycle(n_epochs, lr_max=lr_max)

        y_test_preds, *_ = learn.get_X_preds(X[splits[2]])
        y_test_preds = to_np(y_test_preds)
        y_test = y[splits[2]]

        var0,var1,var2,var3,var4,var5,var6,var7,var8 = get_var_data(y_test)
        var0_pred,var1_pred,var2_pred,var3_pred,var4_pred,var5_pred,var6_pred,var7_pred,var8_pred = get_var_data(y_test_preds)

        results_df = get_results(var0,var1,var2,var3,var4,var5,var6,var7,var8,
                                 var0_pred,var1_pred,var2_pred,var3_pred,var4_pred,var5_pred,var6_pred,var7_pred,var8_pred)
        all_metrics = get_all_metrics(results_df)

        get_chart(results_df)

# fetch the auto logged parameters and metrics
        mlflow.log_param("architecture", arch_config)
        mlflow.log_param("batch size", batch_size)
        mlflow.log_param("epochs number", n_epochs)
        mlflow.log_param("fcst_history", fcst_history)
        mlflow.log_param("fcst_horizon", fcst_horizon)
        mlflow.log_param("learning rate", lr_max)

        mlflow.log_metrics(all_metrics)

        mlflow.log_artifact("predictions.png")
        results_df.reset_index(inplace=True)
        results_df.to_csv('scores.csv',index=True)
        mlflow.log_artifact('scores.csv')
        mlflow.fastai.log_model(learn, "model")
        matplotlib.pyplot.close()

    with mlflow.start_run(description = 'iteration 4',nested=True):        
    # Initialize our model and trainer
        print('\niteration 4\n')  
        arch_config, batch_size, fcst_history, fcst_horizon = get_hyperparameters(n_heads=16, d_model=128, d_ff=256)

        splits = get_forecasting_splits(df, fcst_history=fcst_history, fcst_horizon=fcst_horizon, datetime_col=datetime_col,
                                valid_size=valid_size, test_size=test_size, show_plot = False)
        train_split = splits[0]
        X, y = prepare_forecasting_data(df, fcst_history=fcst_history, fcst_horizon=fcst_horizon, x_vars=x_vars, y_vars=y_vars)

        learn = TSForecaster(X, y, splits=splits, batch_size=batch_size, path='model_tsai', pipelines=[preproc_pipe, exp_pipe],
                     arch="PatchTST", arch_config=arch_config, metrics=[mse, mae])

        lr_max = learn.lr_find().valley
        learn.fit_one_cycle(n_epochs, lr_max=lr_max)

        y_test_preds, *_ = learn.get_X_preds(X[splits[2]])
        y_test_preds = to_np(y_test_preds)
        y_test = y[splits[2]]

        var0,var1,var2,var3,var4,var5,var6,var7,var8 = get_var_data(y_test)
        var0_pred,var1_pred,var2_pred,var3_pred,var4_pred,var5_pred,var6_pred,var7_pred,var8_pred = get_var_data(y_test_preds)

        results_df = get_results(var0,var1,var2,var3,var4,var5,var6,var7,var8,
                                 var0_pred,var1_pred,var2_pred,var3_pred,var4_pred,var5_pred,var6_pred,var7_pred,var8_pred)
        all_metrics = get_all_metrics(results_df)

        get_chart(results_df)

# fetch the auto logged parameters and metrics
        mlflow.log_param("architecture", arch_config)
        mlflow.log_param("batch size", batch_size)
        mlflow.log_param("epochs number", n_epochs)
        mlflow.log_param("fcst_history", fcst_history)
        mlflow.log_param("fcst_horizon", fcst_horizon)
        mlflow.log_param("learning rate", lr_max)

        mlflow.log_metrics(all_metrics)

        mlflow.log_artifact("predictions.png")
        results_df.reset_index(inplace=True)
        results_df.to_csv('scores.csv',index=True)
        mlflow.log_artifact('scores.csv')
        mlflow.fastai.log_model(learn, "model")
        matplotlib.pyplot.close()

    with mlflow.start_run(description = 'iteration 5',nested=True):        
    # Initialize our model and trainer
        print('\niteration 5\n')  
        arch_config, batch_size, fcst_history, fcst_horizon = get_hyperparameters(n_heads=16,d_model=128, d_ff=256,attn_dropout= 0.1)

        splits = get_forecasting_splits(df, fcst_history=fcst_history, fcst_horizon=fcst_horizon, datetime_col=datetime_col,
                                valid_size=valid_size, test_size=test_size, show_plot = False)
        train_split = splits[0]
        X, y = prepare_forecasting_data(df, fcst_history=fcst_history, fcst_horizon=fcst_horizon, x_vars=x_vars, y_vars=y_vars)

        learn = TSForecaster(X, y, splits=splits, batch_size=batch_size, path='model_tsai', pipelines=[preproc_pipe, exp_pipe],
                     arch="PatchTST", arch_config=arch_config, metrics=[mse, mae])

        lr_max = learn.lr_find().valley
        learn.fit_one_cycle(n_epochs, lr_max=lr_max)

        y_test_preds, *_ = learn.get_X_preds(X[splits[2]])
        y_test_preds = to_np(y_test_preds)
        y_test = y[splits[2]]

        var0,var1,var2,var3,var4,var5,var6,var7,var8 = get_var_data(y_test)
        var0_pred,var1_pred,var2_pred,var3_pred,var4_pred,var5_pred,var6_pred,var7_pred,var8_pred = get_var_data(y_test_preds)

        results_df = get_results(var0,var1,var2,var3,var4,var5,var6,var7,var8,
                                 var0_pred,var1_pred,var2_pred,var3_pred,var4_pred,var5_pred,var6_pred,var7_pred,var8_pred)
        all_metrics = get_all_metrics(results_df)

        get_chart(results_df)

# fetch the auto logged parameters and metrics
        mlflow.log_param("architecture", arch_config)
        mlflow.log_param("batch size", batch_size)
        mlflow.log_param("epochs number", n_epochs)
        mlflow.log_param("fcst_history", fcst_history)
        mlflow.log_param("fcst_horizon", fcst_horizon)
        mlflow.log_param("learning rate", lr_max)

        mlflow.log_metrics(all_metrics)

        mlflow.log_artifact("predictions.png")
        results_df.reset_index(inplace=True)
        results_df.to_csv('scores.csv',index=True)
        mlflow.log_artifact('scores.csv')
        mlflow.fastai.log_model(learn, "model")
        matplotlib.pyplot.close()

    with mlflow.start_run(description = 'iteration 6',nested=True):        
    # Initialize our model and trainer
        print('\niteration 6\n')  
        arch_config, batch_size, fcst_history, fcst_horizon = get_hyperparameters(n_heads=16,d_model=128, d_ff=256,attn_dropout = 0.3)

        splits = get_forecasting_splits(df, fcst_history=fcst_history, fcst_horizon=fcst_horizon, datetime_col=datetime_col,
                                valid_size=valid_size, test_size=test_size, show_plot = False)
        train_split = splits[0]
        X, y = prepare_forecasting_data(df, fcst_history=fcst_history, fcst_horizon=fcst_horizon, x_vars=x_vars, y_vars=y_vars)

        learn = TSForecaster(X, y, splits=splits, batch_size=batch_size, path='model_tsai', pipelines=[preproc_pipe, exp_pipe],
                     arch="PatchTST", arch_config=arch_config, metrics=[mse, mae])

        lr_max = learn.lr_find().valley
        learn.fit_one_cycle(n_epochs, lr_max=lr_max)

        y_test_preds, *_ = learn.get_X_preds(X[splits[2]])
        y_test_preds = to_np(y_test_preds)
        y_test = y[splits[2]]

        var0,var1,var2,var3,var4,var5,var6,var7,var8 = get_var_data(y_test)
        var0_pred,var1_pred,var2_pred,var3_pred,var4_pred,var5_pred,var6_pred,var7_pred,var8_pred = get_var_data(y_test_preds)

        results_df = get_results(var0,var1,var2,var3,var4,var5,var6,var7,var8,
                                 var0_pred,var1_pred,var2_pred,var3_pred,var4_pred,var5_pred,var6_pred,var7_pred,var8_pred)
        all_metrics = get_all_metrics(results_df)

        get_chart(results_df)

# fetch the auto logged parameters and metrics
        mlflow.log_param("architecture", arch_config)
        mlflow.log_param("batch size", batch_size)
        mlflow.log_param("epochs number", n_epochs)
        mlflow.log_param("fcst_history", fcst_history)
        mlflow.log_param("fcst_horizon", fcst_horizon)
        mlflow.log_param("learning rate", lr_max)

        mlflow.log_metrics(all_metrics)

        mlflow.log_artifact("predictions.png")
        results_df.reset_index(inplace=True)
        results_df.to_csv('scores.csv',index=True)
        mlflow.log_artifact('scores.csv')
        mlflow.fastai.log_model(learn, "model")
        matplotlib.pyplot.close()

    with mlflow.start_run(description = 'iteration 7',nested=True):        
    # Initialize our model and trainer
        print('\niteration 7\n')  
        arch_config, batch_size, fcst_history, fcst_horizon = get_hyperparameters(n_heads=16,d_model=128, d_ff=256,attn_dropout = 0.5)

        splits = get_forecasting_splits(df, fcst_history=fcst_history, fcst_horizon=fcst_horizon, datetime_col=datetime_col,
                                valid_size=valid_size, test_size=test_size, show_plot = False)
        train_split = splits[0]
        X, y = prepare_forecasting_data(df, fcst_history=fcst_history, fcst_horizon=fcst_horizon, x_vars=x_vars, y_vars=y_vars)

        learn = TSForecaster(X, y, splits=splits, batch_size=batch_size, path='model_tsai', pipelines=[preproc_pipe, exp_pipe],
                     arch="PatchTST", arch_config=arch_config, metrics=[mse, mae])

        lr_max = learn.lr_find().valley
        learn.fit_one_cycle(n_epochs, lr_max=lr_max)

        y_test_preds, *_ = learn.get_X_preds(X[splits[2]])
        y_test_preds = to_np(y_test_preds)
        y_test = y[splits[2]]

        var0,var1,var2,var3,var4,var5,var6,var7,var8 = get_var_data(y_test)
        var0_pred,var1_pred,var2_pred,var3_pred,var4_pred,var5_pred,var6_pred,var7_pred,var8_pred = get_var_data(y_test_preds)

        results_df = get_results(var0,var1,var2,var3,var4,var5,var6,var7,var8,
                                 var0_pred,var1_pred,var2_pred,var3_pred,var4_pred,var5_pred,var6_pred,var7_pred,var8_pred)
        all_metrics = get_all_metrics(results_df)

        get_chart(results_df)

# fetch the auto logged parameters and metrics
        mlflow.log_param("architecture", arch_config)
        mlflow.log_param("batch size", batch_size)
        mlflow.log_param("epochs number", n_epochs)
        mlflow.log_param("fcst_history", fcst_history)
        mlflow.log_param("fcst_horizon", fcst_horizon)
        mlflow.log_param("learning rate", lr_max)

        mlflow.log_metrics(all_metrics)

        mlflow.log_artifact("predictions.png")
        results_df.reset_index(inplace=True)
        results_df.to_csv('scores.csv',index=True)
        mlflow.log_artifact('scores.csv')
        mlflow.fastai.log_model(learn, "model")
        matplotlib.pyplot.close()

    with mlflow.start_run(description = 'iteration 8',nested=True):        
    # Initialize our model and trainer
        print('\niteration 8\n')  
        arch_config, batch_size, fcst_history, fcst_horizon = get_hyperparameters(n_heads=16,d_model=128, d_ff=256,fcst_horizon=24)

        splits = get_forecasting_splits(df, fcst_history=fcst_history, fcst_horizon=fcst_horizon, datetime_col=datetime_col,
                                valid_size=valid_size, test_size=test_size, show_plot = False)
        train_split = splits[0]
        X, y = prepare_forecasting_data(df, fcst_history=fcst_history, fcst_horizon=fcst_horizon, x_vars=x_vars, y_vars=y_vars)

        learn = TSForecaster(X, y, splits=splits, batch_size=batch_size, path='model_tsai', pipelines=[preproc_pipe, exp_pipe],
                     arch="PatchTST", arch_config=arch_config, metrics=[mse, mae])

        lr_max = learn.lr_find().valley
        learn.fit_one_cycle(n_epochs, lr_max=lr_max)

        y_test_preds, *_ = learn.get_X_preds(X[splits[2]])
        y_test_preds = to_np(y_test_preds)
        y_test = y[splits[2]]

        var0,var1,var2,var3,var4,var5,var6,var7,var8 = get_var_data(y_test)
        var0_pred,var1_pred,var2_pred,var3_pred,var4_pred,var5_pred,var6_pred,var7_pred,var8_pred = get_var_data(y_test_preds)

        results_df = get_results(var0,var1,var2,var3,var4,var5,var6,var7,var8,
                                 var0_pred,var1_pred,var2_pred,var3_pred,var4_pred,var5_pred,var6_pred,var7_pred,var8_pred)
        all_metrics = get_all_metrics(results_df)

        get_chart(results_df)

# fetch the auto logged parameters and metrics
        mlflow.log_param("architecture", arch_config)
        mlflow.log_param("batch size", batch_size)
        mlflow.log_param("epochs number", n_epochs)
        mlflow.log_param("fcst_history", fcst_history)
        mlflow.log_param("fcst_horizon", fcst_horizon)
        mlflow.log_param("learning rate", lr_max)

        mlflow.log_metrics(all_metrics)

        mlflow.log_artifact("predictions.png")
        results_df.reset_index(inplace=True)
        results_df.to_csv('scores.csv',index=True)
        mlflow.log_artifact('scores.csv')
        mlflow.fastai.log_model(learn, "model")
        matplotlib.pyplot.close()

    with mlflow.start_run(description = 'iteration 9',nested=True):
    # Initialize our model and trainer
        print('\niteration 9\n')  
        arch_config, batch_size, fcst_history, fcst_horizon = get_hyperparameters(n_heads=16,d_model=128, d_ff=256,fcst_horizon=56)

        splits = get_forecasting_splits(df, fcst_history=fcst_history, fcst_horizon=fcst_horizon, datetime_col=datetime_col,
                                valid_size=valid_size, test_size=test_size, show_plot = False)
        train_split = splits[0]
        X, y = prepare_forecasting_data(df, fcst_history=fcst_history, fcst_horizon=fcst_horizon, x_vars=x_vars, y_vars=y_vars)

        learn = TSForecaster(X, y, splits=splits, batch_size=batch_size, path='model_tsai', pipelines=[preproc_pipe, exp_pipe],
                     arch="PatchTST", arch_config=arch_config, metrics=[mse, mae])

        lr_max = learn.lr_find().valley
        learn.fit_one_cycle(n_epochs, lr_max=lr_max)

        y_test_preds, *_ = learn.get_X_preds(X[splits[2]])
        y_test_preds = to_np(y_test_preds)
        y_test = y[splits[2]]

        var0,var1,var2,var3,var4,var5,var6,var7,var8 = get_var_data(y_test)
        var0_pred,var1_pred,var2_pred,var3_pred,var4_pred,var5_pred,var6_pred,var7_pred,var8_pred = get_var_data(y_test_preds)

        results_df = get_results(var0,var1,var2,var3,var4,var5,var6,var7,var8,
                                 var0_pred,var1_pred,var2_pred,var3_pred,var4_pred,var5_pred,var6_pred,var7_pred,var8_pred)
        all_metrics = get_all_metrics(results_df)

        get_chart(results_df)

# fetch the auto logged parameters and metrics
        mlflow.log_param("architecture", arch_config)
        mlflow.log_param("batch size", batch_size)
        mlflow.log_param("epochs number", n_epochs)
        mlflow.log_param("fcst_history", fcst_history)
        mlflow.log_param("fcst_horizon", fcst_horizon)
        mlflow.log_param("learning rate", lr_max)

        mlflow.log_metrics(all_metrics)

        mlflow.log_artifact("predictions.png")
        results_df.reset_index(inplace=True)
        results_df.to_csv('scores.csv',index=True)
        mlflow.log_artifact('scores.csv')
        mlflow.fastai.log_model(learn, "model")
        matplotlib.pyplot.close()

    with mlflow.start_run(description = 'iteration 10',nested=True):        
    # Initialize our model and trainer
        print('\niteration 10\n')  
        arch_config, batch_size, fcst_history, fcst_horizon = get_hyperparameters(n_heads=16,d_model=128, d_ff=256,fcst_history=192,fcst_horizon=24)

        splits = get_forecasting_splits(df, fcst_history=fcst_history, fcst_horizon=fcst_horizon, datetime_col=datetime_col,
                                valid_size=valid_size, test_size=test_size, show_plot = False)
        train_split = splits[0]
        X, y = prepare_forecasting_data(df, fcst_history=fcst_history, fcst_horizon=fcst_horizon, x_vars=x_vars, y_vars=y_vars)

        learn = TSForecaster(X, y, splits=splits, batch_size=batch_size, path='model_tsai', pipelines=[preproc_pipe, exp_pipe],
                     arch="PatchTST", arch_config=arch_config, metrics=[mse, mae])

        lr_max = learn.lr_find().valley
        learn.fit_one_cycle(n_epochs, lr_max=lr_max)

        y_test_preds, *_ = learn.get_X_preds(X[splits[2]])
        y_test_preds = to_np(y_test_preds)
        y_test = y[splits[2]]

        var0,var1,var2,var3,var4,var5,var6,var7,var8 = get_var_data(y_test)
        var0_pred,var1_pred,var2_pred,var3_pred,var4_pred,var5_pred,var6_pred,var7_pred,var8_pred = get_var_data(y_test_preds)

        results_df = get_results(var0,var1,var2,var3,var4,var5,var6,var7,var8,
                                 var0_pred,var1_pred,var2_pred,var3_pred,var4_pred,var5_pred,var6_pred,var7_pred,var8_pred)
        all_metrics = get_all_metrics(results_df)

        get_chart(results_df)

# fetch the auto logged parameters and metrics
        mlflow.log_param("architecture", arch_config)
        mlflow.log_param("batch size", batch_size)
        mlflow.log_param("epochs number", n_epochs)
        mlflow.log_param("fcst_history", fcst_history)
        mlflow.log_param("fcst_horizon", fcst_horizon)
        mlflow.log_param("learning rate", lr_max)

        mlflow.log_metrics(all_metrics)

        mlflow.log_artifact("predictions.png")
        results_df.reset_index(inplace=True)
        results_df.to_csv('scores.csv',index=True)
        mlflow.log_artifact('scores.csv')
        mlflow.fastai.log_model(learn, "model")
        matplotlib.pyplot.close()

    with mlflow.start_run(description = 'iteration 11',nested=True):        
    # Initialize our model and trainer
        print('\niteration 11\n')  
        arch_config, batch_size, fcst_history, fcst_horizon = get_hyperparameters(n_heads=16,d_model=128, d_ff=256,fcst_history=96,fcst_horizon=24)

        splits = get_forecasting_splits(df, fcst_history=fcst_history, fcst_horizon=fcst_horizon, datetime_col=datetime_col,
                                valid_size=valid_size, test_size=test_size, show_plot = False)
        train_split = splits[0]
        X, y = prepare_forecasting_data(df, fcst_history=fcst_history, fcst_horizon=fcst_horizon, x_vars=x_vars, y_vars=y_vars)

        learn = TSForecaster(X, y, splits=splits, batch_size=batch_size, path='model_tsai', pipelines=[preproc_pipe, exp_pipe],
                     arch="PatchTST", arch_config=arch_config, metrics=[mse, mae])

        lr_max = learn.lr_find().valley
        learn.fit_one_cycle(n_epochs, lr_max=lr_max)

        y_test_preds, *_ = learn.get_X_preds(X[splits[2]])
        y_test_preds = to_np(y_test_preds)
        y_test = y[splits[2]]

        var0,var1,var2,var3,var4,var5,var6,var7,var8 = get_var_data(y_test)
        var0_pred,var1_pred,var2_pred,var3_pred,var4_pred,var5_pred,var6_pred,var7_pred,var8_pred = get_var_data(y_test_preds)

        results_df = get_results(var0,var1,var2,var3,var4,var5,var6,var7,var8,
                                 var0_pred,var1_pred,var2_pred,var3_pred,var4_pred,var5_pred,var6_pred,var7_pred,var8_pred)
        all_metrics = get_all_metrics(results_df)

        get_chart(results_df)

# fetch the auto logged parameters and metrics
        mlflow.log_param("architecture", arch_config)
        mlflow.log_param("batch size", batch_size)
        mlflow.log_param("epochs number", n_epochs)
        mlflow.log_param("fcst_history", fcst_history)
        mlflow.log_param("fcst_horizon", fcst_horizon)
        mlflow.log_param("learning rate", lr_max)

        mlflow.log_metrics(all_metrics)

        mlflow.log_artifact("predictions.png")
        results_df.reset_index(inplace=True)
        results_df.to_csv('scores.csv',index=True)
        mlflow.log_artifact('scores.csv')
        mlflow.fastai.log_model(learn, "model")
        matplotlib.pyplot.close()

    with mlflow.start_run(description = 'iteration 12',nested=True):        
    # Initialize our model and trainer
        print('\niteration 12\n')  
        arch_config, batch_size, fcst_history, fcst_horizon = get_hyperparameters(n_heads=16,d_model=128, d_ff=256,dropout=0.1)

        splits = get_forecasting_splits(df, fcst_history=fcst_history, fcst_horizon=fcst_horizon, datetime_col=datetime_col,
                                valid_size=valid_size, test_size=test_size, show_plot = False)
        train_split = splits[0]
        X, y = prepare_forecasting_data(df, fcst_history=fcst_history, fcst_horizon=fcst_horizon, x_vars=x_vars, y_vars=y_vars)

        learn = TSForecaster(X, y, splits=splits, batch_size=batch_size, path='model_tsai', pipelines=[preproc_pipe, exp_pipe],
                     arch="PatchTST", arch_config=arch_config, metrics=[mse, mae])

        lr_max = learn.lr_find().valley
        learn.fit_one_cycle(n_epochs, lr_max=lr_max)

        y_test_preds, *_ = learn.get_X_preds(X[splits[2]])
        y_test_preds = to_np(y_test_preds)
        y_test = y[splits[2]]

        var0,var1,var2,var3,var4,var5,var6,var7,var8 = get_var_data(y_test)
        var0_pred,var1_pred,var2_pred,var3_pred,var4_pred,var5_pred,var6_pred,var7_pred,var8_pred = get_var_data(y_test_preds)

        results_df = get_results(var0,var1,var2,var3,var4,var5,var6,var7,var8,
                                 var0_pred,var1_pred,var2_pred,var3_pred,var4_pred,var5_pred,var6_pred,var7_pred,var8_pred)
        all_metrics = get_all_metrics(results_df)

        get_chart(results_df)

# fetch the auto logged parameters and metrics
        mlflow.log_param("architecture", arch_config)
        mlflow.log_param("batch size", batch_size)
        mlflow.log_param("epochs number", n_epochs)
        mlflow.log_param("fcst_history", fcst_history)
        mlflow.log_param("fcst_horizon", fcst_horizon)
        mlflow.log_param("learning rate", lr_max)

        mlflow.log_metrics(all_metrics)

        mlflow.log_artifact("predictions.png")
        results_df.reset_index(inplace=True)
        results_df.to_csv('scores.csv',index=True)
        mlflow.log_artifact('scores.csv')
        mlflow.fastai.log_model(learn, "model")
        matplotlib.pyplot.close()

    with mlflow.start_run(description = 'iteration 13',nested=True):        
    # Initialize our model and trainer
        print('\niteration 13\n')  
        arch_config, batch_size, fcst_history, fcst_horizon = get_hyperparameters(n_heads=16,d_model=128, d_ff=256,dropout=0.5)

        splits = get_forecasting_splits(df, fcst_history=fcst_history, fcst_horizon=fcst_horizon, datetime_col=datetime_col,
                                valid_size=valid_size, test_size=test_size, show_plot = False)
        train_split = splits[0]
        X, y = prepare_forecasting_data(df, fcst_history=fcst_history, fcst_horizon=fcst_horizon, x_vars=x_vars, y_vars=y_vars)

        learn = TSForecaster(X, y, splits=splits, batch_size=batch_size, path='model_tsai', pipelines=[preproc_pipe, exp_pipe],
                     arch="PatchTST", arch_config=arch_config, metrics=[mse, mae])

        lr_max = learn.lr_find().valley
        learn.fit_one_cycle(n_epochs, lr_max=lr_max)

        y_test_preds, *_ = learn.get_X_preds(X[splits[2]])
        y_test_preds = to_np(y_test_preds)
        y_test = y[splits[2]]

        var0,var1,var2,var3,var4,var5,var6,var7,var8 = get_var_data(y_test)
        var0_pred,var1_pred,var2_pred,var3_pred,var4_pred,var5_pred,var6_pred,var7_pred,var8_pred = get_var_data(y_test_preds)

        results_df = get_results(var0,var1,var2,var3,var4,var5,var6,var7,var8,
                                 var0_pred,var1_pred,var2_pred,var3_pred,var4_pred,var5_pred,var6_pred,var7_pred,var8_pred)
        all_metrics = get_all_metrics(results_df)

        get_chart(results_df)

# fetch the auto logged parameters and metrics
        mlflow.log_param("architecture", arch_config)
        mlflow.log_param("batch size", batch_size)
        mlflow.log_param("epochs number", n_epochs)
        mlflow.log_param("fcst_history", fcst_history)
        mlflow.log_param("fcst_horizon", fcst_horizon)
        mlflow.log_param("learning rate", lr_max)

        mlflow.log_metrics(all_metrics)

        mlflow.log_artifact("predictions.png")
        results_df.reset_index(inplace=True)
        results_df.to_csv('scores.csv',index=True)
        mlflow.log_artifact('scores.csv')
        mlflow.fastai.log_model(learn, "model")
        matplotlib.pyplot.close()

    with mlflow.start_run(description = 'iteration 14',nested=True):        
    # Initialize our model and trainer
        print('\niteration 14\n')  
        arch_config, batch_size, fcst_history, fcst_horizon = get_hyperparameters(n_heads=16,d_model=128, d_ff=256,batch_size=8)

        splits = get_forecasting_splits(df, fcst_history=fcst_history, fcst_horizon=fcst_horizon, datetime_col=datetime_col,
                                valid_size=valid_size, test_size=test_size, show_plot = False)
        train_split = splits[0]
        X, y = prepare_forecasting_data(df, fcst_history=fcst_history, fcst_horizon=fcst_horizon, x_vars=x_vars, y_vars=y_vars)

        learn = TSForecaster(X, y, splits=splits, batch_size=batch_size, path='model_tsai', pipelines=[preproc_pipe, exp_pipe],
                     arch="PatchTST", arch_config=arch_config, metrics=[mse, mae])

        lr_max = learn.lr_find().valley
        learn.fit_one_cycle(n_epochs, lr_max=lr_max)

        y_test_preds, *_ = learn.get_X_preds(X[splits[2]])
        y_test_preds = to_np(y_test_preds)
        y_test = y[splits[2]]

        var0,var1,var2,var3,var4,var5,var6,var7,var8 = get_var_data(y_test)
        var0_pred,var1_pred,var2_pred,var3_pred,var4_pred,var5_pred,var6_pred,var7_pred,var8_pred = get_var_data(y_test_preds)

        results_df = get_results(var0,var1,var2,var3,var4,var5,var6,var7,var8,
                                 var0_pred,var1_pred,var2_pred,var3_pred,var4_pred,var5_pred,var6_pred,var7_pred,var8_pred)
        all_metrics = get_all_metrics(results_df)

        get_chart(results_df)

# fetch the auto logged parameters and metrics
        mlflow.log_param("architecture", arch_config)
        mlflow.log_param("batch size", batch_size)
        mlflow.log_param("epochs number", n_epochs)
        mlflow.log_param("fcst_history", fcst_history)
        mlflow.log_param("fcst_horizon", fcst_horizon)
        mlflow.log_param("learning rate", lr_max)

        mlflow.log_metrics(all_metrics)

        mlflow.log_artifact("predictions.png")
        results_df.reset_index(inplace=True)
        results_df.to_csv('scores.csv',index=True)
        mlflow.log_artifact('scores.csv')
        mlflow.fastai.log_model(learn, "model")
        matplotlib.pyplot.close()

    with mlflow.start_run(description = 'iteration 15',nested=True):        
    # Initialize our model and trainer
        print('\niteration 15\n')  
        arch_config, batch_size, fcst_history, fcst_horizon = get_hyperparameters(n_heads=16,d_model=128, d_ff=256,batch_size=32)

        splits = get_forecasting_splits(df, fcst_history=fcst_history, fcst_horizon=fcst_horizon, datetime_col=datetime_col,
                                valid_size=valid_size, test_size=test_size, show_plot = False)
        train_split = splits[0]
        X, y = prepare_forecasting_data(df, fcst_history=fcst_history, fcst_horizon=fcst_horizon, x_vars=x_vars, y_vars=y_vars)

        learn = TSForecaster(X, y, splits=splits, batch_size=batch_size, path='model_tsai', pipelines=[preproc_pipe, exp_pipe],
                     arch="PatchTST", arch_config=arch_config, metrics=[mse, mae])

        lr_max = learn.lr_find().valley
        learn.fit_one_cycle(n_epochs, lr_max=lr_max)

        y_test_preds, *_ = learn.get_X_preds(X[splits[2]])
        y_test_preds = to_np(y_test_preds)
        y_test = y[splits[2]]

        var0,var1,var2,var3,var4,var5,var6,var7,var8 = get_var_data(y_test)
        var0_pred,var1_pred,var2_pred,var3_pred,var4_pred,var5_pred,var6_pred,var7_pred,var8_pred = get_var_data(y_test_preds)

        results_df = get_results(var0,var1,var2,var3,var4,var5,var6,var7,var8,
                                 var0_pred,var1_pred,var2_pred,var3_pred,var4_pred,var5_pred,var6_pred,var7_pred,var8_pred)
        all_metrics = get_all_metrics(results_df)

        get_chart(results_df)

# fetch the auto logged parameters and metrics
        mlflow.log_param("architecture", arch_config)
        mlflow.log_param("batch size", batch_size)
        mlflow.log_param("epochs number", n_epochs)
        mlflow.log_param("fcst_history", fcst_history)
        mlflow.log_param("fcst_horizon", fcst_horizon)
        mlflow.log_param("learning rate", lr_max)

        mlflow.log_metrics(all_metrics)

        mlflow.log_artifact("predictions.png")
        results_df.reset_index(inplace=True)
        results_df.to_csv('scores.csv',index=True)
        mlflow.log_artifact('scores.csv')
        mlflow.fastai.log_model(learn, "model")
        matplotlib.pyplot.close()

    with mlflow.start_run(description = 'iteration 16',nested=True):        
    # Initialize our model and trainer
        print('\niteration 16\n')  
        arch_config, batch_size, fcst_history, fcst_horizon = get_hyperparameters(n_heads=16,d_model=128, d_ff=256,batch_size=64)

        splits = get_forecasting_splits(df, fcst_history=fcst_history, fcst_horizon=fcst_horizon, datetime_col=datetime_col,
                                valid_size=valid_size, test_size=test_size, show_plot = False)
        train_split = splits[0]
        X, y = prepare_forecasting_data(df, fcst_history=fcst_history, fcst_horizon=fcst_horizon, x_vars=x_vars, y_vars=y_vars)

        learn = TSForecaster(X, y, splits=splits, batch_size=batch_size, path='model_tsai', pipelines=[preproc_pipe, exp_pipe],
                     arch="PatchTST", arch_config=arch_config, metrics=[mse, mae])

        lr_max = learn.lr_find().valley
        learn.fit_one_cycle(n_epochs, lr_max=lr_max)

        y_test_preds, *_ = learn.get_X_preds(X[splits[2]])
        y_test_preds = to_np(y_test_preds)
        y_test = y[splits[2]]

        var0,var1,var2,var3,var4,var5,var6,var7,var8 = get_var_data(y_test)
        var0_pred,var1_pred,var2_pred,var3_pred,var4_pred,var5_pred,var6_pred,var7_pred,var8_pred = get_var_data(y_test_preds)

        results_df = get_results(var0,var1,var2,var3,var4,var5,var6,var7,var8,
                                 var0_pred,var1_pred,var2_pred,var3_pred,var4_pred,var5_pred,var6_pred,var7_pred,var8_pred)
        all_metrics = get_all_metrics(results_df)

        get_chart(results_df)

# fetch the auto logged parameters and metrics
        mlflow.log_param("architecture", arch_config)
        mlflow.log_param("batch size", batch_size)
        mlflow.log_param("epochs number", n_epochs)
        mlflow.log_param("fcst_history", fcst_history)
        mlflow.log_param("fcst_horizon", fcst_horizon)
        mlflow.log_param("learning rate", lr_max)

        mlflow.log_metrics(all_metrics)

        mlflow.log_artifact("predictions.png")
        results_df.reset_index(inplace=True)
        results_df.to_csv('scores.csv',index=True)
        mlflow.log_artifact('scores.csv')
        mlflow.fastai.log_model(learn, "model")
        matplotlib.pyplot.close()

    with mlflow.start_run(description = 'iteration 17',nested=True):        
    # Initialize our model and trainer
        print('\niteration 17\n')  
        arch_config, batch_size, fcst_history, fcst_horizon = get_hyperparameters(n_heads=16,d_model=128, d_ff=256,patch_len=8,stride=8)

        splits = get_forecasting_splits(df, fcst_history=fcst_history, fcst_horizon=fcst_horizon, datetime_col=datetime_col,
                                valid_size=valid_size, test_size=test_size, show_plot = False)
        train_split = splits[0]
        X, y = prepare_forecasting_data(df, fcst_history=fcst_history, fcst_horizon=fcst_horizon, x_vars=x_vars, y_vars=y_vars)

        learn = TSForecaster(X, y, splits=splits, batch_size=batch_size, path='model_tsai', pipelines=[preproc_pipe, exp_pipe],
                     arch="PatchTST", arch_config=arch_config, metrics=[mse, mae])

        lr_max = learn.lr_find().valley
        learn.fit_one_cycle(n_epochs, lr_max=lr_max)

        y_test_preds, *_ = learn.get_X_preds(X[splits[2]])
        y_test_preds = to_np(y_test_preds)
        y_test = y[splits[2]]

        var0,var1,var2,var3,var4,var5,var6,var7,var8 = get_var_data(y_test)
        var0_pred,var1_pred,var2_pred,var3_pred,var4_pred,var5_pred,var6_pred,var7_pred,var8_pred = get_var_data(y_test_preds)

        results_df = get_results(var0,var1,var2,var3,var4,var5,var6,var7,var8,
                                 var0_pred,var1_pred,var2_pred,var3_pred,var4_pred,var5_pred,var6_pred,var7_pred,var8_pred)
        all_metrics = get_all_metrics(results_df)

        get_chart(results_df)

# fetch the auto logged parameters and metrics
        mlflow.log_param("architecture", arch_config)
        mlflow.log_param("batch size", batch_size)
        mlflow.log_param("epochs number", n_epochs)
        mlflow.log_param("fcst_history", fcst_history)
        mlflow.log_param("fcst_horizon", fcst_horizon)
        mlflow.log_param("learning rate", lr_max)

        mlflow.log_metrics(all_metrics)

        mlflow.log_artifact("predictions.png")
        results_df.reset_index(inplace=True)
        results_df.to_csv('scores.csv',index=True)
        mlflow.log_artifact('scores.csv')
        mlflow.fastai.log_model(learn, "model")
        matplotlib.pyplot.close()

    with mlflow.start_run(description = 'iteration 18',nested=True):        
    # Initialize our model and trainer
        print('\niteration 18\n')  
        arch_config, batch_size, fcst_history, fcst_horizon = get_hyperparameters(n_heads=16,d_model=128, d_ff=256,patch_len=16,stride=16)

        splits = get_forecasting_splits(df, fcst_history=fcst_history, fcst_horizon=fcst_horizon, datetime_col=datetime_col,
                                valid_size=valid_size, test_size=test_size, show_plot = False)
        train_split = splits[0]
        X, y = prepare_forecasting_data(df, fcst_history=fcst_history, fcst_horizon=fcst_horizon, x_vars=x_vars, y_vars=y_vars)

        learn = TSForecaster(X, y, splits=splits, batch_size=batch_size, path='model_tsai', pipelines=[preproc_pipe, exp_pipe],
                     arch="PatchTST", arch_config=arch_config, metrics=[mse, mae])

        lr_max = learn.lr_find().valley
        learn.fit_one_cycle(n_epochs, lr_max=lr_max)

        y_test_preds, *_ = learn.get_X_preds(X[splits[2]])
        y_test_preds = to_np(y_test_preds)
        y_test = y[splits[2]]

        var0,var1,var2,var3,var4,var5,var6,var7,var8 = get_var_data(y_test)
        var0_pred,var1_pred,var2_pred,var3_pred,var4_pred,var5_pred,var6_pred,var7_pred,var8_pred = get_var_data(y_test_preds)

        results_df = get_results(var0,var1,var2,var3,var4,var5,var6,var7,var8,
                                 var0_pred,var1_pred,var2_pred,var3_pred,var4_pred,var5_pred,var6_pred,var7_pred,var8_pred)
        all_metrics = get_all_metrics(results_df)

        get_chart(results_df)

# fetch the auto logged parameters and metrics
        mlflow.log_param("architecture", arch_config)
        mlflow.log_param("batch size", batch_size)
        mlflow.log_param("epochs number", n_epochs)
        mlflow.log_param("fcst_history", fcst_history)
        mlflow.log_param("fcst_horizon", fcst_horizon)
        mlflow.log_param("learning rate", lr_max)

        mlflow.log_metrics(all_metrics)

        mlflow.log_artifact("predictions.png")
        results_df.reset_index(inplace=True)
        results_df.to_csv('scores.csv',index=True)
        mlflow.log_artifact('scores.csv')
        mlflow.fastai.log_model(learn, "model")
        matplotlib.pyplot.close()

    with mlflow.start_run(description = 'iteration 19',nested=True):        
    # Initialize our model and trainer
        print('\niteration 19\n')  
        arch_config, batch_size, fcst_history, fcst_horizon = get_hyperparameters(n_heads=16,d_model=128, d_ff=256,patch_len=32,stride=32)

        splits = get_forecasting_splits(df, fcst_history=fcst_history, fcst_horizon=fcst_horizon, datetime_col=datetime_col,
                                valid_size=valid_size, test_size=test_size, show_plot = False)
        train_split = splits[0]
        X, y = prepare_forecasting_data(df, fcst_history=fcst_history, fcst_horizon=fcst_horizon, x_vars=x_vars, y_vars=y_vars)

        learn = TSForecaster(X, y, splits=splits, batch_size=batch_size, path='model_tsai', pipelines=[preproc_pipe, exp_pipe],
                     arch="PatchTST", arch_config=arch_config, metrics=[mse, mae])

        lr_max = learn.lr_find().valley
        learn.fit_one_cycle(n_epochs, lr_max=lr_max)

        y_test_preds, *_ = learn.get_X_preds(X[splits[2]])
        y_test_preds = to_np(y_test_preds)
        y_test = y[splits[2]]

        var0,var1,var2,var3,var4,var5,var6,var7,var8 = get_var_data(y_test)
        var0_pred,var1_pred,var2_pred,var3_pred,var4_pred,var5_pred,var6_pred,var7_pred,var8_pred = get_var_data(y_test_preds)

        results_df = get_results(var0,var1,var2,var3,var4,var5,var6,var7,var8,
                                 var0_pred,var1_pred,var2_pred,var3_pred,var4_pred,var5_pred,var6_pred,var7_pred,var8_pred)
        all_metrics = get_all_metrics(results_df)

        get_chart(results_df)

# fetch the auto logged parameters and metrics
        mlflow.log_param("architecture", arch_config)
        mlflow.log_param("batch size", batch_size)
        mlflow.log_param("epochs number", n_epochs)
        mlflow.log_param("fcst_history", fcst_history)
        mlflow.log_param("fcst_horizon", fcst_horizon)
        mlflow.log_param("learning rate", lr_max)

        mlflow.log_metrics(all_metrics)

        mlflow.log_artifact("predictions.png")
        results_df.reset_index(inplace=True)
        results_df.to_csv('scores.csv',index=True)
        mlflow.log_artifact('scores.csv')
        mlflow.fastai.log_model(learn, "model")
        matplotlib.pyplot.close()

end_time = datetime.now()

print(end_time-init_time)