# Disclaimer
This project is built on [Big Data Europe - Hadoop in Docker](https://github.com/big-data-europe/docker-hadoop).

# Getting started
1. Clone the repository
2. Install the Python requirements
    ```shell
    pip install
    ```
3. Build Hadock images
    ```shell
    python hadock.py install
    ```
4. Setup config
    ```shell
    python hadock.py setup $HADOOP_DIST_HOME
    ```
   > $HADOOP_DIST_HOME is generally located in $HADOOP_REPOSITORY/hadoop-dist/target/hadoop-$VERSION
                                                                    
5. Run Hadock                                                                                   
    ```shell
    python hadock.py run
    ```



