from typing import cast
from fasthtml.common import *
from fasthtml.core import Request, FT
from app.services import create_good_thing
from app.validation.schemas import GoodThingsThatHappenedToMeCreate

good_thing_app, rt = fast_app()


@rt("/", methods=["GET", "POST"])
async def create_good_thing_view(req: Request) -> FT:
    if req.method == "POST":
        form = await req.form()
        description = cast(str, form.get("description", "")).strip()
        impact = cast(str, form.get("impact", "1"))
        if description:
            create_good_thing(
                GoodThingsThatHappenedToMeCreate(
                    description=description,
                    impact=impact,
                    # date will default to today
                )
            )
            return Titled(H2("Good thing added!"), A("Back to Home", href="/"))
        else:
            error = "Description is required."
    else:
        error = None
    return Titled(
        "Add Good Thing That Happened To Me",
        Form(
            Label("Description", Textarea(name="description", required=True)),
            Label(
                "Impact (1-10)",
                Input(type="number", name="impact", min=1, max=10, value="1"),
            ),
            Button("Add", type="submit"),
            cls="form-section",
            method="post",
        ),
        P(error, cls="error") if error else None,
    )
