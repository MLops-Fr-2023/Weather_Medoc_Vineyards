import pandas as pd
from tsai.inference import load_learner
from tsai.basics import *
from db_access.DbCnx import UserDao

class Tools():

    city = "Margaux"
    fcst_history = 365 # # steps in the past
    fcst_horizon = 7  # # steps in the future
    # valid_size   = 0.2  # int or float indicating the size of the training set
    # test_size    = 0.1  # int or float indicating the size of the test set

    datetime_col = "DATE"
    freq = '3H'
    # method = 'ffill'
    # value = 0

    def transform_data(df, city):
        df.insert(0, 'DATE', df['OBSERVATION_TIME'].astype(str) + ' ' + df['TIME'].astype(str))
        df = df[df.CITY == city]
        df = df.sort_values(by=['DATE'])  # sort lines to have chronological order
        df['DATE'] = pd.to_datetime(df['DATE'])
        # reset index to be able to use split function
        df.reset_index(drop = True, inplace = True)                     
        # remove categorical columns
        df.drop(['WIND_DIR','TIME','CITY','OBSERVATION_TIME','VISIBILITY', 'WEATHER_CODE'], inplace = True, axis = 1)   
        return df
    
    def get_forecast(city):
        # Creating dates to have for inference
        fcst_date = UserDao.get_last_datetime_weather(Tools.city)
        dates = pd.date_range(start=None, end=fcst_date, periods=Tools.fcst_history, freq=Tools.freq)

        # loading data used for inference
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