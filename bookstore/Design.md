### sql 版本的表结构

##### Table User
- user_id
- password
- balance
- token
- terminal

### Table Book
- store_id PRIMARY
- book_id PRIMARY
- book_info
- stock_level

### Table UsertoStore
- user_id
- store_id

### Table Order
- order_id
- buyer
- store_id
- state
- total_price
- timestamp

### Table OrdertoBooks
- order_id
- book_id
- count
- price


### Mongodb 版本表结构

##### Doc user

- _id (user_id)
- password
- balance
- token
- terminal



##### Doc book

- _id (store_id, book_id)
- book_info (class)
- stock_level



##### Doc store

- owner (user_id)
- _id (store_id)



##### Doc order

- order_id
- buyer (user_id)
- store (store_id)
- total_price
- books (list)
  - book_id
  - count
  - price
- state (`Literal[unpaid, paid, delivered, canceled, finished]`)
- timestamp
