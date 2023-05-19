FROM python:3.10.8-alpine

WORKDIR /app/kap-disclosures

RUN mkdir logs

RUN addgroup -S kap-app && adduser -S kap-disc-user -G kap-app

COPY requirements.txt ./

ENV PATH /home/kap-disc-user/.local/bin:${PATH}

RUN pip install --no-cache-dir -r ./requirements.txt

COPY . .

RUN chown -R kap-disc-user:kap-app /app/kap-disclosures

USER kap-disc-user

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "3002"]