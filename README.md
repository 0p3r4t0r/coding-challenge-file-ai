# File AI Coding Challenge

[PO - Invoice Matching Assessment use case.docx - Google Docs](./PO%20-%20Invoice%20Matching%20Assessment%20use%20case.docx%20-%20Google%20Docs.pdf)

## Questions

- Should data be ingested into a database, or is doing everything in-memory acceptable?




## Quickstart

### Local

- [Install uv package manager](https://docs.astral.sh/uv/getting-started/installation/)
- Install dependencies: `uv sync`


### Docker (TODO)

For those who really don't want to [install uv](https://docs.astral.sh/uv/getting-started/installation/)




## Function Requirements Checklist

- [x] System must read two Excel files.
  - [x] PO.xlsx
  - [x] Invoices.xlsx
- [ ] Validate column headers
- [ ] Normalize data types (numbers, text)




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


- Data Ingestion/Output (Read/Write Excel): [pandas](https://pandas.pydata.org/)

    - pandas depends [openpyxl](https://openpyxl.readthedocs.io/en/stable/),
      while it's possible to use openpyxl directly, pandas offers a more powerful api
      and is popular enough that many engineers and data scientists already have
      experience with it.

    - pandas also comes with capabilities for data validation and normalization.

