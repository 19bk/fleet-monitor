FROM python:3.11-slim

WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir -e .[viz,ml]

EXPOSE 8501

CMD ["sh", "-c", "python scripts/seed_history.py && streamlit run src/fleet_monitor/dashboard/app.py --server.address=0.0.0.0 --server.port=8501"]

