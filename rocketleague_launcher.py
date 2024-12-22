import os, requests, uuid, subprocess

rlpath = 'C:\\Epic Games\\rocketleague\\Binaries\\Win64\\RocketLeague.exe'
envfile = '.epivenv'

# Configure this if you want to proxy the traffic
#proxy = {'http': '127.0.0.1:8888', 'https': '127.0.0.1:8888'}
#verify = False
proxy = {}
verify = True

epic_api_url = 'https://account-public-service-prod.ak.epicgames.com/account/api'

# Step 1 (browser) - GET https://www.epicgames.com/id/api/redirect?clientId=34a02cf8f4414e29b15921876da36f9a&responseType=code&prompt=login&
# Step 2 (get auth & refresh codes) - POST https://account-public-service-prod.ak.epicgames.com/account/api/oauth/token - grant_type=authorization_code&code=<code>
# Step 3 (convert refresh code to eg1 refresh & access token) - POST https://account-public-service-prod.ak.epicgames.com/account/api/oauth/token - grant_type=refresh_token&refresh_token=<refresh>&token_type=eg1
# Step 4 (use access token to get an exchange code) - GET https://account-public-service-prod.ak.epicgames.com/account/api/oauth/exchange - Authorization: bearer <access_token>
# Step 5 (launch game with -AUTH_PASSWORD=<exchangecode>)

# Perform an API request using the Epic Launcher authorization credentials
def api_request(method='post', path='/oauth/token', data='', auth='basic MzRhMDJjZjhmNDQxNGUyOWIxNTkyMTg3NmRhMzZmOWE6ZGFhZmJjY2M3Mzc3NDUwMzlkZmZlNTNkOTRmYzc2Y2Y='):
	
	if method == 'post':
		req = requests.post(epic_api_url + path, headers={
			'Accept': '*/*',
			'Accept-Encoding': 'deflate, gzip',
			'X-Epic-Correlation-ID': 'UE4-5dea7166457d308530e85a9b3333ff78-C9AD1AA540580FDB3CCEA5B0A22B3218-' + str(uuid.uuid4()).replace('-', '').upper(),
			'User-Agent': 'UELauncher/16.12.1-36115220+++Portal+Release-Live Windows/10.0.22631.1.768.64bit',
			'Content-Type': 'application/x-www-form-urlencoded',
			'Authorization': auth
		}, data=data, proxies=proxy, verify=verify)
	elif method == 'get':
		req = requests.get(epic_api_url + path, headers={
			'Accept': '*/*',
			'Accept-Encoding': 'deflate, gzip',
			'X-Epic-Correlation-ID': 'UE4-5dea7166457d308530e85a9b3333ff78-C9AD1AA540580FDB3CCEA5B0A22B3218-' + str(uuid.uuid4()).replace('-', '').upper(),
			'User-Agent': 'UELauncher/16.12.1-36115220+++Portal+Release-Live Windows/10.0.22631.1.768.64bit',
			'Authorization': auth
		}, proxies=proxy, verify=verify)

	return req

##########################


if __name__ == '__main__':
	epicenv = ''
	with open(f'{os.getcwd()}\\{envfile}', 'r') as f:
		epicenv = f.read()

	auth_code = ''
	refresh_token = ''
	if len(epicenv) == 32:
		auth_code = epicenv
	else:
		refresh_token = epicenv

	# If we only have an auth code let's convert it to an initial generic refresh code
	if auth_code:
		req = api_request(method='post', path='/oauth/token', data='grant_type=authorization_code&code=' + auth_code)
		refresh_token = req.json()['refresh_token']

	# Get a new eg1 access token and refresh code
	req = api_request(method='post', path='/oauth/token', data='grant_type=refresh_token&refresh_token=' + refresh_token + '&token_type=eg1')

	access_token = req.json()['access_token']
	refresh_token = req.json()['refresh_token']
	account_id = req.json()['account_id']

	# Save our refresh code for next time
	with open(f'{os.getcwd()}\\{envfile}', 'w') as f:
		f.write(refresh_token)

	# Exchange our access token for a launcher code
	req = api_request(method='get', path='/oauth/exchange', auth='bearer ' + access_token)

	code = req.json()['code']

	# Launch the game using our launcher exchange code!
	subprocess.Popen([rlpath, '-AUTH_LOGIN=unused', '-AUTH_PASSWORD=' + code, '-AUTH_TYPE=exchangecode', '-epicapp=Sugar', '-epicenv=Prod', '-EpicPortal', '-epicusername=""', '-epicuserid=' + account_id])