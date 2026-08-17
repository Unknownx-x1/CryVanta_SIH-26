For end-to-end Testing:

```bash

python -m unittest test.py test_decision.py test_actuation.py
python -m py_compile risk_engine.py decision_engine.py actuation.py schemas.py mqtt_client.py main.py

```


All working usable APIs

``` bash
/health
/state
/telemetry
/potency
/forecast
```


To run everything:

``` bash

pip install -r requirements.txt

python -m uvicorn main:app --reload

```


For Docs:

```bash
http://127.0.0.1:8000/docs
```