import os
import mlflow
import logging
import sklearn
import pathlib
import pandas as pd
import mlflow.fastai
from tsai.basics import *
from datetime import datetime
from mlflow import MlflowClient
from logger import LoggingConfig
from db_access.DbCnx import UserDao
from business.KeyReturn import KeyReturn
from business.HyperParams import HyperParams
from sklearn.metrics import mean_squared_error, mean_absolute_error
from config.variables import VarEnvInferenceModel, VarEnvMLflow

if os.name == 'nt':
    temp = pathlib.PosixPath
    pathlib.PosixPath = pathlib.WindowsPath

# Import du logger
LoggingConfig.setup_logging()

# Import des variables
varenv_inference_model = VarEnvInferenceModel()
varenv_mlflow = VarEnvMLflow()

client = MlflowClient()


class Tools():

    fcst_history = int(varenv_inference_model.fcst_history)  # steps in the past
    fcst_horizon = int(varenv_inference_model.fcst_horizon)  # steps in the future
    valid_size = 0.2  # int or float indicating the size of the training set
    test_size = 0.1  # int or float indicating the size of the test set

    datetime_col = "DATE"
    freq = '3H'

    columns_keep = ['TEMPERATURE', 'WIND_SPEED', 'WIND_DEGREE', 'PRESSURE', 'PRECIP', 'HUMIDITY',
                    'CLOUDCOVER', 'FEELSLIKE', 'UV_INDEX']
    columns_drop = ['WIND_DIR', 'TIME', 'CITY', 'OBSERVATION_TIME', 'VISIBILITY', 'WEATHER_CODE']

    preproc_pipe = sklearn.pipeline.Pipeline(
        # shrink dataframe memory usage
        [('shrinker', TSShrinkDataFrame()),
         # drop duplicate rows (if any)
         ('drop_duplicates', TSDropDuplicates(datetime_col=datetime_col)),
         # add missing timestamps (if any)
         ('add_mts', TSAddMissingTimestamps(datetime_col=datetime_col, freq=freq)),
         # fill missing data (1st ffill. 2nd value=0)
         ('fill_missing', TSFillMissing(columns=columns_keep, method='ffill', value=0)),
         ], verbose=True)

    exp_pipe = sklearn.pipeline.Pipeline(
        # standardize data using train_split
        [('scaler', TSStandardScaler(columns=columns_keep)), ], verbose=True)

    def transform_data(df, city):
        df.insert(0, 'DATE', df['OBSERVATION_TIME'].astype(str) + ' ' + df['TIME'].astype(str))
        df = df.loc[df.CITY == city]
        df = df.drop_duplicates()
        # sort lines to have chronological order
        df['DATE'] = pd.to_datetime(df['DATE'])
        df = df.sort_values(by=['DATE'])
        # reset index to be able to use split function
        df.reset_index(drop=True, inplace=True)
        # remove categorical columns
        df.drop(Tools.columns_drop, inplace=True, axis=1)
        return df

    def get_chart(df, varlist, predlist):
        fig, axes = plt.subplots(3, 3, figsize=(12, 9))  # créé une grille 3x3 de subplots
        axes = axes.ravel()  # convertit le tableau 2D en 1D pour faciliter l'itération

        for i in range(9):  # boucle sur les 9 subplots
            axes[i].plot(varlist[i])  # trace les données réelles
            axes[i].plot(predlist[i])  # trace les prédictions
            axes[i].set_title(df.columns[i + 1], fontsize=10)  # met à jour le titre du subplot

        fig.savefig("predictions.png")
        plt.close(fig)

        for i in range(9):  # boucle sur les 9 subplots
            fig, ax = plt.subplots(figsize=(10, 5))
            ax.plot(varlist[i])  # trace les données réelles
            ax.plot(predlist[i])  # trace les prédictions
            ax.set_title(df.columns[i + 1], fontsize=10)  # met à jour le titre du subplot
            fig.savefig(str(df.columns[i + 1]) + ".png")
            plt.close(fig)

    def get_var_data(y, fcst_horizon):
        dim_var = (int(y.shape[0] / fcst_horizon) + 1)
        vars = [np.ones(dim_var) for _ in range(len(Tools.columns_keep))]  # liste pour stocker les variables

        j = 0
        while j < (dim_var - fcst_horizon):
            y_part = y[j]
            y_part = y_part.flatten()

            for i in range(len(Tools.columns_keep)):
                vars[i][j:j + fcst_horizon] = y_part[fcst_horizon * i:fcst_horizon * (i + 1)]

            j += fcst_horizon

        return vars

    def get_all_metrics(df):
        all_metrics = {}
        for name in df.index:
            all_metrics[name + '_mse'] = float(df.loc[name, 'mse'])
            all_metrics[name + '_mae'] = float(df.loc[name, 'mae'])
        return all_metrics

    def get_results(df, varlist, predlist):
        results_df = pd.DataFrame(columns=["mse", "mae"])

        for i in range(len(varlist)):
            results_df.loc[df.columns[i + 1], "mse"] = round(mean_squared_error(varlist[i], predlist[i]), 2)
            results_df.loc[df.columns[i + 1], "mae"] = round(mean_absolute_error(varlist[i], predlist[i]), 2)

        return results_df

    async def get_forecast(city):
        try:
            # Creating dates to have for inference
            fcst_date = UserDao.get_last_datetime_weather(city)
            dates = pd.date_range(start=None, end=fcst_date, periods=Tools.fcst_history, freq=Tools.freq)

            # loading data used for inference - todo replace the 3 following lines with get_weather_data_df()
            weather_dict = UserDao.get_weather_data()
            df = pd.DataFrame(weather_dict)
            df = df.set_index('ID')

            df_initial = Tools.transform_data(df, 'Margaux')
            new_df = df_initial[df_initial['DATE'].isin(dates)]
            new_df.reset_index(drop=True, inplace=True)
            save_new_df = new_df

            # loading of model
            s3_root = str(varenv_inference_model.s3_root)
            model_inference = str(varenv_inference_model.model_inference)
            path_artifact = str(varenv_inference_model.path_artifact)
            model_uri = f"{s3_root}{model_inference}{path_artifact}"

            learn = mlflow.fastai.load_model(model_uri=model_uri)
            print('model loaded')

            # todo : make this line work
            # new_df = learn.transform(new_df)

            # why y_vars=None ?
            new_X, _ = prepare_forecasting_data(new_df,
                                                fcst_history=Tools.fcst_history,
                                                fcst_horizon=0,
                                                x_vars=Tools.columns_keep,
                                                y_vars=None)
            new_scaled_preds, *_ = learn.get_X_preds(new_X)

            new_scaled_preds = to_np(new_scaled_preds).swapaxes(1, 2).reshape(-1, len(Tools.columns_keep))
            dates = pd.date_range(start=fcst_date, periods=Tools.fcst_horizon + 1, freq=Tools.freq)[1:]
            preds_df = pd.DataFrame(dates, columns=[Tools.datetime_col])
            preds_df.loc[:, Tools.columns_keep] = new_scaled_preds
            # todo : make this line work
            # preds_df = learn.inverse_transform(preds_df)

            df_total_pred = pd.concat([save_new_df, preds_df], ignore_index=True)
            preds_df['city'] = city

            await UserDao.send_data_from_df_to_db(preds_df, table_name='FORECAST_DATA')

            return {KeyReturn.success.value: df_total_pred}

        except Exception as e:
            logging.error(f"Forecast failed : {e}")
            return {f"{KeyReturn.error.value}: Forecast failed : {e}"}

    def train_model(city: str, hyper_params: HyperParams, train_label: str):
        mlflow.set_tracking_uri(varenv_mlflow.mlflow_server_port)

        # import data
        df = UserDao.get_weather_data_df()

        # transform data
        df = Tools.transform_data(df, city)

        try:
            with mlflow.start_run():
                print(f"\n {train_label} \n")

                splits = get_forecasting_splits(df,
                                                fcst_history=hyper_params.fcst_history,
                                                fcst_horizon=hyper_params.fcst_horizon,
                                                datetime_col=Tools.datetime_col,
                                                valid_size=Tools.valid_size,
                                                test_size=Tools.test_size,
                                                show_plot=False)

                X, y = prepare_forecasting_data(df,
                                                fcst_history=hyper_params.fcst_history,
                                                fcst_horizon=hyper_params.fcst_horizon,
                                                x_vars=Tools.columns_keep,
                                                y_vars=Tools.columns_keep)

                learn = TSForecaster(X, y, splits=splits, batch_size=hyper_params.batch_size,
                                     path='model_tsai', pipelines=[Tools.exp_pipe], arch="PatchTST",
                                     arch_config=vars(hyper_params.arch_config), metrics=[mse, mae])

                lr_max = 0.0025
                learn.fit_one_cycle(hyper_params.n_epochs, lr_max=lr_max)
                y_test_preds, *_ = learn.get_X_preds(X[splits[2]])
                y_test_preds = to_np(y_test_preds)
                y_test = y[splits[2]]

                varlist = Tools.get_var_data(y_test, hyper_params.fcst_horizon)
                predlist = Tools.get_var_data(y_test_preds, hyper_params.fcst_horizon)
                results_df = Tools.get_results(df, varlist, predlist)
                all_metrics = Tools.get_all_metrics(results_df)
                Tools.get_chart(df, varlist, predlist)

                logging.info(f"Training performed with hyperparams : {hyper_params}")

                # fetch the auto logged parameters and metrics
                for params in hyper_params.arch_config:
                    mlflow.log_param(params[0], params[1])
                mlflow.log_param("batch size", hyper_params.batch_size)
                mlflow.log_param("epochs number", hyper_params.n_epochs)
                mlflow.log_param("fcst_history", hyper_params.fcst_history)
                mlflow.log_param("fcst_horizon", hyper_params.fcst_horizon)
                mlflow.log_param("learning rate", lr_max)

                mlflow.log_metrics(all_metrics)

                arch = pd.DataFrame(index=[0])
                for params in hyper_params.arch_config:
                    arch.insert(0, params[0], params[1])
                arch.insert(0, "batch_size", hyper_params.batch_size)
                arch.insert(0, "epochs number", hyper_params.n_epochs)
                arch.insert(0, "fcst_history", hyper_params.fcst_history)
                arch.insert(0, "fcst_horizon", hyper_params.fcst_horizon)
                arch.insert(0, "learning rate", lr_max)
                arch.to_csv("hyper_parameters.csv")
                print(arch)
                mlflow.log_artifact("hyper_parameters.csv")
                for signal_name in df.columns[1:]:
                    mlflow.log_artifact(str(signal_name) + ".png")
                mlflow.log_artifact("predictions.png")
                results_df.reset_index(inplace=True)
                results_df.to_csv('scores.csv', index=True)
                mlflow.log_artifact('scores.csv')

                model_name = train_label + '-' + city
                mlflow.fastai.log_model(fastai_learner=learn,
                                        registered_model_name=model_name,
                                        artifact_path="model")
                matplotlib.pyplot.close()
        except Exception as e:
            return {KeyReturn.error.value: f"Training failed : {e}"}

        return {'success': f"Training '{train_label}' terminated - Hyperparameters : {hyper_params}"}

    def launch_trainings(city: str, hyper_params_dict, train_label: str):
        start_time = datetime.now()
        try:
            for hp_key in hyper_params_dict.keys():
                data = hyper_params_dict[hp_key]
                Tools.train_model(city=city, hyper_params=data, train_label=train_label)
                logging.error(f"Trained model successfully with hyperparameters : {data}")

            total_time = datetime.now() - start_time
            return {KeyReturn.success.value: f"Trainings performed in {total_time}"}
        except Exception as e:
            logging.error(f"Trainings failed : {e}")
            return {KeyReturn.error.value: f"Trainings failed : {e}"}

    def model_evaluation(city: str):
        mlflow.set_tracking_uri(varenv_mlflow.mlflow_server_port)

        # import data
        df = UserDao.get_weather_data_df()

        # transform data
        df = Tools.transform_data(df, city)

        try:
            with mlflow.start_run():

                fcst_history = Tools.fcst_history
                fcst_horizon = Tools.fcst_horizon

                splits = get_forecasting_splits(df,
                                                fcst_history=fcst_history,
                                                fcst_horizon=fcst_horizon,
                                                datetime_col=Tools.datetime_col,
                                                valid_size=Tools.valid_size,
                                                test_size=Tools.test_size,
                                                show_plot=False)

                X, y = prepare_forecasting_data(df,
                                                fcst_history=fcst_history,
                                                fcst_horizon=fcst_horizon,
                                                x_vars=Tools.columns_keep,
                                                y_vars=Tools.columns_keep)

                # loading of model
                s3_root = str(varenv_inference_model.s3_root)
                model_inference = str(varenv_inference_model.model_inference)
                path_artifact = str(varenv_inference_model.path_artifact)
                model_uri = f"{s3_root}{model_inference}{path_artifact}"

                learn = mlflow.fastai.load_model(model_uri=model_uri)
                print('model loaded')

                # lr_max = learn.lr_find().valley
                lr_max = 0.0025
                scaled_preds, *_ = learn.get_X_preds(X[splits[1]])
                scaled_preds = to_np(scaled_preds)

                scaled_y_true = y[splits[1]]
                results_df = pd.DataFrame(columns=["mse", "mae"])
                results_df.loc["valid", "mse"] = mean_squared_error(scaled_y_true.flatten(), scaled_preds.flatten())
                results_df.loc["valid", "mae"] = mean_absolute_error(scaled_y_true.flatten(), scaled_preds.flatten())


                y_test_preds, *_ = learn.get_X_preds(X[splits[2]])
                y_test_preds = to_np(y_test_preds)
                y_test = y[splits[2]]

                varlist = Tools.get_var_data(y_test, hyper_params.fcst_horizon)
                predlist = Tools.get_var_data(y_test_preds, hyper_params.fcst_horizon)
                results_df = Tools.get_results(df, varlist, predlist)
                all_metrics = Tools.get_all_metrics(results_df)
                Tools.get_chart(df, varlist, predlist)


                # fetch the auto logged parameters and metrics
                for params in hyper_params.arch_config:
                    mlflow.log_param(params[0], params[1])
                mlflow.log_param("batch size", hyper_params.batch_size)
                mlflow.log_param("epochs number", hyper_params.n_epochs)
                mlflow.log_param("fcst_history", hyper_params.fcst_history)
                mlflow.log_param("fcst_horizon", hyper_params.fcst_horizon)
                mlflow.log_param("learning rate", lr_max)

                mlflow.log_metrics(all_metrics)

                for signal_name in df.columns[1:]:
                    mlflow.log_artifact(str(signal_name) + ".png")
                mlflow.log_artifact("predictions.png")
                results_df.reset_index(inplace=True)
                results_df.to_csv('scores.csv', index=True)
                mlflow.log_artifact('scores.csv')

                model_name = train_label + '-' + city
                mlflow.fastai.log_model(fastai_learner=learn,
                                        registered_model_name=model_name,
                                        artifact_path="model")
                matplotlib.pyplot.close()

                logging.info(f"Retraining performed with model : {varenv_inference_model.model_inference}")

                matplotlib.pyplot.close()
        except Exception as e:
            return {KeyReturn.error.value: f"Training failed : {e}"}

        return {'success': "Retraining terminated with success"}

    def retrain(city: str, n_epochs: int):
        mlflow.set_tracking_uri(varenv_mlflow.mlflow_server_port)

        # import data
        df = UserDao.get_weather_data_df()

        # transform data
        df = Tools.transform_data(df, city)

        try:
            with mlflow.start_run():
                
                fcst_history = Tools.fcst_history
                fcst_horizon = Tools.fcst_horizon

                splits = get_forecasting_splits(df,
                                                fcst_history=fcst_history,
                                                fcst_horizon=fcst_horizon,
                                                datetime_col=Tools.datetime_col,
                                                valid_size=Tools.valid_size,
                                                test_size=Tools.test_size,
                                                show_plot=False)

                X, y = prepare_forecasting_data(df,
                                                fcst_history=fcst_history,
                                                fcst_horizon=fcst_horizon,
                                                x_vars=Tools.columns_keep,
                                                y_vars=Tools.columns_keep)

                # loading of model
                s3_root = str(varenv_inference_model.s3_root)
                model_inference = str(varenv_inference_model.model_inference)
                path_artifact = str(varenv_inference_model.path_artifact)
                model_uri = f"{s3_root}{model_inference}{path_artifact}"

                learn = mlflow.fastai.load_model(model_uri=model_uri)
                print('model loaded')

                # lr_max = learn.lr_find().valley
                lr_max = 0.0025
                learn.fit_one_cycle(n_epochs, lr_max=lr_max)

                y_test_preds, *_ = learn.get_X_preds(X[splits[2]])
                y_test_preds = to_np(y_test_preds)
                y_test = y[splits[2]]

                varlist = Tools.get_var_data(y_test, fcst_horizon)
                predlist = Tools.get_var_data(y_test_preds, fcst_horizon)
                results_df = Tools.get_results(df, varlist, predlist)
                all_metrics = Tools.get_all_metrics(results_df)
                Tools.get_chart(df, varlist, predlist)

                logging.info(f"Retraining performed with model : {varenv_inference_model.model_inference}")

                mlflow.log_metrics(all_metrics)

                mlflow.log_artifact("predictions.png")
                results_df.reset_index(inplace=True)
                results_df.to_csv('scores.csv', index=True)
                mlflow.log_artifact('scores.csv')


                mlflow.fastai.log_model(fastai_learner=learn,
                                        model_name=
                                        artifact_path="model")


                matplotlib.pyplot.close()
        except Exception as e:
            return {KeyReturn.error.value: f"Training failed : {e}"}

        return {'success': "Retraining terminated with success"}
