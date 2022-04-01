FROM arm64v8/openjdk:17.0-slim-buster
# FROM openjdk:17-alpine # for amd64 CPU

WORKDIR /opt/Lavalink

COPY Lavalink.jar Lavalink.jar
COPY application.yml application.yml

EXPOSE 2333

CMD ["java", "-jar", "Lavalink.jar"]
