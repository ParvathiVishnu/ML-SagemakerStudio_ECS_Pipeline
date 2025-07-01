🔷 Bluesky Sentiment Analysis Pipeline on AWS

This project implements a serverless data pipeline that fetches social media posts from the Bluesky API, performs sentiment analysis using a machine learning model deployed on Amazon SageMaker, and stores the results in Amazon RDS for visualization via a Streamlit dashboard hosted on Amazon ECS Fargate.

![Architecture Diagram](Architecture.png)

⚙️ End-to-End Architecture Workflow

1. Data Collection
A Lambda function is triggered every 5 minutes using Amazon EventBridge.
It fetches fresh posts from the Bluesky API.

2. Data Storage
The raw JSON data fetched from the API is stored in an Amazon S3 bucket for archival and reproducibility.

![S3 bucket](Images/bluesky_bucket-1.png)
![S3 bucket](Images/bluesky_bucket-3.png)

4. Sentiment Analysis
The same Lambda function invokes a SageMaker endpoint that analyses sentiments on the posts fetched by the lambda function and train a model and save it in the form of tar.gz format .
The endpoint returns predicted sentiment labels (Positive, Neutral, Negative) along with the confidence_score for each post.

![Amazon Sagemaker Studio](Images/Amazon_Sagemaker_Studio_Lab.png)
![S3 bucket](Images/bluesky_bucket-2.png)

6. Database Storage
The predicted sentiment results, along with the original post content, are stored in an Amazon RDS PostgreSQL database.

![RDS](Images/RDS.png)
![pg_admin](Images/pgadmin.png)


8. Dashboard Visualization
A Streamlit dashboard queries the RDS database for sentiment data.
The dashboard is containerized using Docker and deployed on ECS Fargate via Amazon ECR.
The dashboard runs on port 8051 and provides real-time sentiment insights.

![RDS](Images/ECR.png)
![RDS](Images/ECS.png)


