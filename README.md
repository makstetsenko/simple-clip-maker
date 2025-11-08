# Usage

### Setup venv

```bash
python3 -m venv venv
```

```bash
source venv/bin/activate
```

```bash
python -m pip install -r ./requirements.txt
```

### basic usage

```bash
python main.py -i "input" -r "1280x720" -f 30
```

### build plot with beats markers (where clips suppose to be changed)

```bash
python main.py -i "input" -p
```

### store sub clips used to build result video

```bash
python main.py --save-timeline-clips -i "input" -r "1280x720" -f 25
```

or

```bash
python main.py -st "input" -r "1280x720" -f 25
```
