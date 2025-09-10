# Usage

### Setup venv

```bash
python3 -m venv venv
```

```bash
source venv/bin/activate
```

### basic usage

```bash
python main.py -m "input/*.mp3" -v "input/*.mp4,input/*.m4v,input/*.mov"
```

### build plot with beats markers (where clips suppose to be changed)

```bash
python main.py -m "input/*.mp3" -p
```

### store sub clips used to build result video

```bash
python main.py --store-sub-clips -m "input/*.mp3" -v "input/*.mp4,input/*.m4v,input/*.mov"
```
