Mi propuesta como solución al problema es usar Spark streaming como framework de procesamiento en paralelo, el módulo de Apache Apark que permite 
el procesamiento de eventos en "tiempo real" (la latencia real es de 1s approx, 
pero para este caso de uso es más que suficiente). He elegido Spark por varios motivos:

1. #### Escalabilidad de la arquitectura. 

Un cluster de Spark puede configurarse para procesar un alto volumen
de datos (terabytes) tan solo añadiendo más nodos y reconfigurando el tuneo de memoria, numero de ejecutores, etc., con lo que no tendremos ningún problema de escalabilidad.

2. #### Integración con Kafka mediante Structured Streaming.

La introducción de Spark 2.4 trajo importantes mejoras al procesamiento de datos estructurados con la DataFrame API y el módulo Structured Streaming, que permite tratar a los eventos ingestados en tiempo real como si fueran filas de un dataframe infinito.
Gran parte de la funcionalidad de procesamiento en batch se conserva en Structured Streaming. 

3. #### Integración con multiples bases de datos SQL y NoSQL, data lakes.

Si bien Spark está pensado para ir de la mano de un data lake por su capacidad para procesar un elevado volumen de datos, también puede interaccionar
con bases de datos SQL (MySQL, Postgres) y NoSQL (MongoDB, Cassandra).


Para exponer los datos he elegido MySQL porque dispongo de un servidor local que me permite testar la funcionalidad
del pipeline. En un entorno de produccion eligiría una base de datos de formato columnar, como Redshift o BigQuey, puesto
que son mas eficientes para el análisis de datos.


# Description del proceso (en MacOS)

1. #### Instalar el servidor local de MySQL
```brew install mysql```

2. #### Crear la base de datos "seedtag" desde cualquier cliente de SQL o la linea de comandos (yo uso DBeaver)

3. #### Definir la tabla "kafka_streams" usando el siguiente DDL:
```CREATE TABLE `kafka_streams` (
  `window_start` timestamp NULL DEFAULT NULL,
  `window_end` timestamp NULL DEFAULT NULL,
  `label` varchar(255) DEFAULT NULL,
  `saga_characters` varchar(255) DEFAULT NULL,
  `total_views_per_character` int DEFAULT NULL,
  `top_5` int DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;```

4. #### Instalar Hadoop y Spark en modo local
````xcode-select --install````
````brew cask install java````
````brew install scala````
````brew install apache-spark````

Abrir la terminal y ejecutar el comando  ````spark-shell````o  ````pyspark```` que nos permite lanzar consulas interactivas en Spark desde Scala o Python, respectivamente. Si se abre la shell, hemos completado la instalación.

5. #### Lanzar el Spark job con ````spark-submit````

Para lanzar un job en streaming solo tenemos que proporcionar las coordenadas Maven del paquete del driver que
habilita la conexión al cluster de Kafka y al driver de MySQL. Primero nos aseguramos que hemos levantado los contenedores de Kafka y el streaming service, tal cual se indica en las instrucciones de la tarea.
Importante: en modo local los procesos driver y ejecutores de la app Spark comparten la memoria del driver, por eso la elevo a 3g (por si acaso).
Entramos en el directorio donde esta el app.py.

````cd your_working_directory````

Y ejecutamos el comando spark-submit:

````spark-submit --conf spark.driver.memory=3g --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.1.1,mysql:mysql-connector-java:8.0.16 app.py````


Para monitorizar el proceso, vemos como en la terminal aparecen mensajes sobre la duración de cada batch, o podemos ir refrescando la tabla de MySQL y veremos ir apareciendo los datos.
Adjunto varias consultas y una captura de pantalla de DBeaver para demostrar que sí funciona.


En resumen, esta es una solución para procesar datos en streaming con Spark leyendo desde un topic de Kafka y usando una base
de datos MySQL como data sink para visualización y análisis. Este tipo de soluciones son muy habituales en big data por su capacidad para
escalar a altos volumenes de datos y su simplicidad para el desarrollo y despliegue.






