## DUCO API Module
To build your own Duino-Coin apps we've created Duino-Coin API for python3. Here's the documentation for the module.

<h3>Getting Started</h3>

```python
import duco_api
```

Initialize the connection to the server

```python
api_connection = duco_api.api_actions() #creates the api connection instance
```

The next step is to Login/Register <i>*Note: login and register do not require you to init but they close the connection after use*</i>
<h4>Login</h4>

```python
api_connection.login(username="username", password="password")
```

<h4>Register</h4>

```python
api_connection.register(username="username", password="password", email="user@example.com")
```

<h3>Functions</h3>
These functions require user being loged-in.

<h4>Balance</h4>
Gets the current balance of the logged-in user

```python
api_connection.balance() # takes no args
```

<h4>Transfer</h4>
Transfers Duco from logged-in user to the specified username

```python
api_connection.transfer(recipient_username='test_user1', amount=1)
```

<h4>reset password</h4>
Resets the password of the logged-in user

```python
api_connection.reset_pass(old_password='123', new_password='abc')
```

<h4>Get Latests Transactions</h4>
Get the latests transactions

```python
api_connection.getTransactions(7) # 7 is the number of transactions to get
# returns JSON
```

<h3>Other Functions</h3>
Use of this functions does not require being loged-in.

<h4>Get Duco Price</h4>
returns the current Duco price as a float

```python
>>> duco_api.get_duco_price() 
0.01249
```

<h4>Duco price update timer</h4>
starts a timer that updates the price at a specified interval in seconds (default is 15)

```python
>>> duco_api.start_duco_price_timer(interval = 5) # start the timer that updates the price every 5 seconds
>>> duco_api.duco_price # you can get the updated price from a global variable <duco_price>
0.01249
```

<h4>Example API script</h4>

```python
import duco_api

api_connection = duco_api.api_actions()

api_connection.login(username='YourUsername', password='YourPassword')

current_balance = api_connection.balance()
print(current_balance)

api_connection.close()
```
