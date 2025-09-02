
[Gender Recognition Certificate service](../README.md) >
[Developer documentation](README.md) >
Hosting and live databases

# Hosting and live databases

* To access the live databases you will need to follow step one and two from the [cloud platform documentation]("https://user-guide.cloud-platform.service.justice.gov.uk/documentation/other-topics/rds-external-access.html#accessing-your-rds-database"). This will port forward the live database to your local machine.


* You can retrieve database credentials from kubernetes secrets under `dps-rds-instance-output`


* You can then access the database using psql or a UI such as PGAdmin using these credentials:
  --host localhost \
  --port 5432 \
  --dbname [your database name] \
  --username [your database username] \
  --password [your database password]


* After you can delete the port forward `kubectl delete pod port-forward-pod -n [your namespace]`
