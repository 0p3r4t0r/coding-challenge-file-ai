- Setup unit tests that run on pre-commit

- add file-hashes
  - because excel stores metadata we need to hash csv files
  - because the OS might create extra things in a file, we will
    simply concatenate the csvs.
- add filename of report to db report record
- add soft-delete
- Consider indexes for SQL

- Validate that unit_price on purchase order matches the invoice.
- Final cleanup of code -- add comments for the walkthrough
- Final cleanup of documentation