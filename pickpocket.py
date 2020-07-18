# pickpocket - a Python script to removed duplicates from your Pocket account

# Copyright (C) 2018  Hugh Rundle

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# You can contact Hugh on Twitter @hughrundle
# or Mastodon at @hugh@ausglam.space 
# or email hugh [at] hughrundle [dot] net

# ----------------
# Import libraries
# ----------------

# You will need to install the 'requests' library from the command line with 'pip install requests' or, if you're using Python3 you might need to use 'pip3 install requests' instead
# import the 'requests' library into your script
# docs for requests are at http://docs.python-requests.org
import requests

# import webbrowser, json and urllib libraries
# these come bundled with Python so you don't have to install them first
# info for webbrowser is at https://docs.python.org/3/library/webbrowser.html
# info for json is at https://docs.python.org/3.5/library/json.html
# info for urllib is at https://docs.python.org/3/library/urllib.parse.html
import webbrowser
import json
import urllib

# ----------------
# Create app
# ----------------

# Log in to Pocket in a web browser
# Go to https://getpocket.com/developer and click 'CREATE NEW APP'
# Complete the form: you will need 'Modify' and 'Retrieve' permissions, and the platform should be 'Desktop (other)'
# Your new app will show a 'consumer key', which you need to paste in between the quotes below

# assign the consumer key to a parameter called consumer_key
consumer_key = 'YOUR_CONSUMER_KEY_HERE'
# assign a redirect URL for Pocket authentication
redirect_uri = 'https://hugh.run/success'

# ----------------
# Authorise
# ----------------

# Now you need to authorise your app - you have a consumer_key for the app, but you need an access_token to be able to use it on your pocket collection.
# Docs - https://getpocket.com/developer/docs/authentication
# Note that for Pocket API calls, we must use POST exclusively (not GET)
# To make an API call we use the requests library like: requests.post('url', params)

# Pocket expects particular HTTP headers to send and receive JSON
headers = {"Content-Type": "application/json; charset=UTF-8", "X-Accept": "application/json"}
paramsOne = {"consumer_key": consumer_key, "redirect_uri": redirect_uri}

# set up step 1 request - this should return a 'code' aka 'request token'
requestOne = requests.post('https://getpocket.com/v3/oauth/request', headers=headers, params=paramsOne)
# if you want to see the JSON response you can print to screen here by uncommenting the line below
# print(requestOne.json())
# we only want the 'code', so we get that like "jsonObject['key']"
# get the JSON response and save the token to a param for the next step
request_token = requestOne.json()['code']
# print the request token to the console so you know it happened
print('Your request token (code) is ' + request_token)

# now you need to authorise the app in your Pocket account
# build the url
auth_url = 'https://getpocket.com/auth/authorize?request_token=' + request_token + '&redirect_uri=' + redirect_uri
# open the authorisation page in a new tab of your default web browser
webbrowser.open(auth_url, new=2)

# We're not writing a server app here so we use a little hack to check whether the user has finished authorising before we continue
# Just wait for the user (you!) to indicate they have finished authorising the app
# the '\n' prints a new line
print('Authorise your app in the browser tab that just opened.')
user_input = input('Type "done" when you have finished authorising the app in Pocket \n>>')

