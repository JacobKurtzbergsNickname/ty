from fasthtml.common import *
from fasthtml.core import Request, FT
from app.services.positive_quote import create_positive_quote
from app.validation.schemas import PositiveQuoteCreate

quote_app, rt = fast_app()


@rt("/", methods=["GET", "POST"])
async def create_positive_quote_view(req: Request) -> FT:
    if req.method == "POST":
        form = await req.form()
        text = str(form.get("text", "")).strip()
        author = str(form.get("author", ""))
        if text:
            create_positive_quote(
                PositiveQuoteCreate(
                    text=text,
                    author=author,
                    # date will default to today
                )
            )
            return Titled(H2("Positive quote added!"), A("Back to Home", href="/"))
        else:
            error = "Text is required."
    else:
        error = None
    return Titled(
        H2("Add Positive Quote"),
        Form(
            Label("Text", Textarea(name="text", required=True)),
            Label("Author", Input(name="author")),
            Button("Add", type="submit"),
            cls="form-section",
            method="post",
        ),
        P(error, cls="error") if error else None,
    )
