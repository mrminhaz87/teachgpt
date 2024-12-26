install node from: [Node JS Installation](https://deb.nodesource.com/)

```bash
sudo apt update

sudo apt-get install -y libcairo2-dev pkg-config python3-dev libpango1.0-dev libpangocairo-1.0-0 python3-gi nodejs python3-gi-cairo python3-cairo ffmpeg

conda create -n manim2 python=3.10 manim cairo -c conda-forge

pip install fastapi "fastapi[standard]" curl_cffi tzlocal

fastapi dev text_api.py
```




```bash
npm i
npm run dev
```

change following things:
- cookie in .env
- python environment location
- region in claude_api