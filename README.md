**pickpocket** is a Python script to find and remove duplicates in your [Pocket](https://getpocket.com) account.

# Before you run the script

Make sure you've installed Python 3. This is *not* installed on MacOS by default: MacOS comes with Python 2. The easiest way to install and use Python 3 on Mac is to [use Homebrew](https://docs.brew.sh/Homebrew-and-Python).

Read through the script - it includes lots of comments on what each step is doing.

You need to create an app in your Pocket account:

* log in
* go to https://getpocket.com/developer
* click CREATE NEW APP
* enter a name and description
* give it 'modify' and 'retrieve' permissions
* click 'Desktop - other' as the platform
* accept the Terms of Service

Now paste your app's 'consumer key' at line 51 of the script.

# Running

Run the script with `python3 pickpocket.py`
If you type anything other than as directed at the prompt ('done' and 'delete') the script will exit. This is a failsafe allowing you to back out before it deletes things.

# Bugs and suggestions

If you find a bug or have a suggestion for improvement, please log an issue.

# License

GPL 3.0+