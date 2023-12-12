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

### Embeddings

You can use the bash script below to download embeddings to `data/embeddings/plots/`. 
If no arguments are passed, the whole dataset will be downloaded. Alternatively, you can specify the 
decades and for example download the last two decades with:

```bash
sudo chmod +x scripts/extract-embeddings.sh && ./scripts/extract-embeddings.sh 2000 2010
```

Pay in mind that `2000` here refers to all movies for which: `2000` <= release year < `2010`.

If you're unable to do that, you can just use the 
[link](https://drive.google.com/drive/folders/1o_djQ3ayUZuIcYKkerORfPodijbEKIXK?usp=drive_link) 
and download the data to `data/embeddings/plots/`.

### Similarities

Similarities follow exactly the same structure as embeddings in terms of decades, but they are extracted to
`data/embeddings/similarities/`. Keys denote the id-s of the movie pairs. The command for downloading the whole
data is:

```bash
sudo chmod +x scripts/extract-similarities.sh && ./scripts/extract-similarities.sh
```

If you're unable to do that, you can just use the 
[link](https://drive.google.com/drive/folders/17H5Z-x1Qm3B2qsCtp-vvufHo-H0h8gOQ?usp=drive_link) 
and download the data to `data/embeddings/similarities/`.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

