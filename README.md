## My Curriculum Vitae
[![Build Status](https://app.travis-ci.com/stevenliuyi/cv.svg?branch=master)](https://app.travis-ci.com/stevenliuyi/cv)

This repository contains the source code that I use to automatically generate my curriculum vitae (CV) [PDF file](cv.pdf) from a YAML file.

The CV is based on the LaTeX template from [zachscrivena/simple-resume-cv](https://github.com/zachscrivena/simple-resume-cv). [`generate.py`](generate.py) is a Python script that reads data from [`cv.yml`](cv.yml) and then generates the corresponding CV. Outside of this repo, `cv.yml` is also used in [stevenliuyi/my-website](https://github.com/stevenliuyi/my-website) to generate the HTML version of my CV at https://yliu.io/resume.

This repository is mostly inspired by [bamos/cv](https://github.com/bamos/cv).

### Usage

Generate CV PDF file using Latexmk (default choice):

```
python generate.py
```

Use [Tectonic](https://tectonic-typesetting.github.io) instead of Latexmk to compile the file:

```
python generate.py --tectonic
```

Change the secondary text color of the file (default is black, which is the same as the primary text color):

```
python generate.py --color 0d8aba
```

List all available arguments:

```
python generate.py --help
```
