from pyspark.sql import SparkSession
import pyspark.sql.functions as f
from pyspark.sql.types import *
from pyspark.sql.window import Window
import requests
import json


@f.udf(returnType=StringType())
def classify_text(text):
    """
    :param text: el texto a clasificar
    :return: la etiqueta emitida tras la peticion POST.
    """
    to_classify = {"text": text}
    req = requests.Session()
    response = req.post(url="http://0.0.0.0:5000/predict", data=json.dumps(to_classify))
    return json.loads(response.text)["label"]


@f.udf(returnType=ArrayType(elementType=StringType()))
def get_all_characters(text, entities):
    """
    :param text: el texto del cual extraer los personajes
    :param entities: la lista entera de posibles personajes tal cual esta en entities.txt
    :return: todos los personajes del texto que se encuentran en entities.txt como un array de string.
    """
    characters = []
    for character in entities:
        if character in text:
            characters.append(character)
    return characters


def foreach_batch_function(df, epoch_id):
    """
    :param df: el batch de filas en streaming que seran procesadas conjuntamente.
    :param epoch_id: este parametro no se usa en la funcion.
    :return:
    """
    df = df.withColumn("top_5", f.row_number().over(window))  # aplicamos una funcion de ventana que rankea
    # los personajes segun cuantas veces ha aparecido en un intervalo de tiempo en la saga.
    df = df.filter(f.col("top_5") <= 5)  # seleccionamos el top 5 de personajes mas mencionados.

    df.write.mode("append").jdbc(
        # finalmente escribimos el resultado a la tabla seedtag.kafka_streams definida previamente.
        url='jdbc:mysql://localhost:3306/seedtag?useUnicode=true&useJDBCCompliantTimezoneShift=true&useLegacyDatetimeCode=false&serverTimezone=UTC',
        table="kafka_streams",
        properties={"user": "root", "password": "", "driver": "com.mysql.cj.jdbc.Driver"}
    )
    pass


def get_entities(path):
    df_entities = spark.read.text(path, lineSep="\n")
    entities = df_entities.select("value").collect()
    entities = [entity.value for entity in entities]
    return entities


schema = StructType([StructField("id", StringType(), True), StructField("time", IntegerType(), True),
                     StructField("readers", IntegerType(), True), StructField("text", StringType(), True)])

if __name__ == "__main__":

    entities_text = "/Users/ramonsotogarcia/PycharmProjects/codetest-data-engineer-v5/entities.txt"

    # creamos la spark session para poder acceder a la programacion de datos estructurados en Spark Streaming
    spark = SparkSession \
        .builder \
        .appName("APP") \
        .getOrCreate()
    spark.sparkContext.setLogLevel("WARN")

    # ventana que se usara mas tarde para rankear las filas
    window = Window().partitionBy("window_start", "window_end", "label").orderBy(f.desc("total_views_per_character"))

    # creamos el stream de datos indicando la fuente, en este caso de nuestro contenedor Kafka en el puerto 29092
    df = spark \
        .readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "localhost:29092") \
        .option("subscribe", "events") \
        .option("startingOffsets", "earliest") \
        .load()

    # usamos el metodo from_json para castear el campo values a struct type
    df = df.select(f.from_json(f.col("value").cast("string"), schema),
                   f.col("timestamp").cast(TimestampType()))

    # extraemos el campo texto del struct
    df = df.select(f.col("from_json(CAST(value AS STRING)).text").alias("text"),
                   f.col("from_json(CAST(value AS STRING)).id").alias("event_id"),
                   f.col("timestamp").alias("event_timestamp"))

    # aplicamos una udf para generar la llamada POST al contenedor que clasifica el texto en una de las 3 sagas
    df = df.withColumn("label", classify_text(f.col("text")))

    entities = get_entities(entities_text) # extraemos la fila de personajes del entities.txt y la pasamos como un array en una columna del spark dataframe
    df = df.withColumn("entities", f.array([f.lit(i) for i in entities]))

    # aplicamos una udf para obtener un array de personajes mencionados en cada texto
    # y acto seguido explotamos el array para poder contar el numero de personajes
    df = df.withColumn("characters", get_all_characters(f.col("text"), f.col("entities"))) \
        .withColumn("characters", f.explode_outer("characters")) \
        .drop("entities")

    # aplicamos la funcion de ventana para que procese los datos en ventanas de 5 mins
    df = df.withWatermark("event_timestamp", "10 minutes") \
        .groupBy(f.window("event_timestamp", "5 minute"), "label", "characters") \
        .agg(f.count("event_id").alias("total_views_per_character"))

    # extraemos el inicio y el final de cada ventana de tiempo para poder escribir a la base de datos
    df = df.withColumn("window_start", f.col("window.start")) \
        .withColumn("window_end", f.col("window.end")).drop("window")

    df = df.select("window_start", "window_end", "label", f.col("characters").alias("saga_characters"),
                   "total_views_per_character")

    # finalmente escribimos a la base de datos MySQL utilizando un foreachBatch que nos permite
    query = df.writeStream \
        .outputMode("append") \
        .foreachBatch(foreach_batch_function) \
        .trigger(processingTime="5 seconds") \
        .start()

    query.awaitTermination() # no termina a no ser que se produzca un error o sea interrumpida manualmente.
