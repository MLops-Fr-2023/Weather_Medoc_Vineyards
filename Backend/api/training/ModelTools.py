import pandas as pd
import sklearn
from sklearn.metrics import mean_squared_error, mean_absolute_error
from tsai.inference import load_learner
from tsai.basics import *
from db_access.DbCnx import UserDao
from business.HyperParams import HyperParams, ArchConfig
from db_access.DbCnx import UserDao
import mlflow.fastai
import mlflow
import logging
from logger import LoggingConfig

import os
import pathlib
if os.name == 'nt':
    temp = pathlib.PosixPath
    pathlib.PosixPath = pathlib.WindowsPath

LoggingConfig.setup_logging()

class Tools():

    fcst_history = 365 # steps in the past
    fcst_horizon = 7   # steps in the future
    valid_size   = 0.2 # int or float indicating the size of the training set
    test_size    = 0.1 # int or float indicating the size of the test set

    datetime_col = "DATE"
    freq = '3H'
    
    columns_keep = ['TEMPERATURE','WIND_SPEED','WIND_DEGREE','PRESSURE','PRECIP','HUMIDITY','CLOUDCOVER','FEELSLIKE','UV_INDEX']
    columns_drop = ['WIND_DIR','TIME','CITY','OBSERVATION_TIME','VISIBILITY', 'WEATHER_CODE']
    
    x_vars = columns_keep
    y_vars = columns_keep

    n_epochs = 50

    preproc_pipe = sklearn.pipeline.Pipeline([
        ('shrinker', TSShrinkDataFrame()), # shrink dataframe memory usage
        ('drop_duplicates', TSDropDuplicates(datetime_col=datetime_col)), # drop duplicate rows (if any)
        ('add_mts', TSAddMissingTimestamps(datetime_col=datetime_col, freq=freq)), # add missing timestamps (if any)
        ('fill_missing', TSFillMissing(columns=columns_keep, method='ffill', value=0)), # fill missing data (1st ffill. 2nd value=0)
        ], 
        verbose=True)

    exp_pipe = sklearn.pipeline.Pipeline([
        ('scaler', TSStandardScaler(columns=columns_keep)), # standardize data using train_split
        ], 
        verbose=True)

    def transform_data(df, city):
        df.insert(0, 'DATE', df['OBSERVATION_TIME'].astype(str) + ' ' + df['TIME'].astype(str))
        df = df.loc[df.CITY == city]
        df = df.sort_values(by=['DATE'])  # sort lines to have chronological order
        df['DATE'] = pd.to_datetime(df['DATE'])
        # reset index to be able to use split function
        df.reset_index(drop = True, inplace = True)                     
        # remove categorical columns
        df.drop(Tools.columns_drop, inplace = True, axis = 1)   
        return df
    
    def get_chart(results_df, df, varlist, predlist):
        fig, axes = plt.subplots(3, 3, figsize=(12, 9)) # créé une grille 3x3 de subplots
        axes = axes.ravel() # convertit le tableau 2D en 1D pour faciliter l'itération

        for i in range(9): # boucle sur les 9 subplots
            axes[i].plot(varlist[i]) # trace les données réelles
            axes[i].plot(predlist[i]) # trace les prédictions
            axes[i].set_title(df.columns[i+1], fontsize=10) # met à jour le titre du subplot

        fig.savefig("predictions.png")
        plt.close(fig)
    
    def get_hyperparameters(n_layers =3,n_heads=16,d_model=16,d_ff=128,attn_dropout=0.0,dropout=0.3,patch_len=24,stride=24,padding_patch=True,
                        batch_size=16,fcst_history=400,fcst_horizon=8):


        arch_config = ArchConfig(n_layers=n_layers, n_heads=n_heads, d_model=d_model, d_ff=d_ff, attn_dropout=attn_dropout, patch_len=patch_len, 
                                 stride=stride, padding_patch=padding_patch)
        hyper_params = HyperParams(arch_config=arch_config, batch_size=batch_size, fcst_history=fcst_history, fcst_horizon=fcst_horizon)

        return hyper_params

    def get_var_data(y, fcst_horizon):
        dim_var = (int(y.shape[0]/fcst_horizon) + 1)
        vars = [np.ones(dim_var) for _ in range(len(Tools.columns_keep))] # liste pour stocker les variables

        j = 0
        while j < (dim_var-fcst_horizon):
            y_part = y[j]
            y_part = y_part.flatten()
            
            for i in range(len(Tools.columns_keep)): 
                vars[i][j:j+fcst_horizon] = y_part[fcst_horizon*i:fcst_horizon*(i+1)]
            
            j += fcst_horizon

        return vars

    def get_all_metrics(df):
        all_metrics = {}
        for name in df.index:
            all_metrics[name+'_mse'] = float(df.loc[name,'mse'])
            all_metrics[name+'_mae'] = float(df.loc[name,'mae'])
        return all_metrics

    def get_results(df, varlist, predlist):
        results_df = pd.DataFrame(columns=["mse", "mae"])

        for i in range(len(varlist)):
            results_df.loc[df.columns[i+1], "mse"] = round(mean_squared_error(varlist[i], predlist[i]), 2)
            results_df.loc[df.columns[i+1], "mae"] = round(mean_absolute_error(varlist[i], predlist[i]), 2)

        return results_df

    def get_forecast(city):
        try:
            # Creating dates to have for inference
            fcst_date = UserDao.get_last_datetime_weather(city)
            dates = pd.date_range(start=None, end=fcst_date, periods=Tools.fcst_history, freq=Tools.freq)

            # loading data used for inference - todo replace the 3 following lines with get_weather_data_df()
            weather_dict = UserDao.get_weather_data()
            df = pd.DataFrame(weather_dict)
            df = df.set_index('ID')

            df_initial = Tools.transform_data(df,'Margaux')
            new_df = df_initial[df_initial['DATE'].isin(dates)]
            new_df.reset_index(drop = True, inplace = True)
            save_new_df = new_df

            # loading of model
            learn = load_learner(fname='Margaux_v2b.pt')

            # todo : make this line work
            # new_df = learn.transform(new_df)

            # inference
            x_vars = new_df.columns[1:]
            y_vars = new_df.columns[1:]
            
            # why y_vars=None ?
            new_X, _ = prepare_forecasting_data(new_df, fcst_history=Tools.fcst_history, fcst_horizon=0, x_vars=x_vars, y_vars=None)
            new_scaled_preds, *_ = learn.get_X_preds(new_X)

            new_scaled_preds = to_np(new_scaled_preds).swapaxes(1,2).reshape(-1, len(y_vars))
            dates = pd.date_range(start=fcst_date, periods=Tools.fcst_horizon + 1, freq= Tools.freq)[1:]
            preds_df = pd.DataFrame(dates, columns=[Tools.datetime_col])
            preds_df.loc[:, y_vars] = new_scaled_preds
            # todo : make this line work
            # preds_df = learn.inverse_transform(preds_df)

            df_total_pred= pd.concat([save_new_df, preds_df], ignore_index = True)

            return df_total_pred 
        except Exception as e:
            logging.error(f"Forecast failed : {e}")
            return {'error': f"Forecast failed"}        

    def train_model(city: str, hyper_params: HyperParams, train_label: str):

        # import data
        df = UserDao.get_weather_data_df()  

        # transform data
        df = Tools.transform_data(df, city)
        
        with mlflow.start_run():
            with mlflow.start_run(description = train_label,nested=True):

                print(f"\n {train_label} \n")       
                # Initialize model and trainer
                hyper_params = Tools.get_hyperparameters()

                splits = get_forecasting_splits(df, fcst_history=hyper_params.fcst_history, fcst_horizon=hyper_params.fcst_horizon, datetime_col=Tools.datetime_col,
                                        valid_size=Tools.valid_size, test_size=Tools.test_size, show_plot = False)
                train_split = splits[0]

                X, y = prepare_forecasting_data(df, fcst_history=hyper_params.fcst_history, fcst_horizon=hyper_params.fcst_horizon, x_vars=Tools.x_vars, y_vars=Tools.y_vars)

                learn = TSForecaster(X, y, splits=splits, batch_size=hyper_params.batch_size, path='model_tsai', pipelines=[Tools.preproc_pipe, Tools.exp_pipe],
                            arch="PatchTST", arch_config=vars(hyper_params.arch_config), metrics=[mse, mae])

                lr_max = learn.lr_find().valley
                learn.fit_one_cycle(Tools.n_epochs, lr_max=lr_max)

                y_test_preds, *_ = learn.get_X_preds(X[splits[2]])
                y_test_preds = to_np(y_test_preds)
                y_test = y[splits[2]]

                varlist = Tools.get_var_data(y_test, Tools.fcst_horizon)
                predlist = Tools.get_var_data(y_test_preds, Tools.fcst_horizon)
                results_df = Tools.get_results(df, varlist, predlist)
                all_metrics = Tools.get_all_metrics(results_df)

                Tools.get_chart(results_df, df, varlist, predlist)

                logging.info(f"Training performed with hyperparams : {hyper_params}")

                # fetch the auto logged parameters and metrics
                mlflow.log_param("architecture", hyper_params.arch_config)
                mlflow.log_param("batch size", hyper_params.batch_size)
                mlflow.log_param("epochs number", Tools.n_epochs)
                mlflow.log_param("fcst_history", hyper_params.fcst_history)
                mlflow.log_param("fcst_horizon", hyper_params.fcst_horizon)
                mlflow.log_param("learning rate", lr_max)

                mlflow.log_metrics(all_metrics)

                mlflow.log_artifact("predictions.png")
                results_df.reset_index(inplace=True)
                results_df.to_csv('scores.csv',index=True)
                mlflow.log_artifact('scores.csv')
                mlflow.fastai.log_model(learn, "model")
                matplotlib.pyplot.close()

        return {'success': 'Training terminated'}                