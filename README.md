# File AI Coding Challenge

- [Prompt: PO - Invoice Matching Assessment use case](./additional_documents/Prompt_PO%20-%20Invoice%20Matching%20Assessment%20use%20case.pdf)

- [Job Description: Senior Solution Engineer](./additional_documents/JD_Sr.Solution%20Engineer.pdf)

  - The JD specifically asks for "Hands-on experience with Python and SQL." so
    the application is built in Python and PostgreSQL.


## Quickstart




## Testing




## Functional Requirements Checklist

- [x] System must read two Excel files.
  - [x] PO.xlsx
  - [x] Invoices.xlsx
- [ ] Validate column headers
- [ ] Normalize data types (numbers, text)




## Data

### Models

- `purchase_orders`
  - `purchase_order_lines` -- many-to-one --> `purchase_orders`
- `invoices`
  - `invoice_lines` -- many-to-one --> `invoices`

⚠️ We do not normalize items into their own table.
The price of an item could change over time, and thus across purchase orders,
so we want to track them in-line.

We *do* want to ensure that item prices are consistent throughout a purchase
order and all invoices and in order to do so we require the following...

- An item may only be listed *once* on a given purchase order.

- An item may only be listed *once* on a given invoice: there is no
  problem with an item appearing multiple times across several invoices. 

- The purchase order sets the unit price of an item, any discrepancies found
  thereafter in an invoice will be treated as an error.




### Data Flow

Ingestion -> Aggregation -> Output

#### Ingestion

* Each ingestion operation is wrapped in a transaction to ensure atomicity.

1. Validate and Import purchase order.
  - [ ] Ensure `PO Number` is consistent across all rows for a give PO.
  - [ ] Create `purchase_orders` record.
  - [ ] Create `purchase_order_lines` record for each line.
    - [ ] Ensure that `Quantity * Unit Price == Total Amount`

2. Validate invoice again purchase order.
  - [ ] Ensure `PO Number` is consistent across all rows for a given invoice.
  - [ ] Ensure `PO Number` matches an existing purchase order
  - [ ] Ensure `Invoice Number` is consistent across all rows for a given invoice.
  - [ ] Create `invoices` record.
  - [ ] Create `invoice_lines` record for each line.
    - [ ] Ensure that `Unit Price` on the invoice line matches the purchase order.
    - [ ] Ensure that `Quantity * Unit Price == Total Amount`


#### Aggregation

If we were processing massive amounts of data here, it would make more sense
to do this in SQL and then send the result back to Python, but I think it's
safe to assume that a single purchase order and its invoices will never
contain enough data for this to be a concern.

We will fetch the data from the database, and perform the aggregation in
Python before writing the result out to the file system.


#### Output

For the purposes of this project, we will simply output the final excel
to the file system.




## Tech Stack and Library Choices

Documenting my thought process as I go.


- [Docker](https://www.docker.com/): Easily run the application yourselves.


- Python dependency management: [uv](https://docs.astral.sh/uv/)

    - [Poetry](https://python-poetry.org/) is another option.
      I personally find uv more intuitive and it's also
      [much faster than poetry](https://github.com/astral-sh/uv/blob/main/BENCHMARKS.md).

    - Why not just `requirements.txt`? 
      `requirements.txt` does not enforce version requirements on dependencies 
      of packages. `uv` explicitly raise errors at install time. Furthermore,
      `uv` also manages your python version and automatically creates a
      [venv](https://docs.python.org/3/library/venv.html).


- Use [typing](https://docs.python.org/3/library/typing.html)

  - Typing has been part of the standard library since 3.5, which was released in 2015.
    The real world was slow to catch up, but it's not uncommon to see them these days.
    I try to make a habit of using them whenever I can.


- Data Ingestion/Output (Read/Write Excel): [pandas](https://pandas.pydata.org/)

    - pandas depends [openpyxl](https://openpyxl.readthedocs.io/en/stable/),
      while it's possible to use openpyxl directly, pandas offers a more powerful api
      and is popular enough that many engineers and data scientists already have
      experience with it.

    - pandas also comes with capabilities for data validation and normalization.


- Database Migrations

  - A popular choice in Python is [Alembic](https://alembic.sqlalchemy.org/en/latest/)
    which is built on [SQLAlchemy](https://www.sqlalchemy.org/).
    However, the use of Alembic doesn't necessarily demonstrate nowledge of SQL.
    For this reason I've opted to write the initialization scripts in pure SQL and use
    [/docker-entrypoint-initdb.d](https://docs.docker.com/guides/pre-seeding/#pre-seed-the-database-by-bind-mounting-a-sql-script)
    to ensure the database initialization is run on container startup.


- Database Queries: Using an ORM

  - If I'm going to write an entire project for an interview, I've got to at least
    use the opportunity to try something new.

  - I looked into [Tortoise ORM](https://github.com/tortoise/tortoise-orm?tab=readme-ov-file#introduction)
    and their benchmarks actually show [Pony ORM](https://github.com/ponyorm/pony) as being the fastest.

  - Pony has two extremely interesting features.
  
    - [You can use Python generator expressions for queries](https://docs.ponyorm.org/queries.html).
      The way Pony achieves this extremely interesting. You can read
      [this answer by the creator on StackOverflow](https://stackoverflow.com/questions/16115713/how-pony-orm-does-its-tricks)
      if you would like to learn more about it.

    - It uses the [Identity Map Pattern](https://en.wikipedia.org/wiki/Identity_map_pattern) to cache results.
  
  - Finally, I plan to make extensive use of transactions, and
    [Pony's API makes this very easy](https://ponyorm.readthedocs.io/en/latest/transactions.html)

