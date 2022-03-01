# Postgresql basis # 

Postgres docs.

## Comandos útiles ##


* CREATE POSTGRES USER FOR CONNECTION

    ```SQL
    CREATE USER montessoread_local PASSWORD 'mOnt3sS0_r34D*local';
    ```

* GRANT MANAGEMENT TO CREATE ROLE (Amazon RDS required)

    ```SQL
    GRANT montessoread_local TO postgres;
    ```


* POSTGRESQL DATABASE CREATION UTF8

    ```SQL
    CREATE DATABASE "montessoread_local" WITH OWNER "montessoread_local" ENCODING 'UTF8' LC_COLLATE = 'en_US.UTF8' LC_CTYPE = 'en_US.UTF8' TEMPLATE template0;
    ```

* DELETE USER

    ```SQL
    DROP USER user_name;
    ```

* ASSIGN ALL PERMISSIONS TO A USER ON AN EXISTING DATABASE

    ```SQL
    GRANT ALL PRIVILEGES ON DATABASE db_name TO user_name;
    ```

* MANAGING DATABASE BACKUPS/RESTORE

    ```bash
    #!/bin/bash
    pg_dump -Fc database_name > file_name.dump
    pg_restore -d database_name file_name.dump
    ```

### PSQL remote connection

psql -U postgres -h triduum-postgres.ctizan5nidqm.us-east-2.rds.amazonaws.com

### pg_dump

/usr/lib/postgresql/11/bin/pg_dump -Fc -d montessoread_local -U postgres -h triduum-postgres.ctizan5nidqm.us-east-2.rds.amazonaws.com > dump.dump

### pg_restore

/usr/lib/postgresql/11/bin/pg_restore -d montessoread_dev montessoread_local.dump -U postgres -h triduum-postgres.ctizan5nidqm.us-east-2.rds.amazonaws.com