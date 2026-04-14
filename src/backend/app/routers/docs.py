"""
API documentation endpoints for OpenAPI spec and ReDoc.
"""

from fastapi import APIRouter, Request
from fastapi.openapi.utils import get_openapi
from fastapi.responses import HTMLResponse, JSONResponse

from app.core.config import get_settings

router = APIRouter()
settings = get_settings()


@router.get("/docs/openapi.json")
async def get_openapi_json(request: Request):
    """Return auto-generated OpenAPI specification as JSON."""
    # Use request.app to avoid circular import with app.main
    app = request.app
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

    # Add additional info
    openapi_schema["info"]["x-logo"] = {"url": "https://contentforge.ai/logo.png"}
    openapi_schema["servers"] = [
        {"url": str(request.base_url), "description": "Current server"},
        {"url": "https://api.contentforge.ai", "description": "Production server"},
    ]

    return JSONResponse(content=openapi_schema)


@router.get("/docs/redoc", response_class=HTMLResponse)
async def get_redoc():
    """Return ReDoc HTML documentation."""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>ContentForge AI API Documentation</title>
        <meta charset="utf-8"/>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link rel="shortcut icon" href="https://contentforge.ai/favicon.ico">
        <link href="https://fonts.googleapis.com/css?family=Montserrat:300,400,700|Roboto:300,400,700" rel="stylesheet">
        <style>
            body {
                margin: 0;
                padding: 0;
            }
        </style>
    </head>
    <body>
        <redoc spec-url="/api/v1/docs/openapi.json"></redoc>
        <script src="https://cdn.redoc.ly/redoc/latest/bundles/redoc.standalone.js"> </script>
    </body>
    </html>
    """
    return html_content


@router.get("/docs/swagger", response_class=HTMLResponse)
async def get_swagger_ui():
    """Return Swagger UI HTML documentation (alternative to ReDoc)."""
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>ContentForge AI API - Swagger UI</title>
        <link rel="stylesheet" type="text/css" href="https://unpkg.com/swagger-ui-dist@5.9.0/swagger-ui.css" />
    </head>
    <body>
        <div id="swagger-ui"></div>
        <script src="https://unpkg.com/swagger-ui-dist@5.9.0/swagger-ui-bundle.js"></script>
        <script>
            window.onload = function() {
                window.ui = SwaggerUIBundle({
                    url: '/api/v1/docs/openapi.json',
                    dom_id: '#swagger-ui',
                    presets: [
                        SwaggerUIBundle.presets.apis,
                        SwaggerUIBundle.presets.standalone
                    ],
                    layout: "BaseLayout",
                    deepLinking: true,
                    showExtensions: true,
                    showCommonExtensions: true
                });
            };
        </script>
    </body>
    </html>
    """
    return html_content
