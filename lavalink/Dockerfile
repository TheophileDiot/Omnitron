# FROM arm64v8/openjdk:17.0-slim-buster
FROM openjdk:17-alpine

WORKDIR /opt/Lavalink

# temporary workaround for youtube search
# COPY Lavalink.jar Lavalink.jar
COPY 2277cf-Lavalink.jar Lavalink.jar
COPY application.yml application.yml

EXPOSE 2333

CMD ["java", "-jar", "Lavalink.jar"]
