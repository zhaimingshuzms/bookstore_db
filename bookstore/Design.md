### sql 版本的表结构

##### Table User
- user_id PRIMARY FOREIGNKEY
- password
- balance
- token
- terminal

### Table Book
- store_id PRIMARY FOREIGNKEY
- book_id PRIMARY
- book_info
- stock_level

### Table UsertoStore
- user_id
- store_id PRIMARY

### Table Order
- order_id PRIMARY FOREIGNKEY
- buyer FOREIGNKEY
- store_id FOREIGNKEY
- state
- total_price
- timestamp

### Table OrdertoBooks
- order_id PRIMARY FOREIGNKEY
- book_id PRIMARY
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
