unload ('select * from archive.zizoo_analytics')
to 's3://zizoo-dwh/redshift-archive/zizoo_analytics/data'
iam_role 'arn:aws:iam::847534572340:role/Redshift_S3FullAccess'
csv
header
delimiter ','
ALLOWOVERWRITE
PARALLEL off

-- parallel on makes each slice in the cluster write its allocated data to s3. Setting it to off will write to one or more files according to maxfilesize.