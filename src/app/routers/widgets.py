"""
Widget API Router.

This module implements all CRUD endpoints for Widget resources following
REST conventions with proper HTTP status codes, error handling, and
OpenAPI documentation.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..repositories.widget import (
    WidgetNotFoundError,
    WidgetRepository,
    WidgetRepositoryError,
)
from ..schemas.widget import (
    WidgetCreate,
    WidgetListResponse,
    WidgetResponse,
    WidgetUpdate,
)

router = APIRouter(prefix="/widgets", tags=["Widgets"])


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
                    "example": {"detail": "Validation error in request data"}
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
async def create_widget(
    widget_data: WidgetCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> WidgetResponse:
    """Create a new widget."""
    try:
        widget_repo = WidgetRepository(db)
        widget = await widget_repo.create(widget_data)
        return WidgetResponse.model_validate(widget)
    except WidgetRepositoryError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}",
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}",
        ) from e


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
    try:
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

        return WidgetListResponse(
            widgets=widgets,
            total=result.total,
            page=result.page,
            size=result.size,
            pages=result.pages,
        )
    except WidgetRepositoryError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}",
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}",
        ) from e


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
    try:
        widget_repo = WidgetRepository(db)
        widget = await widget_repo.get_by_id(widget_id)
        return WidgetResponse.model_validate(widget)
    except WidgetNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e
    except WidgetRepositoryError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}",
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}",
        ) from e


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
    try:
        widget_repo = WidgetRepository(db)
        widget = await widget_repo.update(widget_id, widget_data)
        return WidgetResponse.model_validate(widget)
    except WidgetNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e
    except WidgetRepositoryError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}",
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}",
        ) from e


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
    try:
        widget_repo = WidgetRepository(db)
        await widget_repo.delete(widget_id)
        # Return None for 204 No Content status
    except WidgetNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e
    except WidgetRepositoryError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}",
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}",
        ) from e
