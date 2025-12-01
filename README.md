# 📦 go‑grpc‑micro

A micro‑service‑based e‑commerce skeleton written in Go.  
The repo exposes four domains – **Order**, **Catalog**, **Account**, and **GraphQL** – each running in its own Docker container and communicating via gRPC.  

---

## ✨ Description

This project demonstrates a simple, domain‑driven micro‑service architecture.  
Each service is a standalone container that can be started independently, yet they all share a common gRPC interface.

- **Order** – create orders and list orders per account.  
- **Catalog** – CRUD for products, paging, search, and bulk lookup.  
- **Account** – (not shown in the snippet) – user registration and authentication.  
- **GraphQL** – optional GraphQL layer (not part of the current release).  

---

## 🚀 Features

- **gRPC** servers & clients (auto‑generated with protobuf).  
- **KSUID** for stable, sortable IDs.  
- **Docker‑Compose** ready – each domain runs in its own container.  
- **Reflection** enabled on gRPC servers for easy debugging.  
- Basic repository abstractions for persistence (PostgreSQL for Orders, Elastic‑Search/SQL for Catalog).  

---

## 🛠️ Installation

```bash
# Clone the repo
git clone https://github.com/adityaadpandey/go-grpc-micro.git
cd go-grpc-micro

# Build all services
make build
```

> **NOTE**  
> The build script expects `protoc` to be installed.  
> Install it on Ubuntu:  
> ```bash
> sudo apt-get install -y protobuf-compiler
> ```

---

## 📦 Docker

```bash
# Build images
docker compose build

# Start services
docker compose up -d
```

> Ports mapping (default)  
> | Service | Port | Notes |
> |---------|------|-------|
> | Order   | 50051 | gRPC |
> | Catalog | 50052 | gRPC |
> | Account | 50053 | gRPC |
> | GraphQL | 50054 | (optional) |

Use `docker compose down` to stop.

---

## 📄 Usage

### 1️⃣ Order Service

```go
import (
    "context"
    "github.com/adityaadpandey/go-grpc-micro/order"
)

func createOrder() {
    client, _ := order.NewClient("localhost:50051")
    defer client.Close()

    products := []order.OrderedProduct{
        {ID: "p1", Name: "T‑Shirt", Price: 19.99, Quantity: 2},
    }

    order, _ := client.PostOrder(context.Background(), "acct123", products)
    fmt.Printf("Order %s created at %s, total: $%.2f\n",
        order.ID, order.CreatedAt, order.TotalPrice)
}
```

### 2️⃣ Catalog Service

```go
import (
    "context"
    "github.com/adityaadpandey/go-grpc-micro/catalog"
)

func addProduct() {
    client, _ := catalog.NewClient("localhost:50052")
    defer client.Close()

    prod, _ := client.PostProduct(context.Background(), "Coffee Mug", "Ceramic mug", 9.99)
    fmt.Printf("Created product %s (%s) – $%.2f\n", prod.ID, prod.Name, prod.Price)
}
```

---

## ⚙️ Configuration

All services read the following environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `GRPC_PORT` | TCP port for the gRPC server | `50051` for Order, `50052` for Catalog, etc. |
| `DB_URL` | Database connection string (PostgreSQL, Elastic‑Search) | – |
| `SERVICE_URL` | URL for a dependent service (e.g., `ACCOUNT_URL`) | – |

> Example `.env` file:
> ```dotenv
> GRPC_PORT=50051
> DB_URL=postgres://user:pass@localhost:5432/orders
> ```

---

## 🤝 Contributing

Feel free to submit issues or pull requests.  
Please follow the code style and keep changes focused on the existing features.

---

## 📜 License

This repository does not ship a license.  
Please contact the maintainer before using it for commercial projects.