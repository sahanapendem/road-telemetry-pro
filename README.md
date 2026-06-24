# Clone the repository:

git clone [https://github.com/sahanaoendem/road-telemetry-pro.git](https://github.com/sahanaoendem/road-telemetry-pro.git)
cd road-telemetry-pro


# Install dependencies:

pip install -r requirements.txt


# Run the app locally:

python -m streamlit run app.py
# Configuration & Webhook Testing

Go to Webhook.site to receive your private, unique endpoint URL.

Under the Notification Hub Configurations tab in the app, toggle on "Forward JSON Payload to Slack Webhook" and paste your unique URL.

Deploy the live feed and trigger a camera alert, or click "Trigger Test Webhook Alert" to watch the formatted JSON hit your dashboard instantly.
