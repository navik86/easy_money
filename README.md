## Launching the project
- ```git clone https://github.com/navik86/easy_money.git```
- ```mv .env.example .env```
- ```docker compose up -d --build```
- ```docker compose exec app python manage.py migrate --noinput```

---

## Get endpoints 
- ```http://127.0.0.1:8000/swagger/```


![Alt text](endpoints.jpg?raw=true "Optional Title")