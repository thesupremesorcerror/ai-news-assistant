# Service B - Core API (Spring Boot)
# Stage 1: build the jar with Maven
FROM maven:3.9-eclipse-temurin-17 AS build

WORKDIR /app

# Cache dependencies separately from source so code changes don't
# force a full re-download.
COPY pom.xml .
RUN mvn dependency:go-offline -B

COPY src ./src
RUN mvn clean package -DskipTests -B

# Stage 2: slim runtime image
FROM eclipse-temurin:17-jre

WORKDIR /app
COPY --from=build /app/target/*.jar app.jar

EXPOSE 8080

ENTRYPOINT ["java", "-jar", "app.jar"]
