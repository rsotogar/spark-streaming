select saga_characters , label ,  count(*) as top_1_times
from seedtag.kafka_streams ks
where top_5 = 1
group by 1, 2
order by 3 desc

-- muestra que personajes han aparecido mas veces como top 1 entidad en todos los rangos de tiempo
