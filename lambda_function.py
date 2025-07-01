import os
import json
import boto3
import requests
import psycopg2

def get_bluesky_token(username, password):
    url = "https://bsky.social/xrpc/com.atproto.server.createSession"
    payload = {
        "identifier": username,
        "password": password
    }

    response = requests.post(url, json=payload, timeout=10)
    response.raise_for_status()
    return response.json()["accessJwt"]

def lambda_handler(event, context):
    print("Logging into Bluesky...")

    username = os.environ.get("BLUESKY_USERNAME")
    password = os.environ.get("BLUESKY_PASSWORD")

    if not username or not password:
        raise Exception("Bluesky credentials not set in environment variables.")

    try:
        token = get_bluesky_token(username, password)
        print("Authenticated.")
    except Exception as e:
        print(f"Error during authentication: {e}")
        raise

    # Fetch feed using pagination
    print("Fetching Bluesky timeline with pagination...")
    headers = {"Authorization": f"Bearer {token}"}
    all_posts = []
    cursor = None
    MAX_POSTS = 500

    try:
        while len(all_posts) < MAX_POSTS:
            url = "https://bsky.social/xrpc/app.bsky.feed.getTimeline?limit=30"
            if cursor:
                url += f"&cursor={cursor}"

            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()

            feed = data.get("feed", [])
            all_posts.extend(feed)

            print(f"Fetched {len(feed)} posts (Total: {len(all_posts)})")

            cursor = data.get("cursor")
            if not cursor or not feed:
                print("No more pages to fetch.")
                break

        post_count = len(all_posts)
        print(f"Retrieved {post_count} posts in total.")
    except Exception as e:
        print(f"Failed to fetch posts: {e}")
        raise

    # Upload to S3
    print("Uploading to S3...")
    try:
        s3 = boto3.client("s3")
        s3.put_object(
            Bucket="bluesky-raw-posts-parvathi",
            Key="raw/bluesky_posts.json",
            Body=json.dumps(all_posts),
            ContentType="application/json"
        )
        print("Upload successful.")
    except Exception as e:
        print(f"Failed to upload to S3: {e}")
        raise

    
        # Run sentiment inference
    try:
        runtime = boto3.client("sagemaker-runtime")
        endpoint_name = "bluesky-sentiment-endpoint"

        predictions = []
        for entry in all_posts:
            try:
                post = entry.get("post", {})
                record = post.get("record", {})

                if isinstance(record, dict):
                    text = record.get("text", "").strip()
                    if text:
                        payload = {"inputs": text}
                        response = runtime.invoke_endpoint(
                        EndpointName=endpoint_name,
                        ContentType="application/json",
                        Body=json.dumps(payload)
                         )
                        result = json.loads(response["Body"].read())

                    # Expecting result like: [{"label": "positive", "score": 0.843}]
                        if isinstance(result, list) and len(result) > 0 and "label" in result[0]:
                            predictions.append({
                            "text": text,
                            "sentiment": result[0]["label"].lower(),
                            "confidence_score": result[0]["confidence"]

                            })
                        else:
                            predictions.append({
                            "text": text,
                            "sentiment": "unknown",
                            "confidence_score": None
                             })
            except Exception as post_err:
                print(f"Skipped one post due to: {post_err}")

        print(f"Inference complete. {len(predictions)} predictions made.")

        s3.put_object(
            Bucket="bluesky-raw-posts-parvathi",
            Key="predictions/bluesky_predictions.json",
            Body=json.dumps(predictions),
            ContentType="application/json"
            )
        print("Predictions saved to S3.")

    except Exception as e:
        print(f"Failed during inference or saving predictions: {e}")



    # Insert into RDS
    db_host = os.environ["DB_HOST"]
    db_name = os.environ["DB_NAME"]
    db_user = os.environ["DB_USER"]
    db_pass = os.environ["DB_PASSWORD"]

    try:
        conn = psycopg2.connect(
        host=db_host,
        dbname=db_name,
        user=db_user,
        password=db_pass
        )
        cursor = conn.cursor()

        for item in predictions:
            text = item["text"]
            sentiment = item["sentiment"].strip().lower()
            confidence_score = item.get("confidence_score", None)  # safely extract score
            # 🔍 Log each prediction before storing
            print(f"Post: {text[:80]}... → {sentiment} ({confidence_score})")
            cursor.execute(
            """
            INSERT INTO posts (post_text, sentiment, confidence_score)
            VALUES (%s, %s, %s)
            """,
            (text, sentiment, confidence_score)
            )

        conn.commit()
        cursor.close()
        conn.close()
        print("Predictions inserted into RDS.")

    except Exception as e:
        print(f"Failed to insert into RDS: {e}")

    return {
        "status": "done",
        "post_count": post_count,
        "predictions": len(predictions)
         }

