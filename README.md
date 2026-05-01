# PyObjectDB (formerly ZODB)

![Latest release](https://img.shields.io/pypi/v/ZODB.svg) ![Supported Python versions](https://img.shields.io/pypi/pyversions/ZODB.svg) ![Build status](https://github.com/zopefoundation/ZODB/actions/workflows/tests.yml/badge.svg) ![Coverage status](https://coveralls.io/repos/github/zopefoundation/ZODB/badge.svg) ![Documentation status](https://readthedocs.org/projects/zodb-docs/badge/?version=latest)

**PyObjectDB** is an ACID-compliant, object-oriented database for Python that provides a high degree of transparency. It runs on Python 3.7 and above, as well as PyPy.

## Key Features

- **No separate language** for database operations.
- **Very little impact** on your code to make objects persistent.
- **No database mapper** that partially hides the database. Using an object-relational mapping is *not* like using an object-oriented database.
- **Almost no seam** between code and database.

## Architecture

PyObjectDB natively stores Python objects without requiring an ORM layer, ensuring seamless integration between your code's state and the database's persistence.

```mermaid
graph TD
    A[Python Application] -->|Native Python Objects| B(PyObjectDB Core)
    B -->|Transactions| C{Storage Layer}
    C -->|FileStorage| D[Local Filesystem]
    C -->|RelStorage| E[SQL Database]
    C -->|ZEO| F[Network Storage]
    
    style A fill:#4CAF50,stroke:#388E3C,stroke-width:2px,color:#fff
    style B fill:#2196F3,stroke:#1976D2,stroke-width:2px,color:#fff
    style C fill:#FFC107,stroke:#FFA000,stroke-width:2px,color:#fff
    style D fill:#9E9E9E,stroke:#757575,stroke-width:2px,color:#fff
    style E fill:#9E9E9E,stroke:#757575,stroke-width:2px,color:#fff
    style F fill:#9E9E9E,stroke:#757575,stroke-width:2px,color:#fff
```

## Documentation

To learn more, visit: https://zodb-docs.readthedocs.io

*(This repository is a renamed demonstration fork of the original ZODB project.)*
