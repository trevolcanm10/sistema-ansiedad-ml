# Usa una imagen base con Maven y JDK 17 para compilar
FROM maven:3.8.4-openjdk-17-slim AS build
WORKDIR /app

# Copia el archivo de configuración de Maven y descarga dependencias
COPY pom.xml .
RUN mvn dependency:go-offline

# Copia el código fuente y compila
COPY src ./src
RUN mvn package -DskipTests

# Segunda etapa: imagen más pequeña solo con el JAR y JRE
FROM openjdk:17-jdk-slim
WORKDIR /app
COPY --from=build /app/target/*.jar app.jar

# Expone el puerto que usa Spring Boot (8080)
EXPOSE 8080

# Comando para ejecutar la aplicación
ENTRYPOINT ["java", "-jar", "app.jar"]