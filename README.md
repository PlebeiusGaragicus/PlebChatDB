# PlebChatDB


## run locally

```sh
# run MongoDB
mongod --replSet "rs0" --dbpath /usr/local/var/mongodb

# run the database API
uvicorn src.app:app --reload --port 5101

# run the admin panel
streamlit run admin_panel.py --server.port=5252
```
