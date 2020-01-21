==================
resourcemanager.ap
==================

This add-on is meant to work with collective.resourcemanager.

See the collective.resourcemanager documentation for more details: https://github.com/collective/collective.resourcemanager


Installation
------------

Install the collective.resourcemanager and resourcemanager.ap packages by adding them to your buildout::

    [instance]
    ...
    eggs =
        ...
        collective.resourcemanager
        resourcemanager.ap


Run ``bin/buildout``, and start the instance.

Within Plone:

* Install the add-ons in the Add-ons Control Panel
* Go to the Associated Press Keys Control Panel
* Enter your API key from AP

Use
---

Searching AP within Plone will show you the images available to your account.
Search results will display pricing information to download the original sized image based on your subscription.


Contribute
----------

- Issue Tracker: https://github.com/collective/resourcemanager.ap/issues
- Source Code: https://github.com/collective/resourcemanager.ap


License
-------

The project is licensed under the GPLv2.
