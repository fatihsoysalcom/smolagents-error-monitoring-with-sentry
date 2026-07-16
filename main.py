import os
import random
import time
import logging
import asyncio # Required for async operations

# Import smolagents components
# Note: smolagents is an external library. Install with 'pip install smolagents'.
try:
    from smolagents import Agent, AgentContext, Message
except ImportError:
    print("Smolagents library not found. Please install with 'pip install smolagents'.")
    print("This example requires smolagents to run.")
    exit(1) # Exit if smolagents is not available

# Sentry SDK is an external dependency. Install with 'pip install sentry-sdk'.
try:
    import sentry_sdk
    from sentry_sdk.integrations.logging import LoggingIntegration
except ImportError:
    sentry_sdk = None
    LoggingIntegration = None
    print("Sentry SDK not found. Please install with 'pip install sentry-sdk'.")
    print("Errors will be printed to console but not sent to Sentry.")

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- Sentry Initialization ---
SENTRY_DSN = os.getenv("SENTRY_DSN")

if SENTRY_DSN and sentry_sdk:
    sentry_logging = LoggingIntegration(
        level=logging.INFO,        # Capture info and above as breadcrumbs
        event_level=logging.ERROR  # Send errors and above as events
    )
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[sentry_logging],
        traces_sample_rate=1.0, # Adjust as needed for production
        environment="development",
        release="smolagents-example@1.0.0"
    )
    logger.info("Sentry initialized successfully.")
else:
    logger.warning("SENTRY_DSN not set or Sentry SDK not installed. Sentry error monitoring will be disabled.")


# --- Smolagents Agent Definition ---
class DataProcessorAgent(Agent):
    """
    A smolagent that processes data, sometimes introducing an error.
    This simulates the kind of unexpected bug discussed in the article.
    """
    async def handle_message(self, context: AgentContext, message: Message):
        logger.info(f"Agent '{self.name}' received message: {message.content}")

        try:
            data = message.content
            if not isinstance(data, dict) or "value" not in data:
                raise ValueError("Invalid data format: 'value' key missing or not a dict.")

            value = data["value"]

            # Simulate a processing delay
            await asyncio.sleep(0.1)

            # --- Intentional Bug: This block simulates an unexpected error ---
            # The article talks about surprising bugs. This is one such scenario.
            if random.random() < 0.4:  # 40% chance of hitting the bug path
                logger.warning(f"Simulating a bug for value: {value}")
                if value == 0:
                    # This will cause a ZeroDivisionError
                    result = 100 / value
                elif isinstance(value, str):
                    # This will cause a TypeError
                    result = value + 10
                else:
                    # Another potential error path
                    raise RuntimeError("Unexpected processing error for value: " + str(value))
            else:
                # Normal processing path
                result = value * 2
                logger.info(f"Successfully processed value: {value}, result: {result}")

            # In a real smolagents setup, agents might send messages to other agents.
            # For this demo, we'll just log the "response".
            # await context.send_message(
            #     recipient=message.sender,
            #     content={"original_value": value, "processed_result": result}
            # )

        except Exception as e:
            logger.error(f"Agent '{self.name}' encountered an error: {e}", exc_info=True)
            # Sentry's logging integration (configured above) will automatically capture
            # errors logged at ERROR level or higher.
            # If Sentry SDK is initialized, this error will be sent to Sentry.
            if sentry_sdk:
                # Optionally, explicitly capture the exception if not relying solely on logging integration
                sentry_sdk.capture_exception(e)
            # await context.send_message(
            #     recipient=message.sender,
            #     content={"error": str(e), "status": "failed"}
            # )


async def main():
    logger.info("Starting smolagents Sentry example.")

    # Create an instance of our agent
    processor_agent = DataProcessorAgent(name="ProcessorAgent")

    # Simulate sending messages to the agent
    # These messages are designed to sometimes trigger the intentional bug.
    test_data = [
        {"value": 5},
        {"value": 10},
        {"value": 0},          # Potential ZeroDivisionError
        {"value": "text"},     # Potential TypeError
        {"value": 20},
        {"value": 7},
        {"value": 0},
        {"value": 15},
        {"value": "another_text"},
        {"value": 30},
        {"value": 1},          # Another value to hit RuntimeError path
        {"value": 2}
    ]

    for i, data in enumerate(test_data):
        logger.info(f"\n--- Sending message {i+1} with data: {data} ---")
        # For this simple demo, we'll directly call handle_message with a mock context.
        # In a real smolagents application, a MessageBus would facilitate communication.
        mock_context = AgentContext(agent=processor_agent, message_bus=None)
        mock_message = Message(sender="User", recipient=processor_agent.name, content=data)
        await processor_agent.handle_message(mock_context, mock_message)
        await asyncio.sleep(0.5) # Small delay between messages

    logger.info("\nSmolagents Sentry example finished.")

    # Flush Sentry events before exiting to ensure they are sent.
    if sentry_sdk:
        logger.info("Flushing Sentry events...")
        sentry_sdk.flush()
        logger.info("Sentry events flushed.")

if __name__ == "__main__":
    asyncio.run(main())
