<a name="readme-top"></a>

# Getting Started

This readme is for creating the virtual environment and downloading the data.

## Dependencies

Use the Pypi package manager to set up the environment.

```bash
python3.9 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt
```

## Data Extraction

If you're on Linux based system, you can use the bash script below to download and extract the training and testing data.

```bash
sudo chmod +x scripts/bash/extract-data.sh && ./scripts/extract-data.sh
```

Otherwise you can just use this 
[link](https://drive.google.com/file/d/1PjfwmkkRfuZohk9vpbWSFpmOnOm2DQpz/view?usp=sharing) 
and extract it to `data/raw`.   

<p align="right">(<a href="#readme-top">back to top</a>)</p>