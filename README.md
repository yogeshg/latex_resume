

Setup
-----

```bash
    brew cask install mactex
    pip install -r requirements.txt
    git clone https://github.com/yogeshg/markdown2latex.git
    cd markdown2latex
    git checkout ce9938f74ab3e28a3cf53adff794438ccbad66df
    python setup.py install
    cd -
```


Commands
--------

```bash
    docker build -t texume:ubuntu-18.04 .
    docker run -it -p 80:80 -v $PWD/src:/src -v $PWD/texume:/texume -v /tmp/logs/:/tmp/logs texume:ubuntu-18.04
    docker run -it -p 80:80 -v $PWD/src:/src -v $PWD/texume:/texume -v /tmp/logs/:/tmp/logs texume:ubuntu-18.04 python manage.py test editor.models
```

