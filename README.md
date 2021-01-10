

This proccess involves multiple python libraries. You might want ot use venv.

Also we are going to need Python 3.6+ and pip
```
sudo apt-get install python3 python3-pip
```


### Get list of websites from Hlídač státu

Setup `api_token` for Hlídač státu in `config.py`.

```
python3 -m pip install --user requests
python3 get_data_hlidac_statu.py
```

### Use ADAM from CZ.NIC to collect DNS data

The following part you might want to do from VM, as scanning is prohibited some ISPs for home plans.

From Ubuntu 20.04:
```
snap install docker
git clone https://gitlab.nic.cz/adam/dns-crawler.git
docker build dns-crawler
```

The `list_dns_to_check.txt` is `data\source_lists\weby_merged.txt`, or any other newline separated list of domains.

```
mkdir app_files

# Copy the two following files from this repository to the VM in cloud. For example by pasting or cloning the repo.
# nano app_files/list_dns_to_check.txt 
# nano docker-compose.yml

docker-compose up --build
```

Then copy the resulting file from `app_files/output.json` to your own PC, to path `data/fromAdam/raw.json`.
In `filter_data_from_cznic_adam.py` set variable `filename_dns_crawler_raw` to the path you've copied the result in previous step.
Then run `python3 filter_data_from_cznic_adam.py`


### Use Python library checkdmarc

Python library checkdmarc is used to check validity of DMARC and get additional info about SPF.

```
python3 -m pip install --user checkdmarc
python3 get_data_checkdmarc.py
```

Copy the result to `data/checkdmarc/checkdmarc.json`. (If you are running it all on the same machine, it's already there.)

### Use pyspf for dynamic evaluation against bogus IP

Use pyspf library to check, whether bogus IP is allowed.
Also, you can manally check some combination of HELO and IP would be compliant with SPF record of website.

```
python3 -m pip install --user dnspython pyspf authres loguru tqdm
python3 get_data_pyspf.py
```


### Unify datasources

```
python3 -m pip install --user loguru
python3 unify_datasources.py
```

### Data visualisation

For data visualisation and some parts of the analysis jupyter notebook is used. `data_visualisation.ipynb` 

```
python3 -m pip install --user pandas matplotlib loguru
jupyter notebook
```


