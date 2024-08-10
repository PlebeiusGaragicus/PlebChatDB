# PlebChatDB


## Ensure MongoDB is running

```sh
# run MongoDB
mongod --replSet "rs0" --dbpath /usr/local/var/mongodb

```


## Run this project
```sh
# run the database API
# uvicorn src.app:app --reload --port 5101
sh run.sh
```


## Run the admin panel
```sh
# run the admin panel
streamlit run admin_panel.py --server.port=5252
```
