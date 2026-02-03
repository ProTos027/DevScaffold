#!/bin/bash

# Ensure Java is installed
if ! command -v java &> /dev/null
then
    echo "Java is not installed. Please install Java 17 or higher."
    exit 1
fi

# Ensure Maven is installed
if ! command -v mvn &> /dev/null
then
    echo "Maven is not installed. Please install Maven 3.6 or higher."
    exit 1
fi

echo "Building the project..."
mvn clean install

if [ $? -ne 0 ]; then
    echo "Maven build failed. Exiting."
    exit 1
fi

echo "Running the Spring Boot application..."
java -jar target/url-shortener-0.0.1-SNAPSHOT.jar
