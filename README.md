# 📦 PyObjectDB: Seamless Python Object Storage

Hi there! Welcome to **PyObjectDB**. This is a project I've been working on to solve a common headache in Python development: translating objects to relational databases. 

Instead of writing complex SQL queries or dealing with clunky Object-Relational Mappers (ORMs), **PyObjectDB** lets you store your Python objects *exactly as they are*. It’s a pure, ACID-compliant, object-oriented database designed to make your code feel incredibly clean and natural.

## 🚀 Why I Built This

I realized that we spend way too much time writing boilerplate code just to save data. With PyObjectDB, you can:
- **Skip the SQL**: You don't need to know another language just to save a Python class.
- **Forget the ORM**: There is no mapping layer. You just save the object, and it stays an object.
- **Keep it Pythonic**: The seam between your application logic and your database is practically invisible.

## 🧠 How It Works (Simplified Architecture)

Here is a simple diagram showing how your Python code interacts with the database. Notice how there is no translation layer—your objects go straight into storage!

```mermaid
flowchart TD
    %% Define styles for a friendly look
    classDef app fill:#4CAF50,stroke:#388E3C,stroke-width:2px,color:#fff,rx:10,ry:10
    classDef core fill:#2196F3,stroke:#1976D2,stroke-width:2px,color:#fff,rx:10,ry:10
    classDef storage fill:#FFC107,stroke:#FFA000,stroke-width:2px,color:#333,rx:10,ry:10

    App["💻 Your Python App\n(Creates standard objects)"]:::app
    Core["⚙️ PyObjectDB Core\n(Manages transactions)"]:::core
    
    App -->|Saves Objects directly| Core
    
    subgraph Storage Options
        File["📁 Local File\n(Great for testing)"]:::storage
        DB["🗄️ SQL Database\n(For production)"]:::storage
        Net["🌐 Network\n(For distributed apps)"]:::storage
    end
    
    Core -.->|Option A| File
    Core -.->|Option B| DB
    Core -.->|Option C| Net
```

## 🛠️ Getting Started

This database runs beautifully on Python 3.7+ and PyPy. Whether you are building a small personal project or a large distributed system, PyObjectDB adapts to your needs seamlessly.

---
*Feel free to explore the code, open issues, or submit pull requests!*
