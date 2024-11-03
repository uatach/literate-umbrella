# literate-umbrella

## Intro

Simple guitar soft synth written in Python, based on [Real Python tutorial](https://realpython.com/python-guitar-synthesizer/).


## Current major differences from tutorial

- No project management using `poetry`
- Several boilerplate classes are not used
- Use of `PyAudio` to directly play sounds instead of writing files with `pedalboard`
- Use of `click` to build the CLI instead of `argparse`


## Running the code

Make sure to have PyAudio and PortAudio installed (see install istructions at <https://people.csail.mit.edu/hubert/pyaudio/>).

Then, after setting up your Python environment:
```bash
pip install -r requirements.txt
```

Finally, run the CLI tool to display help and list of commands:
```bash
python src/cli.py
```


## Reproducing the tutorial


### Step 2

To reproduce the sound sequence generated at the end of step 2, run:

```bash
python src/cli.py play-sequence
```


### Step 3

To reproduce the blending of multiple notes:

```bash
python src/cli.py play-chord --delay 0
```

To add 40 milliseconds of delay between notes:

```bash
python src/cli.py play-chord --delay 0.04
```

To reverse the strumming direction:

```bash
python src/cli.py play-chord --delay 0.04 --reverse true
```


### Step 4

To generate the sequence of pitches from the beginning of the step:

```bash
python src/cli.py play-pitches
```

To generate the sequence of notes:

```bash
python src/cli.py play-notes
```

To generate the sounds of the 3 instruments:

```bash
python src/cli.py play-instruments
```


### Step 5

To generate the chorus of Jason Mraz's "I'm Yours":

```bash
python src/cli.py play-chorus
```


### Step 6

To generate the chorus of Jason Mraz's "I'm Yours" with special effects:

```bash
python src/cli.py play-chorus --effects true
```


## repo stats

Language|files|blank|comment|code
:-------|-------:|-------:|-------:|-------:
Python|4|125|1|481
YAML|2|0|0|200
Markdown|1|43|0|61
Text|1|0|0|6
--------|--------|--------|--------|--------
SUM:|8|168|1|748
