### Overview

This ETL pipeline was built as part of a series of interviews for a senior data engineer role in which I had to build
a data system that would ingest, process and store real time events in Kafka.

I show an example of how such streaming workflow could be set up in a scalable, robust and easy-to-integrate manner. 
Structured Streaming is a module of Apache Spark that can ingest and process
a huge volume of incoming files in almost real time. It integrates seamlessly with real-time data ingestion platforms (Kafka, Kinesis) and it provides a bunch
of connectors for SQL and NoSQL databases (MySQL, Mongo), data lakes (S3, GCS, etc.), and data warehouses (Redshift, BigQuery).

This project requires Docker and Docker Compose installed on your local machine (the Docker images were specified for the M1 chip on Mac):

1) In the root directory, run ````docker-compose up````
2) Enter the listener container with ```docker-compose exec listener-service bash```
3) And run the python script to start seeing the messages as they are being published to the events topic in the Kafka container ````python3 kafka_consumer.py````

The messages published to the events topic in Kafka mimic real time messages that are constantly being generated as a result of our activity on websites and apps.
These messages are then buffered into the Kafka cluster waiting for a consumer that 'subscribes' to the topic. The consumer will get every single message
published into the topic it subscribed to so as long as the subscription remains active. If another consumer subscribes to the same topic, each consumer will get a copy of each message, therefore 
enabling one-to-one, one-to-many, many-to-one and many-to-many patterns.

If we decide to process the incoming messages as they are received by the Kafka cluster there are several stream processors available, such as Flink,
Dataflow, and Apache Spark. I chose this one because (besides being the one I use the most) the same programming model is applied to both batch
and streaming pipelines, therefore simplifying ETL pipeline creation and deployment. Spark Streaming can give almost real time data processing latencies (1s microbatches) but if real time processing is needed, 
it may not be your preferred choice. It also has a very simple API in Python and Scala, with a lot of documentation out there that allows us to virtually do any task on streaming data.




