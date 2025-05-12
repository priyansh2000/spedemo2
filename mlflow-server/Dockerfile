FROM python:3.10

RUN pip install mlflow boto3

EXPOSE 5001

ENTRYPOINT ["mlflow", "server", "--host", "0.0.0.0", "--port", "5001", "--backend-store-uri", "sqlite:///mlflow.db", "--default-artifact-root", "/mlflow/artifacts"]
