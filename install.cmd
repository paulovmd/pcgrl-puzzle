python -m pip install --upgrade pip setuptools wheel
python -m pip install tqdm
python -m pip install --user --upgrade twine

python setup.py clean

python -m pip uninstall pcgrl

python -m pip install --upgrade pip setuptools wheel

pip install gym
pip install stable-baselines3==1.6.2
pip install sb3-contrib==1.6.2
pip install pygame==2.0.0 
pip install ipython
pip install opencv-python
pip install imageio
pip install pandas

python setup.py sdist bdist_wheel
python -m pip install dist/pcgrl-0.0.0.1-py3-none-any.whl

pip install -r requirements.txt

python setup.py bdist_wheel