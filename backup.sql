BEGIN TRANSACTION;
CREATE TABLE material (
	id INTEGER NOT NULL, 
	nombre VARCHAR NOT NULL, 
	tipo VARCHAR, 
	activo BOOLEAN NOT NULL, 
	PRIMARY KEY (id)
);
INSERT INTO "material" VALUES(1,'Vogue','Tradicional',1);
INSERT INTO "material" VALUES(2,'Fnails','Semipermanente',1);
INSERT INTO "material" VALUES(3,'Jolie nails','Semipermanente',1);
INSERT INTO "material" VALUES(4,'Admmis','Tradicional',1);
CREATE TABLE resena (
	id INTEGER NOT NULL, 
	calificacion INTEGER NOT NULL, 
	comentario VARCHAR NOT NULL, 
	fecha_creacion DATE NOT NULL, 
	activo BOOLEAN NOT NULL, 
	spa_id INTEGER, 
	usuario_id INTEGER, 
	PRIMARY KEY (id), 
	FOREIGN KEY(spa_id) REFERENCES spa (id), 
	FOREIGN KEY(usuario_id) REFERENCES usuario (id)
);
INSERT INTO "resena" VALUES(1,5,'string','2025-10-21',0,1,1);
INSERT INTO "resena" VALUES(2,5,'tienen buena atencion, y gran calidad de servicio','2025-10-21',1,1,2);
INSERT INTO "resena" VALUES(3,3,'string','2025-10-21',1,2,1);
INSERT INTO "resena" VALUES(4,4,'string','2025-10-21',1,2,2);
INSERT INTO "resena" VALUES(5,4,'string','2025-10-23',0,4,2);
CREATE TABLE servicio (
	id INTEGER NOT NULL, 
	nombre VARCHAR NOT NULL, 
	descripcion VARCHAR, 
	duracion_ref VARCHAR, 
	precio_ref FLOAT, 
	activo BOOLEAN NOT NULL, 
	PRIMARY KEY (id)
);
INSERT INTO "servicio" VALUES(1,'Manicure Tradicional','Limpieza, corte, limado, empuje de cutículas y esmalte tradicional.','45-60 minutos',15000.0,1);
INSERT INTO "servicio" VALUES(2,'Pedicure Tradicional','Baño de pies, limpieza, corte de uñas, limado, exfoliación ligera, masaje, esmalte tradicional.','45-60 minutos',20000.0,1);
INSERT INTO "servicio" VALUES(3,'Manicure Semipermanente / Gel Polish','Limpieza, corte, limado, empuje de cutículas, pulido y esmalte que se fija bajo lámpara LED/UV; más duración.','60-70 minutos',40000.0,1);
INSERT INTO "servicio" VALUES(4,'Pedicure semipermanente','Baño de pies, limpieza, corte de uñas, limado, exfoliación ligera, masaje, esmalte que se fija bajo lámpara LED/UV; más duración.','60-70 minutos',50000.0,1);
INSERT INTO "servicio" VALUES(5,'Retiro semipermanente','Quitar el esmalte semipermanente, remojar, limar si es necesario, limpiar uñas para aplicar otro servicio.','10-20 minutos',10000.0,1);
CREATE TABLE spa (
	id INTEGER NOT NULL, 
	nombre VARCHAR NOT NULL, 
	direccion VARCHAR NOT NULL, 
	zona VARCHAR NOT NULL, 
	horario VARCHAR, 
	calificacion_promedio FLOAT NOT NULL, 
	activo BOOLEAN NOT NULL, 
	ultima_actualizacion DATE, 
	desactualizado BOOLEAN NOT NULL, 
	admin_spa_id INTEGER, 
	PRIMARY KEY (id), 
	FOREIGN KEY(admin_spa_id) REFERENCES usuario (id)
);
INSERT INTO "spa" VALUES(1,'Sala de Belleza GALES','Calle 16f #100-65a','Fontibon, Laguna','Lunes- Domingo, De 7am - 8pm',4.0,1,'2025-10-22',0,NULL);
INSERT INTO "spa" VALUES(2,'MATIZ sala de belleza','Calle 16f #103-18a','Fontibon, Laguna','Lunes a Domingo, De 8am - 7pm',3.5,1,'2025-10-22',0,NULL);
INSERT INTO "spa" VALUES(3,'STUDIO la profe','Calle 16f #103b-33a','Fontibon, Laguna','Lunes a Domingo, De 9am - 8pm',0.0,1,'2025-10-22',0,NULL);
INSERT INTO "spa" VALUES(4,'string','string','string','string',0.0,1,'2025-10-23',0,NULL);
CREATE TABLE spamaterial (
	spa_id INTEGER NOT NULL, 
	material_id INTEGER NOT NULL, 
	activo BOOLEAN NOT NULL, 
	PRIMARY KEY (spa_id, material_id), 
	FOREIGN KEY(spa_id) REFERENCES spa (id), 
	FOREIGN KEY(material_id) REFERENCES material (id)
);
INSERT INTO "spamaterial" VALUES(1,1,1);
INSERT INTO "spamaterial" VALUES(1,2,1);
INSERT INTO "spamaterial" VALUES(1,3,1);
INSERT INTO "spamaterial" VALUES(1,4,1);
INSERT INTO "spamaterial" VALUES(2,4,1);
INSERT INTO "spamaterial" VALUES(2,2,1);
INSERT INTO "spamaterial" VALUES(3,1,1);
INSERT INTO "spamaterial" VALUES(3,2,1);
CREATE TABLE spaservicio (
	id INTEGER NOT NULL, 
	spa_id INTEGER, 
	servicio_id INTEGER, 
	precio FLOAT, 
	duracion VARCHAR, 
	activo BOOLEAN NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(spa_id) REFERENCES spa (id), 
	FOREIGN KEY(servicio_id) REFERENCES servicio (id)
);
INSERT INTO "spaservicio" VALUES(1,1,1,10.0,'40-60 min',1);
INSERT INTO "spaservicio" VALUES(2,1,2,15000.0,'40-50 minutos',1);
INSERT INTO "spaservicio" VALUES(3,1,3,35000.0,'40-50 minutos',1);
INSERT INTO "spaservicio" VALUES(4,1,4,55000.0,'40-50 minutos',1);
INSERT INTO "spaservicio" VALUES(5,2,4,45000.0,'40-50 minutos',1);
INSERT INTO "spaservicio" VALUES(6,1,5,10000.0,'10-20 minutos',1);
INSERT INTO "spaservicio" VALUES(7,2,5,12000.0,'10-20 minutos',1);
INSERT INTO "spaservicio" VALUES(8,3,5,15000.0,'10-20 minutos',1);
CREATE TABLE usuario (
	id INTEGER NOT NULL, 
	nombre VARCHAR NOT NULL, 
	correo VARCHAR NOT NULL, 
	contrasena VARCHAR NOT NULL, 
	rol VARCHAR NOT NULL, 
	activo BOOLEAN NOT NULL, 
	PRIMARY KEY (id)
);
INSERT INTO "usuario" VALUES(1,'Nicole','nicole@admin.com','$2b$12$9x8//3rji6EobujbKiY3.OZRlXakZDJslpM9qUIiUZto0EI.Phiu2','admin_principal',1);
INSERT INTO "usuario" VALUES(2,'oscar','oscar@example.com','$2b$12$wkEG9r.bUkUceK3f2Ronf.1tCeL7GoHtfTjatTkyRX1UyYrU7mghO','usuario',1);
INSERT INTO "usuario" VALUES(3,'andres','andres@admin.com','$2b$12$/8gjyIvK94YVoQFAB98FqO6Cpti25Ta15ojF5fHocJu3ADvNdOyDe','usuario',1);
COMMIT;
