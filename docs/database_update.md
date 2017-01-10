# Updating the database
This is a stand alone part of which the second part data depends on it.

Download the content on [github link](https://github.com/Eb-Zeero/skybright_update)

#### File names
*  `configurations.ini`
*  `update_skybrightness_database.py`

***configurations.ini*** contains settings which must be kept secret.
Ensure that it is *not put under version control after updating it*.
And this file must always be on the same directory as
*update_skybrightness_database.py*

***update_skybrightness_database.py*** is a python 3 script that must run automatically (so far once a day) every time the data on the astmon data is updated.

Running by command

```bash
python3 update_skybrightness_database.py
```

*read [readme](https://github.com/Eb-Zeero/skybright_update/blob/master/README.md) for details*