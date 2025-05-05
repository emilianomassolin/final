flowchart TB
    subgraph Clientes
        C1[Cliente 1]
        C2[Cliente 2]
        C3[Cliente 3]
    end

    C1 -->|Pedido| Server
    C2 -->|Pedido| Server
    C3 -->|Pedido| Server

    Server[Servidor Principal]
    Queue[Cola de Pedidos]
    Worker1[Worker 1]
    Worker2[Worker 2]
    Worker3[Worker 3]

    Server -->|Encola Pedido| Queue
    Queue --> Worker1
    Queue --> Worker2
    Queue --> Worker3

    subgraph Base de Datos
        DB[(SQLite)]
    end

    Worker1 -->|Guardar/Actualizar| DB
    Worker2 -->|Guardar/Actualizar| DB
    Worker3 -->|Guardar/Actualizar| DB
