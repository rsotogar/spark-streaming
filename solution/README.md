My proposal as a solution to the problem is to use Spark streaming as a parallel processing framework, the Apache Apark module that allows
the processing of events in "real time" (the real latency is approx 1s,
but for this use case it is more than enough). I have chosen Spark for several reasons:

1. #### Scalability. 

A Spark cluster can be configured to process a high volume
of data (terabytes) just by adding more nodes and reconfiguring the memory tuning, number of executors, etc., with which we will not have any scalability problem.

2. #### Integration with Kafka via Structured Streaming.

The introduction of Spark 2.4 brought significant improvements to structured data processing with the DataFrame API and the Structured Streaming module, which allows events ingested in real time to be treated as if they were rows of an infinite dataframe.
Much of the batch processing functionality is retained in Structured Streaming.

3. #### Integration with SQL and NoSQL databases, and data lakes.

Although Spark is designed to go hand in hand with a data lake due to its ability to process a high volume of data, it can also interact
with SQL (MySQL, Postgres) and NoSQL (MongoDB, Cassandra) databases.


To expose the data I have chosen MySQL because I have a local server that allows me to test the functionality
of the pipeline. In a production environment I would choose a columnar format database, such as Redshift or BigQuey, since
which are more efficient for data analysis.


# Workflow description (MacOS)

1. #### Iinstall local MySQL server
```brew install mysql```

2. #### Create the "seedtag" database from any SQL client or the command line (I use DBeaver)

3. #### Define the "kafka streams" table using the following DLL:
```CREATE TABLE `kafka_streams` (
  `window_start` timestamp NULL DEFAULT NULL,
  `window_end` timestamp NULL DEFAULT NULL,
  `label` varchar(255) DEFAULT NULL,
  `saga_characters` varchar(255) DEFAULT NULL,
  `total_views_per_character` int DEFAULT NULL,
  `top_5` int DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;```

4. #### Install Hadoop and Spark locally
````xcode-select --install````
````brew cask install java````
````brew install scala````
````brew install apache-spark````

Open the terminal and execute the following commands  ````spark-shell````or  ````pyspark```` which allows us to launch interactive Spark queries from Scala or Python, respectively. If the shell opens, we have completed the installation.

5. #### Submit Spark job with ````spark-submit````

To launch a job in streaming we only have to provide the Maven coordinates of the driver package that
enables the connection to the Kafka cluster and the MySQL driver. First we make sure that we have started the Kafka containers and the streaming service, as indicated in the instructions of the task.
Important: in local mode the driver and executor processes of the Spark app share the driver memory, that's why I raise it to 3g (just in case).
We enter the directory where the app.py is.

````cd your_working_directory````

And execute the spark-submit command:

````spark-submit --conf spark.driver.memory=3g --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.1.1,mysql:mysql-connector-java:8.0.16 app.py````


To monitor the process, we see how messages about the duration of each batch appear in the terminal, or we can refresh the MySQL table and we will see the data appear.
I am attaching several queries and a screenshot of DBeaver to demonstrate that it does work.


In summary, this is a solution to process streaming data with Spark by reading from a Kafka topic and using a database
MySQL data as a data sink for visualization and analysis. These types of solutions are very common in big data due to their ability to
scale to high volumes of data and its simplicity for development and deployment.






