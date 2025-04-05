-- public.local_users определение

-- Drop table

-- DROP TABLE public.local_users;

CREATE TABLE if not exists public.local_users (
	id serial4 NOT NULL,
	keycloak_id varchar(36) NOT NULL,
	username varchar(64) NULL,
	email varchar(120) NULL,
	last_active timestamp NULL,
	refresh_token varchar(2000) NULL,
	access_token varchar(2000) NULL,
	CONSTRAINT local_users_keycloak_id_key UNIQUE (keycloak_id),
	CONSTRAINT local_users_pkey PRIMARY KEY (id)
);