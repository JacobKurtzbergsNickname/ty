"""View to add a new affirmation."""

from fasthtml.common import *
from fasthtml.core import Request, FT
from app.services import create_affirmation
from app.validation.schemas import AffirmationCreate

affirmation_app, rt = fast_app()


@rt("/", methods=["GET", "POST"])
async def create_affirmation_view(req: Request) -> FT:
    if req.method == "POST":
        posted_form = await req.form()
        text = posted_form["text"]
        author = posted_form.get("author", "")
        if text:
            create_affirmation(
                AffirmationCreate(
                    text=text,
                    author=author,
                    # date will default to today
                )
            )
            return Titled(H2("Affirmation added!"), A("Back to Home", href="/"))
        else:
            error = "Text is required."
    else:
        error = None
    return Titled(
        "Add Affirmation",
        Form(
            Label("Text", Textarea(name="text", required=True)),
            Label("Author", Input(name="author")),
            Button("Add", type="submit"),
            cls="form-section",
            method="post",
        ),
        P(error, cls="error") if error else None,
    )
