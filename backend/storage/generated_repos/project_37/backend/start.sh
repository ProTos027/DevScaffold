#!/bin/bash

# Ensure Maven is installed and Java is set up
if ! command -v mvn &> /dev/null
then
    echo "Maven is not installed. Please install Maven to proceed."
    exit 1
fi

if ! command -v java &> /dev/null
then
    echo "Java is not installed. Please install JDK 17 or higher to proceed."
    exit 1
fi

echo "Building the Spring Boot application..."
mvn clean install -DskipTests

if [ $? -ne 0 ]; then
    echo "Build failed. Exiting."
    exit 1
fi

JAR_FILE=$(find target -name "*.jar" -print -quit)

if [ -z "$JAR_FILE" ]; then
    echo "No executable JAR file found in the 'target' directory."
    exit 1
fi

echo "Starting the Spring Boot application: $JAR_FILE"
java -jar "$JAR_FILE"
