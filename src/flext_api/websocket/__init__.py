"""WebSocket communication package for FLEXT API.

This package provides WebSocket functionality for real-time bidirectional communication
between the FLEXT API server and connected clients. It enables live updates and streaming
capabilities essential for monitoring pipeline executions and system events.

Key features:
            - Connection lifecycle management with automatic reconnection
- Message broadcasting to multiple connected clients
- Event-based communication patterns for system notifications
- Pipeline execution progress streaming
- Real-time log streaming from running jobs
- Heartbeat mechanism to detect disconnected clients
- Room-based communication for multi-tenant scenarios

The WebSocket implementation follows enterprise patterns with:
            - Proper error handling and graceful degradation
- Connection pooling and resource management
- Message validation and serialization
- Security through authentication tokens
- Rate limiting to prevent abuse
"""
