select saga_characters, sum(total_views_per_character) as sum_total_mentions
from seedtag.kafka_streams ks 
group by 1
order by 2 desc;

-- el numero de menciones totales por personaje en todos los rangos de tiempo