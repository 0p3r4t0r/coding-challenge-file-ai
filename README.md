# File AI Coding Challenge

- [Prompt: PO - Invoice Matching Assessment use case](./additional_documents/Prompt_PO%20-%20Invoice%20Matching%20Assessment%20use%20case.pdf)

- [Job Description: Senior Solution Engineer](./additional_documents/JD_Sr.Solution%20Engineer.pdf)

  - The JD specifically asks for "Hands-on experience with Python and SQL." so
    the application is built in Python and PostgreSQL.




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





## Tech Stack and Library Choices

Documenting my thought process as I go.

- Python dependency management: [uv](https://docs.astral.sh/uv/)

    - I believe [poetry](https://python-poetry.org/) is also a valid choice,
      however, I find uv more intuitive and it's **much** faster than poetry.

    - Especially on machine-learning or AI projects, it's common to swap libraries.
      New AI models come out every week, and the rapid release pase quickly leads
      to version conflicts, even in small teams. There's no reason to deal with
      these issues manually, they exist in every programming language, and that's
      what package managers are for. It's unfortunate that Python doesn't really
      force your to use one.

    - Why not just `requirements.txt`? There is no lockfile, and so `requirement.txt`
      doesn't actually guarantee that your environment is reproducible. Also, uv
      automatically handles the creation of a [venv](https://docs.python.org/3/library/venv.html)


- Docker: Maximize portability for very little additional effort.


- Use [typing](https://docs.python.org/3/library/typing.html)

  - type-hinting and static analysis have come a long way in Python, especially
    over the last 3 years. I can't say I see people taking advantage of it too
    often, but it's something I always try to use whenever possible.


- Data Ingestion/Output (Read/Write Excel): [pandas](https://pandas.pydata.org/)

    - pandas depends [openpyxl](https://openpyxl.readthedocs.io/en/stable/),
      while it's possible to use openpyxl directly, pandas offers a more powerful api
      and is popular enough that many engineers and data scientists already have
      experience with it.

    - pandas also comes with capabilities for data validation and normalization.

