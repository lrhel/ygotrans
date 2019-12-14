
## YGOTrans - A translator for Ygopro CDB's file

The script will firstly copy the cdb passed as argument to a backup version [name + .backup]
Then the script will create a file missing_translation.txt which hold the passcode of the card that couldn't be fetched (no translation).

### Installation

You need to have python3 and pip then install dependencies with

```
python3 -m pip install -r requirements.txt
```

### Usage

./ygotrans.py [OPTION]... [CDB] [LANG]

* OPTION:
    * -h, --help  show this help message and exit
    * -y, --yugipedia Use Yugipedia instead of Wikia
    
* CDB:
    * The path to the CDB file
    
* LANG:
    * en
    * fr
    * de
    * it
    * pt
    * es
