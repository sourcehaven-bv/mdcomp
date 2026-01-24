# Invoice Example

Generate professional invoices from timesheet data.

## Structure

```
invoice/
├── templates/
│   └── invoice.md.j2      # Main invoice template
├── snippets/
│   ├── company-header.md  # Your company details
│   ├── payment-terms.md   # English payment terms
│   └── payment-terms-nl.md # Dutch payment terms
├── context/
│   └── acme-january.yaml  # Invoice data (client, timesheet)
└── output/
    └── invoice-acme-january.md
```

## Usage

```bash
# Generate invoice
mdcomp render templates/invoice.md.j2 \
  -c context/acme-january.yaml \
  --snippets snippets \
  -o output/invoice-acme-january.md

# Convert to PDF
mdcomp render templates/invoice.md.j2 \
  -c context/acme-january.yaml \
  --snippets snippets | \
  pandoc -o output/invoice-acme-january.pdf

# Override values on the fly
mdcomp render templates/invoice.md.j2 \
  -c context/acme-january.yaml \
  --snippets snippets \
  --var vat_rate=0 \
  --var "payment_days=14"
```

## Customization

### Different languages

Edit the template to use Dutch payment terms:

```jinja
{{ content("snippets/payment-terms-nl.md") }}
```

### Add your company details

Edit `snippets/company-header.md` with your information.

### Different VAT rates

Override in context file or via CLI:
- `--var vat_rate=0` for VAT-exempt
- `--var vat_rate=9` for reduced rate
