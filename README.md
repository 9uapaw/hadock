# Disclaimer
This project is built on [Big Data Europe - Hadoop in Docker](https://github.com/big-data-europe/docker-hadoop).

# Getting started
1. Clone the repository

2. Go to the project's main directory and set up a python virtualenv: 
    ```shell
    python3 -m venv ./venv
    ```

3. Activate the virtualenv: 
    ```shell
    source venv/bin/activate
    ```

4. Install all the dependencies into the virtualenv: 
    ```shell
    python3 -m ensurepip --default-pip
    python3 -m pip install -r requirements.txt
    ```

5. Build Hadock images
    ```shell
    python3 hadock.py install
    ```
6. Setup config
    ```shell
    python3 hadock.py setup $HADOOP_DIST_HOME
    ```
   > $HADOOP_DIST_HOME is generally located in $HADOOP_REPOSITORY/hadoop-dist/target/hadoop-$VERSION
                                                                    
7. Run Hadock                                                                                   
    ```shell
    python3 hadock.py run
    ```
