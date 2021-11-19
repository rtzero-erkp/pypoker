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
python client_web.py

# server
python service_poker_custom.py
#python service_poker_long.py
#python service_poker_short.py

# agent
pip install websocket-client
python ws_agent.py
