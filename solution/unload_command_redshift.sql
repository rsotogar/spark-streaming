unload ('select * from admin_mysql.user_group')
to 's3://zizoo-dwh/redshift_serverless/copy_data/user_group/'
iam_role 'arn:aws:iam::847534572340:role/Redshift_S3FullAccess'
csv
header
delimiter ','
ALLOWOVERWRITE