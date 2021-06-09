
  
# Account  
Supports handling fund transfers between users, listing all user transactions and accessing a particular user transaction by the transaction Id  
    
## P2P Transfer    
 **Request**:    
    
`POST` `/account/:sender_account_id/transfers/:recipient_account_id`    
 Parameters:    
    
Name                 | Type   | Required | Description    
--------------------|--------|----------|------------    
amount   | number | Yes      | The amount to be transfered   funds.    
 
  
    
*Note:*    
 - **[Authorization Protected](authentication.md)**    
 **Response**:    
    
```json    
Content-Type application/json    
201 Created    
    
{    
  "status": "complete",    
  "amount": 500,    
  "transaction_type": "p2p transfer",    
}    
```    
    
    
    
## Get all transactions for a particular user **Request**:    
    
`GET` `/account/:account_id/transactions`    
  
    
*Note:*    
 - **[Authorization Protected](authentication.md)**    
 **Response**:    
    
```json    
Content-Type application/json    
200 OK    
    
{  
    "count": 24,  
    "next": null,  
    "previous": null,  
    "results": [  
        {  
            "id": "053e5fab-7c99-4f9c-9305-bdc9ffcd3dd1",  
            "type": "withdrawal",  
            "created": "2021-06-08T17:05:12+0100",  
            "modified": "2021-06-08T17:05:12+0100",  
            "reference": "Withdrawalc28310b297d05928c46e1d",  
            "status": "complete",  
            "amount": 10.0,  
            "new_balance": 0.0,  
            "owner": "8394ecc4-0138-4fe4-b649-285979782141"  
        },  
        ...                         
]  
}  
  
```    
  
  
## Get a user transaction by Id **Request**:    
    
`GET` `/account/:account_id/transactions/:transaction_id`    
 
  
    
*Note:*    
 - **[Authorization Protected](authentication.md)**    
 **Response**:    
    
```json    
Content-Type application/json    
200 OK    
    
{  
    "id": "13d45aae-cc34-43d3-9d62-19024a5ab37e",  
    "username": "mandi",  
    "first_name": "mandi",  
    "last_name": "papers"  
}  
```
