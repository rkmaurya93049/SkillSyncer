import os


def configure_langsmith():
    api_key = os.getenv("LANGCHAIN_API_KEY")
    if not api_key:
        # Tracing is optional; do not fail application startup when it is unset.
        os.environ["LANGCHAIN_TRACING_V2"] = "false"
        return False

    os.environ["LANGCHAIN_API_KEY"] = api_key
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ.setdefault("LANGCHAIN_PROJECT", "resume-evaluator")
    return True
