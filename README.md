Filmtipset Data Exporter
========================

Export data from your account at Filmtipset.

The goals of this project are

1. To backup your movie ratings from Filmtipset
2. To upload your ratings to other sites, such as Flixter

Information
-----------

The project is written in Python 3.0 by André Laszlo. It does not make use of
Filmtipset's API but instead uses plain HTTP requests and regular expression
parsing of the received responses.

This project is mainly for my personal use but I have decided to put it here on
GitHub since there might be other people out there that might want to backup
their movie ratings. Please note that this program is quite request heavy and I
have not gotten permission from Filmtipset to do this - you have been warned,
do not blame me if you get banned or something.

If you wish to contact me, my email address is <andre@laszlo.nu>.

Files
-----

* browser.py - A small http "browser" class that keeps cookies (made for this project)
* filmtipset.py - The main program
* README.md - This text
* .gitignore - List of files for GIT to ignore

License
-------

[Filmtipset Data Exporter by André
Laszlo](https://github.com/andrelaszlo/Filmtipset-Data-Exporter) is licensed
under a [Creative Commons Attribution-NonCommercial 3.0 Unported
License](http://creativecommons.org/licenses/by-nc/3.0/).

Permissions beyond the scope of this license may be available at
<andre@laszlo.nu>.