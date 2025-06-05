"""
Widget API Router.

This module implements all CRUD endpoints for Widget resources following
REST conventions with proper HTTP status codes, error handling, and
OpenAPI documentation.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..exceptions import DatabaseException, WidgetNotFoundException
from ..logging_config import get_logger, log_business_event
from ..repositories.widget import WidgetRepository
from ..schemas.widget import (
    WidgetCreate,
    WidgetListResponse,
    WidgetResponse,
    WidgetUpdate,
)

router = APIRouter(prefix="/widgets", tags=["Widgets"])
logger = get_logger(__name__)


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=WidgetResponse,
    summary="Create a new widget",
    description=(
        "Create a new widget with the provided name and number of parts."
    ),
    responses={
        201: {
            "description": "Widget created successfully",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "name": "Sample Widget",
                        "number_of_parts": 10,
                        "created_at": "2024-01-15T10:30:00.000Z",
                        "updated_at": "2024-01-15T10:30:00.000Z",
                    }
                }
            },
        },
        400: {
            "description": "Invalid input data",
            "content": {
                "application/json": {
                    "example": {
                        "error": "VALIDATION_ERROR",
                        "message": "Validation failed",
                        "details": {"field_errors": {"name": "Field required"}},
                    }
                }
            },
        },
        500: {
            "description": "Internal server error",
            "content": {
                "application/json": {
                    "example": {
                        "error": "DATABASE_ERROR",
                        "message": "Database operation failed",
                        "details": {"operation": "create"},
                    }
                }
            },
        },
    },
)
async def create_widget(
    widget_data: WidgetCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> WidgetResponse:
    """Create a new widget."""
    logger.info(f"Creating widget: {widget_data.name}")
    
    widget_repo = WidgetRepository(db)
    widget = await widget_repo.create(widget_data)
    
    # Log business event
    log_business_event(
        event_type="widget_created",
        details={
            "widget_id": widget.id,
            "widget_name": widget.name,
            "number_of_parts": widget.number_of_parts,
        }
    )
    
    logger.info(f"Widget created successfully: ID {widget.id}")
    return WidgetResponse.model_validate(widget)


@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    response_model=WidgetListResponse,
    summary="Get all widgets with pagination",
    description=(
        "Retrieve a paginated list of all widgets with optional ordering."
    ),
    responses={
        200: {
            "description": "Widgets retrieved successfully",
            "content": {
                "application/json": {
                    "example": {
                        "widgets": [
                            {
                                "id": 1,
                                "name": "Sample Widget",
                                "number_of_parts": 10,
                                "created_at": "2024-01-15T10:30:00.000Z",
                                "updated_at": "2024-01-15T10:30:00.000Z",
                            }
                        ],
                        "total": 1,
                        "page": 1,
                        "size": 10,
                        "pages": 1,
                    }
                }
            },
        },
        500: {
            "description": "Internal server error",
            "content": {
                "application/json": {
                    "example": {"detail": "Database error occurred"}
                }
            },
        },
    },
)
async def get_widgets(
    db: Annotated[AsyncSession, Depends(get_db)],
    page: Annotated[
        int,
        Query(
            ge=1,
            description="Page number (1-based)",
            examples=[1],
        ),
    ] = 1,
    size: Annotated[
        int,
        Query(
            ge=1,
            le=100,
            description="Number of items per page (max 100)",
            examples=[10],
        ),
    ] = 10,
    order_by: Annotated[
        str,
        Query(
            description="Field to order by",
            examples=["id"],
        ),
    ] = "id",
    order_desc: Annotated[
        bool,
        Query(
            description="Order in descending order",
            examples=[False],
        ),
    ] = False,
) -> WidgetListResponse:
    """Get all widgets with pagination and ordering."""
    logger.debug(
        f"Retrieving widgets: page={page}, size={size}, "
        f"order_by={order_by}, order_desc={order_desc}"
    )
    
    widget_repo = WidgetRepository(db)
    result = await widget_repo.get_all(
        page=page,
        size=size,
        order_by=order_by,
        order_desc=order_desc,
    )

    widgets = [
        WidgetResponse.model_validate(widget) for widget in result.items
    ]

    logger.info(f"Retrieved {len(widgets)} widgets (page {page} of {result.pages})")
    
    return WidgetListResponse(
        widgets=widgets,
        total=result.total,
        page=result.page,
        size=result.size,
        pages=result.pages,
    )


@router.get(
    "/{widget_id}",
    status_code=status.HTTP_200_OK,
    response_model=WidgetResponse,
    summary="Get a widget by ID",
    description="Retrieve a specific widget by its unique identifier.",
    responses={
        200: {
            "description": "Widget retrieved successfully",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "name": "Sample Widget",
                        "number_of_parts": 10,
                        "created_at": "2024-01-15T10:30:00.000Z",
                        "updated_at": "2024-01-15T10:30:00.000Z",
                    }
                }
            },
        },
        404: {
            "description": "Widget not found",
            "content": {
                "application/json": {
                    "example": {"detail": "Widget with ID 123 not found"}
                }
            },
        },
        500: {
            "description": "Internal server error",
            "content": {
                "application/json": {
                    "example": {"detail": "Database error occurred"}
                }
            },
        },
    },
)
async def get_widget(
    widget_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> WidgetResponse:
    """Get a widget by ID."""
    logger.debug(f"Retrieving widget: ID {widget_id}")
    
    widget_repo = WidgetRepository(db)
    widget = await widget_repo.get_by_id(widget_id)
    
    logger.info(f"Widget retrieved successfully: ID {widget_id}")
    return WidgetResponse.model_validate(widget)


@router.put(
    "/{widget_id}",
    status_code=status.HTTP_200_OK,
    response_model=WidgetResponse,
    summary="Update a widget",
    description=(
        "Update an existing widget with new data. "
        "Only provided fields will be updated."
    ),
    responses={
        200: {
            "description": "Widget updated successfully",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "name": "Updated Widget",
                        "number_of_parts": 20,
                        "created_at": "2024-01-15T10:30:00.000Z",
                        "updated_at": "2024-01-15T11:45:00.000Z",
                    }
                }
            },
        },
        400: {
            "description": "Invalid input data",
            "content": {
                "application/json": {
                    "example": {"detail": "Validation error in request data"}
                }
            },
        },
        404: {
            "description": "Widget not found",
            "content": {
                "application/json": {
                    "example": {"detail": "Widget with ID 123 not found"}
                }
            },
        },
        500: {
            "description": "Internal server error",
            "content": {
                "application/json": {
                    "example": {"detail": "Database error occurred"}
                }
            },
        },
    },
)
async def update_widget(
    widget_id: int,
    widget_data: WidgetUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> WidgetResponse:
    """Update a widget."""
    logger.info(f"Updating widget: ID {widget_id}")
    
    widget_repo = WidgetRepository(db)
    widget = await widget_repo.update(widget_id, widget_data)
    
    # Log business event
    log_business_event(
        event_type="widget_updated",
        details={
            "widget_id": widget.id,
            "widget_name": widget.name,
            "number_of_parts": widget.number_of_parts,
            "updated_fields": widget_data.model_dump(exclude_unset=True),
        }
    )
    
    logger.info(f"Widget updated successfully: ID {widget_id}")
    return WidgetResponse.model_validate(widget)


@router.delete(
    "/{widget_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a widget",
    description="Delete an existing widget by its unique identifier.",
    responses={
        204: {
            "description": "Widget deleted successfully",
        },
        404: {
            "description": "Widget not found",
            "content": {
                "application/json": {
                    "example": {"detail": "Widget with ID 123 not found"}
                }
            },
        },
        500: {
            "description": "Internal server error",
            "content": {
                "application/json": {
                    "example": {"detail": "Database error occurred"}
                }
            },
        },
    },
)
async def delete_widget(
    widget_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    """Delete a widget."""
    logger.info(f"Deleting widget: ID {widget_id}")
    
    widget_repo = WidgetRepository(db)
    await widget_repo.delete(widget_id)
    
    # Log business event
    log_business_event(
        event_type="widget_deleted",
        details={"widget_id": widget_id}
    )
    
    logger.info(f"Widget deleted successfully: ID {widget_id}")
    # Return None for 204 No Content status
