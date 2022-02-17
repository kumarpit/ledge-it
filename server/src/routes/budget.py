import pymongo
from fastapi import APIRouter, Body, HTTPException, status, Depends
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from typing import List

from ..middleware import get_current_active_user
from ..models.user import User
from ..models import Budget, UpdateBudgetModel, CategoryBudget
from ..database import budget_collection, user_collection, category_budget_collection
from datetime import datetime
router = APIRouter()


@router.get(
    "/budget/all",
    response_description="Get all stored budgets",
    response_model=List[Budget],
)
def get_all_budgets(current_user: User = Depends(get_current_active_user)):
    if (
        all_budgets := budget_collection.find({"email": current_user["email"]}).sort(
            [("year", pymongo.DESCENDING), ("month", pymongo.DESCENDING)]
        )
    ).count():
        return [jsonable_encoder(next(all_budgets)) for _ in range(all_budgets.count())]

    raise HTTPException(status_code=404, detail=f"No budgets have been found.")


@router.get(
    "/budget/",
    response_description="Get budget by month and year",
    response_model=Budget,
)
def get_budget(
    month: int, year: int, current_user: User = Depends(get_current_active_user)
):
    if (
        budget := budget_collection.find_one(
            {"month": month, "year": year, "email": current_user["email"]}
        )
    ) is not None:
        return budget

    raise HTTPException(
        status_code=404, detail=f"Budget with month: {month} and year: {year} not found"
    )


@router.post("/budget/", response_description="Add new budget", response_model=Budget)
def add_budget(
    budget: Budget = Body(...), current_user: User = Depends(get_current_active_user)
):
    if (
        budget_collection.find_one(
            {"month": budget.month, "year": budget.year, "email": current_user["email"]}
        )
        is not None
    ):
        raise HTTPException(
            status_code=404,
            detail=f"Budget with month: {budget.month} and year: {budget.year} already exists",
        )
    budget.email = current_user["email"]
    budget = jsonable_encoder(budget)
    new_budget = budget_collection.insert_one(budget)
    created_budget = budget_collection.find_one({"_id": new_budget.inserted_id})
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=created_budget)


@router.put("/budget/", response_description="Update a budget", response_model=Budget)
def update_budget(
    month: int,
    year: int,
    budget: UpdateBudgetModel = Body(...),
    current_user: User = Depends(get_current_active_user),
):
    budget = {k: v for k, v in budget.dict().items() if v is not None}
    budget["email"] = current_user["email"]
    budget = jsonable_encoder(budget)

    if len(budget) >= 1:
        update_result = budget_collection.update_one(
            {"month": month, "year": year, "email": current_user["email"]},
            {"$set": budget},
        )

        if update_result.modified_count == 1:
            if (
                updated_budget := budget_collection.find_one(
                    {"month": month, "year": year, "email": current_user["email"]}
                )
            ) is not None:
                return updated_budget

    if (
        existing_budget := budget_collection.find_one(
            {"month": month, "year": year, "email": current_user["email"]}
        )
    ) is not None:
        return existing_budget

    raise HTTPException(
        status_code=404, detail=f"Budget with month: {month} and year: {year} not found"
    )


@router.delete("/budget/", response_description="Delete a budget")
def delete_budget(
    month: int, year: int, current_user: User = Depends(get_current_active_user)
):
    delete_result = budget_collection.delete_one(
        {"month": month, "year": year, "email": current_user["email"]}
    )

    if delete_result.deleted_count == 1:
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=f"Budget with month: {month} and year: {year} was successfully deleted",
        )

    raise HTTPException(
        status_code=404, detail=f"Budget with month: {month} and year: {year} not found"
    )


def update_budget_spent(
    month: int,
    year: int,
    change: float,
    current_user: User = Depends(get_current_active_user),
):
    budget: Budget = budget_collection.find_one(
        {"month": month, "year": year, "email": current_user["email"]}
    )
    if budget is not None:
        budget["spent"] += change
        budget_collection.update_one(
            {"month": month, "year": year, "email": current_user["email"]},
            {"$set": budget},
        )
        return budget

    raise HTTPException(
        status_code=404,
        detail=f"Budget with month: {month} and year: {year}",
    )

@router.post("/generateBudget/", response_description="Generates new budget for next month.", response_model=str)
def generate_budget(
    keyword: str = Body(...)
):
    if (keyword != "verySecurePassword"):
        raise HTTPException(
        status_code=404,
        detail=f"Incorrect keyword!",
        )
    if (all_users := user_collection.find()).count():
        for user in all_users:
            currentTime = datetime.now()
            nextMonth = currentTime.month + 1
            nextYear = currentTime.year
            if currentTime.month == 13:
                nextMonth = 1
                nextYear = nextYear + 1

            # Create a new budget for next month, if not there
            if (budget_collection.find_one(
            {"month": nextMonth, "year": nextYear, "email": user["email"]})) is None:
                nextBudget = Budget(
                    email = user["email"], 
                    month = nextMonth, 
                    year = nextYear, 
                    value = 1000, 
                    spent = 0
                )
                if (
                budget := budget_collection.find_one(
                    {"month": currentTime.month, "year": currentTime.year, "email": user["email"]})
                ) is not None:
                    nextBudget.value = budget["value"]

                nextBudget = jsonable_encoder(nextBudget)
                new_budget = budget_collection.insert_one(nextBudget)

            # Create a category budget for next month, if not there
            all_categories = category_budget_collection.find({"month": currentTime.month, "year": currentTime.year, "email": user["email"]})
            for category in all_categories:
                if (catBudget := category_budget_collection.find_one({"month": nextMonth, "year": nextYear, "email": user["email"], "category": category["category"]})) is None:
                    nextCatBudget = CategoryBudget(
                            email = user["email"], 
                            month = nextMonth, 
                            year = nextYear, 
                            value = category["value"], 
                            spent = 0,
                            category = category["category"]
                        )
                    nextCatBudget = jsonable_encoder(nextCatBudget)
                    new_cat_budget = category_budget_collection.insert_one(nextCatBudget)

    return "Budgets successfully generated!"