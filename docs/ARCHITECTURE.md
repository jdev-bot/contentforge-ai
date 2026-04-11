# ContentForge AI Architecture Overview

## Core Components

- **API Gateway**: Entry point handling authentication, rate limiting, and routing
- **Content Service**: Core business logic for content generation and management
- **Storage Layer**: Data persistence for user content, templates, and metadata
- **Worker Pool**: Background job processing for async content generation tasks

## Data Flow

User requests flow through the API Gateway, which authenticates and routes to the Content Service. The Content Service validates inputs, stores metadata in the Storage Layer, and queues generation jobs to the Worker Pool. Completed results are persisted to storage and returned to the client via the gateway.
