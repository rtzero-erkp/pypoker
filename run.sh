# env
conda create -n texas_web python=3.8.5
conda activate texas_web
pip install -r requirements.txt

pip list
pip uninstall -y Werkzeug # 降级
pip install Werkzeug==1.0.0
pip install Werkzeug==1.0.1
# pip install Werkzeug==1.0.2

# client
export FLASK_APP=client_web.py
flask run --host=0.0.0.0 --port=5000
python client_web.py

# server
python texasholdem_poker_service.py

# test
export FLASK_APP=test/test_ws_server.py
export FLASK_APP=test/test_ws_server2.py
flask run --host=0.0.0.0 --port=5000
python test/test_ws_server.py
python test/test_ws_server2.py

pip install websocket-client
python test/test_ws_client.py
