🔷 Bluesky Sentiment Analysis Pipeline on AWS

This project implements a serverless data pipeline that fetches social media posts from the Bluesky API, performs sentiment analysis using a machine learning model deployed on Amazon SageMaker, and stores the results in Amazon RDS for visualization via a Streamlit dashboard hosted on Amazon ECS Fargate.

![Architecture Diagram](Architecture.png)

🚀 Architecture Overview

BlueskyAPI: Source of social media posts.

AWS Lambda: Scheduled via EventBridge every 5 minutes to:

Fetch raw data from the Bluesky API.

Store raw data in Amazon S3.

Invoke a SageMaker endpoint for sentiment analysis.

Store the sentiment results in Amazon RDS (PostgreSQL).

Amazon SageMaker Studio Lab: Trained ML model deployed as an endpoint to predict sentiments.

Amazon RDS (PostgreSQL): Stores structured sentiment data for analysis.

Amazon ECS Fargate: Hosts the Streamlit dashboard to visualize data.

Amazon ECR: Stores the Docker image for the dashboard.

Streamlit Dashboard: Accessible on port 8051, queries RDS to display sentiment trends.

