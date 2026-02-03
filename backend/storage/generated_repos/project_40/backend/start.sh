#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

echo "Building the Spring Boot application..."
mvn clean package -DskipTests

if [ $? -ne 0 ]; then
    echo "Maven build failed. Exiting."
    exit 1
fi

JAR_FILE=$(find target -name "*.jar" ! -name "*-sources.jar" ! -name "*-javadoc.jar")

if [ -z "$JAR_FILE" ]; then
    echo "No JAR file found in target directory. Exiting."
    exit 1
fi

echo "Starting the Spring Boot application: $JAR_FILE"
java -jar "$JAR_FILE"
