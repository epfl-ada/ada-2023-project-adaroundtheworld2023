<a name="readme-top"></a>

# Getting Started

This readme is for creating the virtual environment and downloading the data (for team members).

## Dependencies

Use the Pypi package manager to set up the environment.

```bash
python3.9 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt
```

## Data Extraction

We've set up convenient extraction scripts for linux based systems. For all the others, you can simply follow
the link attached at the end of the paragraph.

### Raw Data

For Linux users:

```bash
sudo chmod +x scripts/extract-data.sh && ./scripts/extract-data.sh
```

Otherwise you can just use this 
[link](https://drive.google.com/file/d/1PjfwmkkRfuZohk9vpbWSFpmOnOm2DQpz/view?usp=sharing) 
and extract it to `data/raw`.

### Graph Data

In order to download the preprocessed data for graphs (classification, embeddings, 
similarities, graphs), use the script below. Notice that it may take up to an hour:

```bash
sudo chmod +x scripts/extract-graph-data.sh && ./scripts/extract-graph-data.sh
```

Alternatively, you can just use the 
[link](TODO: update) 
to download and extract the data to the current directory.

<p align="right">(<a href="#readme-top">back to top</a>)</p>
