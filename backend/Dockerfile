FROM python:3.12-slim
WORKDIR /maple
COPY backend/requirements.txt /maple/backend/requirements.txt
RUN pip install --no-cache-dir -r /maple/backend/requirements.txt
COPY backend/app /maple/backend/app
COPY data/raw_inputs /maple/data/raw_inputs
COPY data/pm_knowledge /maple/data/pm_knowledge
WORKDIR /maple/backend
ENV PYTHONPATH=/maple/backend
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
