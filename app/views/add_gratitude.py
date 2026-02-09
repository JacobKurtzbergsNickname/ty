from typing import cast
from fasthtml.common import *
from fasthtml.core import Request, FT
from app.services.gratitude import create_gratitude_item
from app.validation.schemas import GratitudeItemCreate

add_gratitude_app, rt = fast_app()


@rt("/", methods=["GET", "POST"])
async def create_gratitude_view(req: Request) -> FT:
    if req.method == "POST":
        form = await req.form()
        title = cast(str, form.get("title", "")).strip()
        description = cast(str, form.get("description", "")).strip()
        how_happy = cast(int, form.get("how_happy_am_i_about_this", 1))
        reused = cast(int, form.get("reused", 0))
        if title:
            create_gratitude_item(
                GratitudeItemCreate(
                    title=title,
                    description=description,
                    how_happy_am_i_about_this=how_happy,
                    reused=reused,
                    # date will default to today
                )
            )
            return Titled(H2("Gratitude item added!"), A("Back to Home", href="/"))
        else:
            error = "Title is required."
    else:
        error = None
    return Titled(
        "Add Gratitude Item",
        Form(
            Label("Title", Input(name="title", required=True)),
            Label("Description", Textarea(name="description")),
            Label(
                "Happiness (1-10)",
                Input(
                    type="number",
                    name="how_happy_am_i_about_this",
                    min=1,
                    max=10,
                    value="1",
                ),
            ),
            Label("Reused", Input(type="number", name="reused", min=0, value="0")),
            Button("Add", type="submit", method="post"),
            cls="form-section",
            method="post",
        ),
        P(error, cls="error") if error else None,
    )
