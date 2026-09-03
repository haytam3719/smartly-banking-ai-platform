FROM maven:3.9.9-eclipse-temurin-21 AS build
WORKDIR /workspace
COPY pom.xml .
RUN mvn -B -DskipTests dependency:go-offline
COPY src src
RUN mvn -B -DskipTests package
FROM eclipse-temurin:21-jre
RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*
RUN useradd --system --uid 10001 mobilebff
WORKDIR /app
COPY --from=build /workspace/target/mobile-bff-*.jar app.jar
USER mobilebff
EXPOSE 8080
ENTRYPOINT ["java","-jar","/app/app.jar"]
