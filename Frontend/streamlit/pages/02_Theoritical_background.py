import streamlit as st
import libs.tools as tools

tools.set_page_config()

images_path = tools.get_images_path()
page_intro = "Introduction"
page_data_ctxt = "Data context"
page_api_db = "API - DB - Model"
page_model_tracking = "Model tracking"
page_infrastruct = "Infrastructure"
page_transformers = "Transformers"


def display_page_title():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.title('Project background')
        c1, c2, c3, c4 = st.columns(4, gap="large")
    st.markdown("""---""")


def main():

    display_page_title()

    choice = st.sidebar.radio("Submenu", [page_intro, page_data_ctxt, page_api_db, page_model_tracking,
                                          page_infrastruct, page_transformers])

    if choice == page_intro:
        col1, col2, col3 = st.columns([0.5, 8, 0.5])
        with col2:
            st.write("""
                     In today's rapidly evolving world of data science and machine learning,
                     integrating MLOps (Machine Learning Operations) into projects has become
                     essential to ensure efficiency, scalability, and reliability. In this context,
                     the wine industry can greatly benefit from MLOps implementation to improve
                     weather prediction in vineyards. By leveraging data science techniques,
                     advanced machine learning models, and a robust MLOps pipeline, winemakers
                     can gain valuable insights that optimize cultivation strategies and ultimately
                     enhance wine quality and yields.

                    #### Challenges in Wineyard Weather Prediction

                     Vineyard management heavily relies on weather conditions. Temperature, humidity,
                     sunlight, and precipitation significantly impact grape growth, maturation, and disease
                     susceptibility. However, predicting weather patterns in specific vineyard locations
                     can be challenging due to the complexity of atmospheric processes and the inherent
                     variability in regional climates.

                    #### Data Collection and Preprocessing

                    The foundation of any successful data science project is the availability of
                     high-quality data. In this wineyard weather prediction project,
                     a diverse range of data sources is collected, including historical
                     weather records, satellite imagery, soil composition data, and even information
                     from IoT (Internet of Things) devices installed throughout the vineyard.

                    Data preprocessing is a crucial step in MLOps. The collected data needs to be cleaned,
                     normalized, and transformed into a suitable format for model training and validation.
                     Handling missing values and outliers is essential to ensure accurate and reliable predictions.

                    #### Machine Learning Model Development

                    For wineyard weather prediction, sophisticated machine learning models, such as
                     Long Short-Term Memory (LSTM) networks, can be employed. LSTMs are well-suited
                     for time-series forecasting tasks, making them ideal for predicting weather patterns,
                     which often exhibit temporal dependencies.

                    The model is trained on historical weather data with corresponding ground truth observations,
                     ensuring it learns to capture the underlying patterns and relationships between various weather
                     variables. The training process is iterative, with hyperparameter tuning to optimize
                     model performance.

                    #### MLops Implementation

                    MLOps refers to the set of practices and tools that streamline the development, deployment, and
                     monitoring of machine learning models. In this project, MLOps principles are employed to build a
                     reliable and scalable pipeline.

                    - Version Control: The codebase and model artifacts are stored in a version control system
                     (e.g., Git)to track changes and facilitate collaboration among team members.
                    - Continuous Integration and Continuous Deployment (CI/CD): An automated CI/CD pipeline is
                     established to ensure seamless integration of new code changes, automatic model retraining,
                     and deployment of updated models to production.
                    - Monitoring and Logging: Metrics like model accuracy, prediction error, and data drift are
                     continuously monitored to detect performance degradation and ensure the model's health.
                    - Model Governance: Strict model versioning and documentation are enforced to ensure
                     reproducibility and compliance with industry regulations.
                    - Scalability: The MLOps pipeline is designed to scale efficiently, accommodating larger
                     datasets and more complex models as the project evolves.

                    #### Conclusion

                    By harnessing the power of data science, advanced machine learning models, and MLOps
                     principles, the wine industry can make significant strides in weather prediction for
                     vineyards. The ability to forecast weather conditions accurately empowers winemakers
                     to make informed decisions, optimize cultivation strategies, and adapt to changing
                     environmental factors. Ultimately, this project holds the potential to enhance wine
                     quality and yields, contributing to the sustainable growth of the wine industry.""")

            st.write("""""")

    if choice == page_data_ctxt:
        col1, col2, col3 = st.columns([0.5, 8, 0.5])
        with col2:
            st.title(page_data_ctxt)
            st.markdown("""---""")
            st.write("""
                     The aim of the project is to provide weather forecasts for the area of the great wine châteaux
                     in Gironde. In order to cover the prediction zone, 7 towns have been identified :
                    - Arsac
                    - Ludon-Medoc
                    - Lamarque
                    - Castelnau-de-Medoc
                    - Macau
                    - Soussan
                    - Margaux

                    For these towns, the data sets studied are: 'observation_time', 'temperature', 'weather_code',
                     'wind_speed', 'wind_degree', 'wind_dir', 'pressure', 'precip', 'humidity', 'cloudcover',
                     'feelslike', 'uv_index', 'visibility', 'time', 'city'.
                    The use of this data by the winegrowers enables them to make assumptions about the weather in
                     the future, and therefore about the winegrowing choices to be made.\n
                    In order to make meaningful predictions, the data needs to go back far enough in time to learn
                     about the relationships and patterns of change between the variables. To this end, all of the
                     data for the features described above was retrieved up to 2008.
                    These data were retrieved thanks to an home made Python script used to run queries a data provider:
                     https://weatherstack.com/
                    """)

        st.markdown("""---""")
        col1, col2, col3 = st.columns([0.5, 8, 0.5])
        with col2:
            st.title('Maps')
            st.markdown("""---""")
            col1, col2 = st.columns([1, 1])
            with col1:
                st.write("")
                st.write("")
                st.write("")
                st.write("""
                         Here is represented the geographical position of the seven selected Cities.
                         They are all situated on the North-West of Bordeaux, France""")
                st.write("")
                st.write("")
                st.write("")
            with col2:
                st.image(images_path + 'Maps_cities.png', channels="RGB", output_format="auto")

    if choice == page_api_db:
        st.markdown("## MySql Database")
        cols = st.columns([0.5, 0.5, 0.5])
        with cols[0]:
            st.markdown("### Users and permissions")
            st.image(images_path + 'db_sql_users_perms.png', channels="RGB", output_format="auto")
        with cols[1]:
            st.markdown("### Weather data")
            st.image(images_path + 'db_sql_weather_data.png', channels="RGB", output_format="auto")
        with cols[2]:
            st.markdown("### Model data")
            st.image(images_path + 'db_sql_model_data.png', channels="RGB", output_format="auto")

        st.markdown("---")

        st.markdown("## API features")

        cols = st.columns(3)
        with cols[0]:
            st.markdown("---")
            st.markdown("##### Users and permissions")
            st.markdown("""
                - create/edit/delete User
                - create/edit/delete Permission
                - add/remove permission to user
            """)
        with cols[1]:
            st.markdown("---")
            st.markdown("##### Weather data")
            st.markdown("""
                - populate table WEATHER_DATA with historitical data from weatherstack.com (15 years of data from
                        20/07/2008 to 31/05/2023)
                - update WEATHER_DATA with data from weatherstack.com (from last date referenced in WEATHER_DATA
                        to today)
                - compute forecast for specific city and insert results into table FORECAST_DATA
                - empty table WEATHER_DATA
                - empty table FORECAST_DATA
            """)
        with cols[2]:
            st.markdown("---")
            st.markdown("##### Machine Learning Model")
            st.markdown("""
                - launch training of the model with a specific set of parameters
                - launch evaluation of the model
                - launch several training of the model with different sets of parameters
                - retrain the model with most recent data
            """)

        cols = st.columns(3)
        with cols[0]:
            st.markdown("---")
            st.markdown("##### Administrators")
            st.markdown("""
                - get API logs
                - get SQL database info (host, user)
            """)
            st.markdown("##### Authentication")
            st.markdown("""
                - get authentication token
                - get info about authenticated user
            """)
        with cols[1]:
            st.markdown("---")
            st.markdown("##### End user")
            st.markdown("""
                - get forecast data for a city from table FORECAST_DATA
                - get historical on a period from table WEATHER_DATA
            """)
            st.markdown("##### Default")
            st.markdown("""
                - get welcome message
            """)

        st.markdown("---")
        st.markdown("## Characteristics")
        st.markdown("""
                    - Bearer token based authentication (token must be injected in http headers to authenticate)
                    - uses **OAuth2PasswordRequestForm** to get data from user
                    - data validation with pydantic
                    """)

        st.markdown("## Testing")
        st.markdown("""
                    - Endpoints tested with pytest
                    - launched
                      - automatically on every change on Pull Requests
                      - manually on branch develop (usually a pull request merged)
                    """)

        st.markdown("## Components interactions")
        st.image(images_path + 'principles_schema.jpg', channels="RGB", output_format="JPEG", width=1200)

    if choice == page_infrastruct:
        col1, col2, col3 = st.columns([0.5, 8, 0.5])
        with col2:
            st.title('Context')
            st.markdown("""---""")
            st.write(""" In order to provide an architecture that meets the needs of the solution, our team decided
                     to move towards a code-based solution (IaC) so that we could quickly and efficiently rebuild the
                     architecture.
                     \nOn the other hand, although our entire application operates as a dockerised microservice, we
                     refused to use the tools offered by AWS for the easy deployment and orchestration of containers:
                     ECR, ECS, EKS, and so on.
                     \nThe aim is to be able to create the whole of our architecture ourselves, so that we are the only
                     masters of it.
                     \nThe target architecture vision considers the orchestration of dockers by Kubernetes. And the MVP
                     version only considers docker management at the mesh level via docker-compose.
                     \nAll the IaC is available on our project repository on Github""")

        st.markdown("""---""")
        col1, col2, col3 = st.columns([0.5, 8, 0.5])
        with col2:
            st.title('Network Architecture')
            st.markdown("""---""")
            st.write(""" In order to ensure some security, we decided to divide our infrastructure boundary (VPC)
                     into two sub-areas: Public and Private subnets and to maximise service availability and
                     redundancy, our architecture is designed symmetrically, with two availability zones: eu-west-3a,
                     eu-west-3b.
                     \nThe public subnet hosts the frontend, allowing users to identify themselves to the API and then
                     access the various weather predictions.
                     \n
                     \nThe private subnet hosts the following services:
                     \n- API
                     \n- MLflow
                     \n- Airflow
                     \n- Nginx
                     \nThese services are made up of different sub-services, explained below (e.g. Airflow requires
                     several services to function correctly).
                     \n
                     \nFor the datalake service, an S3 bucket is attached to the VPC in order to store:
                     \n- API logs
                     \n- MLflow artefacts (description follows)
                     \nThe use of this S3 bucket requires the creation of an endpoint and the association of the
                     necessary and sufficient rights to the machines communicating with it.
                     \n
                     \nIn order to communicate with the outside world, we are integrating an Internet Gateway
                     into our VPC.
                     \n
                     \nTo communicate with each other, the private and public sub-networks need a Network Address
                     Translator (NAT). We also incorporate NATs into the public sub-networks.
                     \n
                     \nFinally, to enable the Internet Gateway - Public Subnet - Private Subnet to communicate with each
                     other, we set up routing tables and associated routes.
                     \n
                     \n The frontend is also used as a bastion host, to manage access to the backend. Like this external
                     network can't access to the critical data and API. The access to the backend is garantee
                     with the ssh key.
                     """)
            with st.expander("Within the description, here a visualization of the Network architecture:"):
                col1, col2, col3 = st.columns([0.5, 2, 0.5])
                with col2:
                    st.image(images_path + 'network.jpg',
                             channels="RGB", output_format="auto", use_column_width='auto')
                    st.image(images_path + 'bastion.jpg',
                             channels="RGB", output_format="auto", use_column_width='auto')
        st.markdown("""---""")

        col1, col2, col3 = st.columns([0.5, 8, 0.5])
        with col2:
            st.title('EC2 Architecture')
            st.markdown("""---""")
            st.write("""The networks part has now been validated. Now it's time to design the virtual machine
                     infrastructure, to launch them and to balance requests.
                     \n
                     \nIn order to make our infrastructure resilient, it must be able to prevent the need to
                     increase the number of machines available per subnetwork. Indeed, in the event of a surge
                     in load, to protect VMs, we need to be able to horizontally scaling the number of machines.
                     \n
                     \nTo achieve this, we defined two entities to manage machine configuration and launch:
                     \n- Autoscaling launch configuration - a configuration instance for EC2 launches
                     \n- Autoscaling launch group - An instance for increasing the number of machines if some of
                     them are deleted, or if our infrastructure is scaling up.
                     \n
                     \nThese two entities are defined at the VM level, which itself is defined according to its
                     subnetwork. So we'll have a configuration instance and launcher for public VMs, and a
                     configuration instance and launcher for private VMs.
                     \n
                     \nAs far as configuration is concerned, we rely on customized AMIs, integrating all the
                     software required for operation (Docker, Docker-compose, Git) as well as the necessary
                     credentials: SSH key for Github, AWS keys etc. Please note that the AMIs at the base of
                     VMs on the public subnet do not have sensitive credentials, precisely because of their
                     exposure to the Internet. AWS credentials are therefore reserved for the AMI Backend.
                     \nOn the other hand, launchers allow you to switch from 1 VM per subnet to 1 VM per availability
                     zone.
                     \n
                     \nAs our architecture is divided according to availability zones, and each subnetwork can
                     increase its number of EC2 machines if need be, we need to set up tools to listen to requests
                     and balance them.
                     \nTo do this, we use :
                     \n- LoadBalancer: to measure and balance requests
                     \n- A Listener: combines with a LoadBalancer to define the listening port on the one hand, and
                     the group of machines to be redirected on the other.
                     \n- A Target Group: groups together the destination machines for requests listened to by the
                     listenee and balanced by LoadBalancer. It can also be used to define the destination port for
                     requests.
                     \n
                     \nAs with the scaling group, these three entities are defined at the VM level, which in turn is
                     defined at the subnetwork level. So we'll have two sets of these instances, one for public VMs
                     and another for private VMs.""")
            with st.expander("""
                             Within the description, here is a visualization or the Network architecture +
                             the EC2 architecture:
                             """):
                col1, col2, col3 = st.columns([0.5, 2, 0.5])
                with col2:
                    st.image(images_path + 'architecture_ec2.jpg',
                             channels="RGB", output_format="auto", use_column_width='auto')
                st.markdown("""---""")

        col1, col2, col3 = st.columns([0.5, 8, 0.5])
        with col2:
            st.title('EC2 Microservices')
            st.markdown("""---""")
            st.write("""Now it's time to talk about the services implemented to meet our project.
                     \n
                     \n Functional objective:
                     \n - In order to best handle the monitoring and re-training of models and their selection
                     for forecasting, we need an MLflow service. MLflow is an open-source Machine Learning project
                     lifecycle management platform that enables data scientists to track, manage, reproduce and
                     deploy models in a collaborative and organized way.
                     \n - In order to centralize functionalities, our application needs an API
                     \n - In order to call up the core functionalities of our application: data update and forecasting,
                     an Airflow service is required. Airflow is a workflow programming, scheduling and monitoring
                     platform that enables developers to create and manage complex workflows in an automated and
                     reproducible way.
                     \n - A Nginx server (reverse Proxy), to redirect access to the microservices, adding a security
                     layer.
                     \n - An external MySQL db to fetch all the weather data (Weather historical data & forecasts).
                     \n Also, our application will contain 4 large sets of functionality. Nevertheless, some of these
                     functionalities are composed of several detailed services.
                     \n MLflow Tracking:
                     \n - In order to manage relational entities (runs, metrics, params, tags) an SQL database
                     is required. PostreSQL is chosen and will be docked.
                     \n - To retrieve artifacts (images, models, config) we decide to use our S3 bucket.
                     \n - To access our resources, an MLflow server is required.
                     \n - The MLflow client is the API itself
                     \n""")
            st.markdown("""---""")
            with st.expander("""
                             Within the description, here a description of the functionnal aspect of
                             MLflow Tracking:"""):
                col1, col2, col3 = st.columns([0.5, 2, 0.5])
                with col2:
                    st.image(images_path + 'MLflow_tracking.png',
                             channels="RGB", output_format="auto", use_column_width='auto')
            st.markdown("""---""")
            st.write("""
                     \n Airflow:
                     \n - Like MLflow, a PostreSQL database is used to manage all the relational data from
                     the runs.
                     \n - In order to access the service, an MLflow server is implemented
                     \n - Two Celery workers are set up, one service per worker, to execute the DAGs. A Celery worker
                     is a process
                     that executes parallel and asynchronous tasks, using the Celery library to efficiently distribute
                     and manage the execution of tasks on one or more nodes in a cluster, enabling workflows to be
                     scaled and accelerated.
                     \n - To go with these workers, we created the scheduleur service. Airflow Scheduler is an
                     Apache Airflow component responsible for scheduling and executing tasks according to their
                     dependencies and specified order.
                     \n - A Redis database is also used for caching data. A Redis backend for Airflow is an in-memory
                     database storage system that enables efficient management of states, queued jobs and execution
                     metadata in Airflow, improving the performance and scalability of the workflow management system.
                     \n - In order to initiate the PostgreSQL database, Airflow uses a specific service - Init_db
                     \n - In order to visualise the completion of tasks, a Flower service has been implemented.
                     Airflow Flower is an open-source tool that allows you to view and monitor the execution of
                     tasks in Apache Airflow.
                     \n""")
            with st.expander("Within the description, here a description of the functionnal aspect of Airflow:"):
                col1, col2, col3 = st.columns([0.5, 2, 0.5])
                with col2:
                    st.image(images_path + 'Airflow.png',
                             channels="RGB", output_format="auto", use_column_width='auto')
            st.markdown("""---""")
        col1, col2, col3 = st.columns([0.5, 8, 0.5])
        with col2:
            st.write("""Now, we can illustrate all the architecture, all together""")
            with st.expander("Within the description, here a description of the functionnal aspect of Airflow:"):
                col1, col2, col3 = st.columns([0.5, 2, 0.5])
                with col2:
                    st.image(images_path + 'architecture_microservice.jpg',
                             channels="RGB", output_format="auto", use_column_width='auto')
        st.markdown("""---""")

    if choice == page_model_tracking:
        col1, col2, col3 = st.columns([0.5, 8, 0.5])
        with col2:
            st.title('Context')
            st.markdown("""---""")
            st.write(""" In order to track the model, it is mandatory.
                     \n - To have update data .
                     \n - To check its metrics regulary.
                     \n - To retrain it if necessary.
                     \n
                     \nTo be able to achieve it, Airflow, Mlfow and tha API are used. Airflow will launch automtic task,
                     Mlflow will manage the model tracking and the roots of the API are used. Two DAGs are define :
                     \nFirst one to update data and forecast weather for the users each 3 hours.
                     \nSecond one which evaluate the model and retain it if necessary once a day.""")

        col1, col2, col3 = st.columns([0.5, 8, 0.5])
        with col2:
            st.image(images_path + 'airflow_dags.jpg',
                     channels="RGB", output_format="auto", use_column_width='auto')
        st.markdown("""---""")

        col1, col2, col3 = st.columns([0.5, 8, 0.5])
        with col2:
            st.title('Update data, forecast weather')
            st.markdown("""---""")
            st.write(""" To have updated data, Airflow and the API are used.
                     \nAirflow to have a DAG which will get the API root to have the token to access the API.
                      And token are saved in Variable to be used be next task.
                     \n
                     \nOnce done, two tasks are launch in the same time, once to update data with the weatherstack api,
                     and the other to delete user forecast data.
                     \nTo finish forecast weather is done on all cities in the same time, during this step two tables of
                      the DB are fullfill, WEATHER_DATA and FORECAST_DATA.""")

        col1, col2, col3 = st.columns([0.5, 8, 0.5])
        with col2:
            st.image(images_path + 'airflow_fetch_data.jpg',
                     channels="RGB", output_format="auto", use_column_width='auto')
        st.markdown("""---""")

        col1, col2, col3 = st.columns([0.5, 8, 0.5])
        with col2:
            st.title('Model evaluation')
            st.markdown("""---""")
            st.write("""As to update data, the first task is to get the token.
                     After the evaluation is done. If success two metrics are push to the next step,
                     the meansquared error of temperature and precipitation, which are the two important metrics
                     for this application.
                     \nIf temperature mse is higher than 5 or precipitation mse is higher than 0.1 the model is
                     retrained with all data.
                     \nAll evaluation, retrain are track by mlflow, with specific model name, and a backup is also
                     done on DB in the table MODEL_DATA.
                     """)
            col1, col2, col3 = st.columns([0.5, 2, 0.5])
            with col2:
                st.image(images_path + 'airflow_evaluation.jpg',
                         channels="RGB", output_format="auto", use_column_width='auto')
        st.markdown("""---""")

        col1, col2, col3 = st.columns([0.5, 8, 0.5])
        with col2:
            st.title('Views of Mlflow tracking')
            st.markdown("""---""")
            st.write("""As explain all data can be managed by Mlflow to compare model
                     """)
            st.markdown("""---""")
        st.write("""
                      Here a view of the functionnal aspect of MLflow Tracking:""")
        col1, col2, col3 = st.columns([0.5, 8, 0.5])
        with col2:
            st.image(images_path + 'MLflow_table.jpg',
                     channels="RGB", output_format="auto", use_column_width='auto')
        st.write("""
                      \nHere a view of charts aspect of MLflow Tracking:""")
        col1, col2, col3 = st.columns([0.5, 8, 0.5])
        with col2:
            st.image(images_path + 'MLflow_chart1.jpg',
                     channels="RGB", output_format="auto", use_column_width='auto')
        col1, col2, col3 = st.columns([0.5, 8, 0.5])
        with col2:
            st.image(images_path + 'MLflow_chart2.jpg',
                     channels="RGB", output_format="auto", use_column_width='auto')
        st.write("""
                 Some filters can be used to have a clear view:""")
        col1, col2, col3 = st.columns([0.5, 8, 0.5])
        with col2:
            st.image(images_path + 'MLflow_filter.jpg',
                     channels="RGB", output_format="auto", use_column_width='auto')
        st.markdown("""---""")

    if choice == page_transformers:
        col1, col2, col3 = st.columns([0.5, 8, 0.5])
        with col2:
            st.title('Context')
            st.markdown("""---""")
            st.write("""
                     The origin of Transformers in the field of natural language processing (NLP) can be
                     traced back to the groundbreaking research paper titled "Attention Is All You Need,"
                     published by Vaswani et al. in 2017. Before Transformers, NLP models predominantly
                     relied on recurrent neural networks (RNNs) and convolutional neural networks (CNNs),
                     which had limitations in handling long-range dependencies in sequential data, like sentences.
                     \nThe Transformer architecture revolutionized NLP by introducing the attention mechanism,
                     a mechanism that allows the model to focus on different parts of the input sequence to
                     understand context. Unlike RNNs, which process words sequentially, Transformers can process
                     all words in the input sentence simultaneously, making it highly parallelizable and
                     significantly speeding up training and inference.
                     \nAt the core of the Transformer is the self-attention mechanism. It calculates attention
                     weights for each word in the input sequence based on its relationship with other words in
                     the sequence. By attending to relevant words, the model can learn rich contextual representations,
                     capturing long-range dependencies and understanding the nuances of language.
                     \nThe Transformer consists of an encoder-decoder structure. The encoder processes the input and
                     produces a fixed-length representation, while the decoder generates the output based on this
                     representation. Transformers can be adapted for various NLP tasks through pre-training
                     and fine-tuning. Pre-training involves training the model on large unlabeled text corpora,
                     enabling it to learn general language patterns and semantics. Fine-tuning follows, where
                     the pre-trained model is adapted to specific tasks with smaller labeled datasets.
                     \nThe success of Transformers led to the development of various models, such as BERT (Bidirectional
                     Encoder Representations from Transformers), GPT (Generative Pre-trained Transformer), and XLNet,
                     each excelling in different NLP applications. These models have become the foundation of many
                     state-of-the-art NLP systems, propelling the field forward and enabling more accurate and
                     contextually aware language understanding and generation.
                     \n
                     \n
                     \n#### Attention Mechanism
                     \nThe attention mechanism in Transformers allows the model to weigh the importance of different
                     elements in the input sequence while processing each element. This mechanism is essential
                     for capturing long-range dependencies and understanding the context of a word in relation
                     to other words in the sequence.
                     \n
                     \n#### Scaled Dot Product Attention
                     \nScaled Dot Product Attention is a key component of the attention mechanism in Transformers.
                     Given a query vector, a set of key vectors, and a set of value vectors, it calculates the
                     attention weights by computing the dot product between the query vector and the key vectors.
                     The resulting dot products are then scaled by the square root of the dimension of the key
                     vectors to prevent large values that can cause instability during training. Next, the scaled
                     dot products are passed through a softmax function to obtain the attention weights, representing
                     the importance of each key-value pair for the query.
                     \n
                     \nMathematically, for a query vector Q, a set of key vectors K, and a set of value vectors V,
                     the scaled dot product attention is calculated as follows:
                     """)
            st.latex(r"""
                     \text{{Attention}}(Q, K, V) = \text{{softmax}}\left(\frac{{Q \cdot K^T}}{{\sqrt{{d_k}}}}\right)
                     \cdot V
                     """)
            st.write("""
                     \n
                     \nHere, $d_k$ is the dimension of the key vectors. The resulting attention weights are then used
                     to compute a weighted sum of the value vectors, producing the final output of the attention layer.
                     \n#### Multi-Head Attention
                     \nWhile the scaled dot product attention is powerful, the Transformer employs multi-head
                     attention to capture different types of information. In multi-head attention, the attention
                     mechanism is performed multiple times in parallel, each time with different learned linear
                     projections of the query, key, and value vectors. This allows the model to focus on different
                     aspects of the input simultaneously and learn diverse representations.
                     \nThe outputs of the multiple attention heads are concatenated and linearly transformed to
                     produce the final output of the multi-head attention layer. The model learns to attend to
                     various parts of the input sequence, enabling it to capture complex patterns and relationships
                     effectively.
                     \nBy combining scaled dot product attention and multi-head attention, Transformers can efficiently
                     process sequential data, like natural language, and have demonstrated remarkable performance
                     in a wide range of NLP tasks, making them one of the most influential breakthroughs in the field
                     of deep learning and natural language processing.
                     \n
                     \n
                     \nSince their explosion in LLMs, transformers are beginning to be put to a wider range
                     of uses. For example, in our case, we use algorithms based on Transformers and their
                     attention mechanism to process time series.
                     \nThis technology offers unprecedented advantages, positioning it as the future of AI:
                     \n- Unlike its predecessors (RNN, LSTM...), transformers have a theoretically infinite
                     window of vision. Also, we are not limited in the amount of data we can process over
                     time (training & prediction).
                     \n- The attention mechanism is accessible through attention matrices. This addresses one of the key
                     issues in the use of deap-learning algorithms: interpretability. Indeed, it is possible
                     to understand, analyze and visualize the importance of data in predicting results. """)
            with st.expander("Here's the description of the Transformer architecture as described "
                             "in 'Attention is all you need' - Ashish and all 2017 :"):
                col1, col2, col3, col4 = st.columns([0.5, 3, 3, 0.5])
                with col2:
                    st.image(images_path + 'Transformers_1.png',
                             channels="RGB", output_format="auto", use_column_width='auto')
                with col3:
                    st.image(images_path + 'Transformers_2.png',
                             channels="RGB", output_format="auto", use_column_width='auto')
            st.markdown("""---""")

        col1, col2, col3 = st.columns([0.5, 8, 0.5])
        with col2:
            st.title('PatchTST')
            st.markdown("""---""")
            st.write("""Following on from the democratization of Transformer algorithms,
                     the time series field is now capable of proposing new ways of processing data.
                     \nThe article studied and on which the algorithm is based is the following:
                     A time serie is worth 64 words : Long term forecasting with Transformers - 2023
                     \n
                     \nThis sections doesn't aims to provid anf full and exhautive explanation of
                     the algorithm (Please refer to the article for this), but aims to gives
                     the main characteristics and advantages of its use.
                     \n
                     \nThis algorithm proposes an independent multi-variable analysis.
                     Two key principles underpin this algorithm:
                     \n- **Patching :** time-series forecasting aims to understand the correlation between data at each
                     different time step. However, a single time step does not have the same semantic meaning
                     as a word in a sentence,
                     so extracting local semantic information is essential for analyzing their connections.
                     Most previous work uses only point
                     input tokens, or simply hand-crafted information from series. In contrast, we
                     improve locality and capture complete semantic
                     information that is not available at the point level by aggregating time steps
                     into patches at the sub-series level.' - A time serie
                     is worth 64 words : Long term forecasting with Transformers - 2023
                     \n- **Channel-independence :** a multivariate time series is a multi-channel signal, and each
                     Trans- former input token can be represented
                     by data from either a single channel or multiple channels. Depending on the design of input
                     tokens, different variants of the Transformer
                     architecture have been proposed. Channel-mixing refers to the latter case where the input
                     token takes the vec- tor of all time series
                     features and projects it to the embedding space to mix information. On the other hand,
                     channel-independence means that each input token
                     only contains information from a single channel' - A time serie is worth 64 words :
                     Long term forecasting with Transformers - 2023.
                     \n
                     \nThis algorithm offers many advantages:
                     \n- A very large window of data consideration
                     \n- Applicability of masked encoding
                     \n- Reduced computation time thanks to patching ( Without patching: quadratic complexity
                     in N^2. With patching, N=L/S,
                     which reduces quadratic complexity)
                     \n- Improved learning thanks to self-supervised learning: 'Self-supervised representation
                     learning has become a popular
                     approach to extract high-level abstract representation from unlabelled data. In this section,
                     we apply PatchTST to obtain
                     useful represen- tation of the multivariate time series. We will show that the learnt
                     representation can be effectively
                     transferred to forecasting tasks.Among popular methods to learn representation via self-supervise
                     pre-training, masked
                     autoencoder has been applied successfully to NLP. This technique is conceptually simple: a portion
                     of input sequence is
                     intentionally removed at random and the model is trained to recover the missing contents.Masked
                     encoder
                     has been recently
                     employed in time series and delivered notable performance on classification and regression tasks.'
                     \n
                     \nIn this paper, the authors propose an algorithm which aims to forecast
                     data by applying Transformer algorythm to multi
                     variate data. They share the same Transformer backbone, but the forward
                     processes are independent. And other way to
                     understand it : The analysis and the training is independant for every
                     signal, but the weights are common and thus,
                     dependance is create between signals during the forecast.
                     \n This is highlighted by the authors :
                     \n >"*We emphasize that each time series will have its own latent representation that
                     are cross-learned via a shared weight mechanism. This design can allow
                     the pre-training data to contain different number of
                     time series than the downstream data, which may not be feasible by other
                     approaches.*"
                     \n
                     \nIn the case of the self_supervised mechanism, each channel univariate
                     series is passed through instance normalization
                     operator and segmented into patches. These patches are used as Transformer
                     input tokens. Masked self-supervised representation
                     learning with PatchTST where patches are randomly selected and set to zero.
                     The model will reconstruct the masked patches.
                     \n The Patch are designed with à Stride to avoid overlaping patches for the
                     self-supervised algorithm (otherwise, owing to
                     overlapping patches, the algorithm could 'cheat' to acces masked values)
                     """)
            with st.expander("Here the descripotion of the PatchTST algorithm:"):
                col1, col2, col3, col4 = st.columns([0.5, 3, 3, 0.5])
                with col2:
                    st.image(images_path + 'Transformers_PatchTST.png',
                             channels="RGB", output_format="auto", use_column_width='auto')
            st.markdown("""---""")


if __name__ == '__main__':
    main()

tools.display_side_bar()
