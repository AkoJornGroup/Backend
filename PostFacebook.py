import requests

#Your Access Keys
page_id_1 = 112108255272481

# Your Page Access Token
facebook_access_token_1 = 'EAAIZAnKtQNZB0BAEoN1Gv2F49rbfRhYZCMT3el2NCzwwLrlvrmckaTNdKUWb5S5TFQZBs6B3SWv8lx6v8mdZB3byffKYtFiQ2X2IOu4ZBPerYVBHV3RPiidamAUXnF1AUOMdIIQDRFZBWst4jlZBGR7AOzL8H8czr8OI4bzi5d0ldn3j9IohAZBgZAgpNWH78INRBOwd9EBS5q2gESgwaSc7n9OAhwZAO0vKwYZD'

# Post Content as Text
msg = 'Test Post From Python'
post_url = 'https://graph.facebook.com/{}/feed'.format(page_id_1)
payload = {
'message': msg,
'access_token': facebook_access_token_1
}
r = requests.post(post_url, data=payload)
print(r.text)