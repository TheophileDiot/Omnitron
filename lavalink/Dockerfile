# FROM arm64v8/openjdk:17.0-slim-buster
FROM openjdk:17-alpine

WORKDIR /opt/Lavalink

# temporary workaround for youtube search
COPY Lavalink.jar /opt/Lavalink/Lavalink.jar
COPY application.yml /opt/Lavalink/application.yml

EXPOSE 2333

CMD ["java", "-jar", "/opt/Lavalink/Lavalink.jar"]
