# Smolagents Error Monitoring with Sentry

This example demonstrates how to integrate Sentry for error monitoring within a `smolagents` application. It sets up a simple `smolagent` that processes data, intentionally introducing a bug that causes various exceptions. Sentry is configured to capture these errors, illustrating how it helps track unexpected issues in lightweight agent-based systems.

## Language

`python`

## How to Run

1. Install dependencies: `pip install smolagents sentry-sdk`
2. Set your Sentry DSN: `export SENTRY_DSN="YOUR_SENTRY_DSN_HERE"` (replace with your actual DSN)
3. Run the script: `python main.py`

## Original Article

This example accompanies the Turkish article: [Smolagents Bug'ını Sentry ile Nasıl Çözdüm: Herkesi Şaşırtan Hatayı Avlama Rehberi](https://fatihsoysal.com/blog/smolagents-bugini-sentry-ile-nasil-cozdum-herkesi-sasirtan-hatayi-avlama-rehberi/).

## License

MIT — see [LICENSE](LICENSE).