if user_input == "done":
  # now we can continue
  # do a new request, this time to the oauth/authorize endpoint with the same JSON headers, but also sending the code as a param
  paramsTwo = {"consumer_key": consumer_key, "code": request_token}
  requestTwo = requests.post('https://getpocket.com/v3/oauth/authorize', headers=headers, params=paramsTwo)
  # get the JSON response as a Python dictionary and call it 'res'.
  res = requestTwo.json()
  # Finally we have the access token!
  print('Access token for ' + res['username'] + ' is ' + res['access_token'])
  # Assign the access token to a parameter called access_token
  access_token = res['access_token']

  # What a bunch of faffing around. Now we can make API calls with the consumer_key for the app and the access_token for the user.

  # ----------------
  # Retrieving items
  # ----------------

  # Now retrieve all 'unread' items (i.e. not archived)
  # we use the Retrieve API call = https://getpocket.com/developer/docs/v3/retrieve
  # The endpoint for retrieving is 'get': https://getpocket.com/v3/get

  # detailType should be 'simple' because we don't need any information except for the item_id and the resolved_url
  parameters = {"consumer_key": consumer_key, "access_token": access_token, "detailType": "simple"}
  headers = {"Content-Type": "application/json"}
  unread = requests.post('https://getpocket.com/v3/get', headers=headers, params=parameters)
  
  # our items will be under the JSON object's "list" key
  item_list = unread.json()['list']
  
  # make a new dictionary called 'summary'
  # we will use this to look for duplicates
  summary = {}  

  # and make a list called 'items_to_delete'
  # I hope you can guess what this will be used for...
  items_to_delete = []

  # loop over each key (not the whole object) in item_list
  # 'item' here refers to each item's key, not the whole object/dictionary
  print('checking ' + str(len(item_list)) + ' items...')
  for item in item_list:
    # conveniently the key Pocket uses is the item_id!
    item_id = item

    # we need the item_id from this request so we can use it in the next API call to delete it
    # get the URL by pulling out the value from the dict using the key
    # generally we want to use the 'resolved url' but sometimes that might not exist
    # if so, use the 'given url' instead
    if not 'resolved_url' in item_list[item]:
      # item_list is a Python dictionary where each value is itself another dictionary
      # or in JSON terms, it's an object where each value is another object
      # below we are getting the value of the current item id (i.e the first dict), then checking if there is a value within the second dict for the key 'given_url'
      item_url = item_list[item]['given_url']
    else:  
      item_url = item_list[item]['resolved_url']
    
    # check whether the resolved_url is already in 'summary'
    # if it isn't, make a new entry with resolved_url as the key and a list holding item_id as the value - basically we're reversing the logic of 'item_list'. This will allow us to check for duplicates easily in a moment.
    if not item_url in summary:
      summary[item_url] = [item_id]
    # if it is there already, add the item_id into the existing list
    else:
      summary[item_url].append(item_id)

  # ------------------
  # Finding duplicates
  # ------------------

  # now we look for duplicates (this is why we use the url as the key)
  for item in summary:
    
    # if the length of the list is more than 1, then by definition there must be a duplicate
    if len(summary[item]) > 1:
      print(item + ' occurs ' + str(len(summary[item])) + ' times')
      # keep only the most recently added item by slicing the list to make a new list of everything except the last one
      # see https://stackoverflow.com/questions/509211/understanding-pythons-slice-notation#509295 for an explanation of why this works
      duplicates = summary[item][:-1]
      # add each duplicate in the duplicates list for this url to the items_to_delete list
      for item in duplicates:
        items_to_delete.append(item)

  # -------------------
  # Deleting duplicates
  # -------------------

  # now use the modify API call to delete duplicate items
  # Docs - https://getpocket.com/developer/docs/v3/modify

  # With our list of duplicate item ids, we create one final list of a bunch of JSON objects
  actions = []

  # for each item to be deleted, append a dictionary to the actions list
  for item_id in items_to_delete:
    actions.append({"action":"delete", "item_id": item_id})

  # Double check you really want to delete them
  print('About to delete ' + str(len(actions)) + ' duplicate items.')
  check = input('Delete these items? Type "delete" to confirm.\n>>')
  if check == 'delete':
    # For some reason when we use the 'send' API endpoint, instead of just sending JSON like we do for the other endpoints, we have to URL encode everything 🤷🏻‍
    # first turn the list and its component dictionaries into a JSON string using the json module's "dumps" ("dump string")
    actions_string = json.dumps(actions)
    # now URL encode it using urllib
    actions_escaped = urllib.parse.quote(actions_string)
    # now POST to pocket and assign the response to a parameter at the same time.
    deleted = requests.post('https://getpocket.com/v3/send?actions=' + actions_escaped + '&access_token=' + access_token + '&consumer_key=' + consumer_key)
    # print the response - it should return '<Response [200]>'
    print(deleted)
    # provide feedback on what happened
    # 'deleted' is a raw http response so we need to turn it into a Python string before we can do a comparison
    if str(deleted) == '<Response [200]>':
      print('These duplicates have been deleted:')
      for item in actions:
        print(item['item_id'])
      # that's it!
    else:
      print('Something went wrong :-(')
  else:
    print('deletion cancelled.')
else:
  # if the user didn't type 'done' then ...we're done.
  print('bye then')
