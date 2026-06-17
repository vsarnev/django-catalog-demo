# Electrical Supply Catalog Using Django

A simple Django application that models an electrical-construction supply catalog
(products, categories, and tags) and provides a search-and-filter page.

Products are grouped into **categories** and described by spec-related **tags** 
(material, gauge, amperage, voltage, etc.) alongside a search bar that searches for 
substrings across each product's various attributes.

## Tech stack

- **Python 3.11+**
- **Django 5.2.15**
- **SQLite** (Django's default; the database file is committed pre-populated)

## Setup & running

### 1. Install dependencies
```
pip install -r requirements.txt
```
### 2. Create your own admin login (the committed DB has data but no shared password)
```
python manage.py createsuperuser
```
### 3. Run the development server
```
python manage.py runserver
```

Then visit:

- **`http://127.0.0.1:8000/`** - the product catalog
- **`http://127.0.0.1:8000/admin/`** - the Django admin interface

## Sample data

The committed `db.sqlite3` is pre-populated with **6 categories, 31 tags, and 25
products**, so the catalog works immediately. All data is added via the admin interface,
and can easily be viewed and edited there. The data is mostly fabricated and AI was used
here to quickly generate a sample dataset to use.

## Running the tests

```
python manage.py test
```

There are 13 tests in `catalog/tests.py` covering the search and filter query logic.

## Data model

There are three models defined in `catalog/models.py`:

#### Category
A simple name for different product categories

#### Tag
Tags contain a name and optionally a grouping to help keep them organized. The group
set is small and fixed for the purposes of this demonstration, so this solution is 
simpler than another model.

#### Product
Products have a name, description, SKU, manufacturer and a stock count. They also must 
reference a `Category` as a foreign key, and at least one `Tag`. The stock count is used
in the `is_in_stock` property to allow easy filtering for in-stock items only.

## Search & filter functionality

The catalog page (`product_list in catalog/views.py`) builds a queryset by starting from
all products and conditionally narrowing it for each filter present in the request:

#### Search box 
A single free-text query matched (case-insensitively) across product name, description, 
manufacturer, SKU, category name, and tag names, using `Q` objects OR-ed together.

#### In-stock-only
Excludes products with `stock = 0`.

#### Category Filter
Narrows to only items in that specific category. When a category is selected, the tag 
sidebar is filtered to only tags actually relevant to the products in that category.

#### Tag filters
Selected tags are grouped by their group, and one filter is applied per group. This allows
AND across groups, and OR within a group. (e.g. Copper **and** (12 AWG **or** 14 AWG wire))
A final distinct call removes possible duplicates introduced by the many-to-many joins.

## AI usage disclosure

AI Tooling (Claude Code/Github Copilot) was used for assistance during development. 
Specifically, it was used to:

- Generate the sample dataset of products, categories, and tags to simplify implementation
- Reviewing certain concepts and aiding understanding of some topics such as security,
utilizing filters, and how to implement the templates.
- Reviewing my implementation plans and architecture and offering feedback and adjustments
- Various optimizations and bugfixes
- Github Copilot to autocomplete simple additions
- Generating the sample data for the setUp function for the unit tests

All design decisions and the implementation were my own. AI was used to review plans
and concepts. I understand and can explain every part of this submission.
