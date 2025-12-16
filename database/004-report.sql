CREATE TABLE report (
    id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    purchase_order_id TEXT NOT NULL,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,

    FOREIGN KEY (purchase_order_id)
        REFERENCES purchase_order (id)
        ON DELETE CASCADE
);


CREATE TABLE report_invoice (
    id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    report_id INT NOT NULL,
    invoice_id TEXT NOT NULL,

    UNIQUE (report_id, invoice_id),

    FOREIGN KEY (report_id)
        REFERENCES report (id)
        ON DELETE CASCADE,

    FOREIGN KEY (invoice_id)
        REFERENCES invoice (id)
        ON DELETE CASCADE
);